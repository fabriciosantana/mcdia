"""Gera embeddings OpenAI retomáveis para os discursos e perguntas de avaliação."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

import numpy as np
import pandas as pd
import tiktoken
from dotenv import load_dotenv
from openai import OpenAI


RAIZ = Path(__file__).resolve().parents[1]
MODELO = "text-embedding-3-large"
DIMENSOES = 512
MAX_TOKENS_TEXTO = 8_000
MAX_TOKENS_LOTE = 200_000
MAX_ITENS_LOTE = 512


@dataclass(frozen=True)
class Item:
    identificador: str
    texto: str
    tokens: int


def sha256(caminho: Path) -> str:
    resumo = hashlib.sha256()
    with caminho.open("rb") as entrada:
        for bloco in iter(lambda: entrada.read(1024 * 1024), b""):
            resumo.update(bloco)
    return resumo.hexdigest()


def preparar_texto(texto: str, codificador: tiktoken.Encoding) -> tuple[str, int, bool]:
    tokens = codificador.encode(texto, disallowed_special=())
    truncado = len(tokens) > MAX_TOKENS_TEXTO
    if truncado:
        tokens = tokens[:MAX_TOKENS_TEXTO]
        texto = codificador.decode(tokens)
    return texto, len(tokens), truncado


def criar_lotes(itens: list[Item]) -> Iterator[list[Item]]:
    lote: list[Item] = []
    total_tokens = 0
    for item in itens:
        excede = lote and (
            len(lote) >= MAX_ITENS_LOTE
            or total_tokens + item.tokens > MAX_TOKENS_LOTE
        )
        if excede:
            yield lote
            lote, total_tokens = [], 0
        lote.append(item)
        total_tokens += item.tokens
    if lote:
        yield lote


def validar_checkpoint(caminho: Path, ids_esperados: list[str]) -> bool:
    if not caminho.exists():
        return False
    try:
        with np.load(caminho, allow_pickle=False) as dados:
            ids = dados["ids"].astype(str).tolist()
            vetores = dados["embeddings"]
        return ids == ids_esperados and vetores.shape == (len(ids), DIMENSOES)
    except (OSError, ValueError, KeyError):
        return False


def processar_lotes(
    cliente: OpenAI,
    itens: list[Item],
    diretorio: Path,
    prefixo: str,
) -> list[Path]:
    diretorio.mkdir(parents=True, exist_ok=True)
    caminhos: list[Path] = []
    for numero, lote in enumerate(criar_lotes(itens)):
        caminho = diretorio / f"{prefixo}_{numero:04d}.npz"
        ids = [item.identificador for item in lote]
        caminhos.append(caminho)
        if validar_checkpoint(caminho, ids):
            print(f"Reutilizando {caminho.name}: {len(lote)} itens")
            continue
        resposta = cliente.embeddings.create(
            model=MODELO,
            input=[item.texto for item in lote],
            dimensions=DIMENSOES,
            encoding_format="float",
        )
        vetores = np.asarray([item.embedding for item in resposta.data], dtype=np.float32)
        temporario = caminho.with_suffix(".tmp.npz")
        np.savez_compressed(temporario, ids=np.asarray(ids), embeddings=vetores)
        temporario.replace(caminho)
        print(f"Criado {caminho.name}: {len(lote)} itens, {sum(x.tokens for x in lote):,} tokens")
    return caminhos


def consolidar(caminhos: list[Path], destino: Path) -> None:
    todos_ids: list[np.ndarray] = []
    todos_vetores: list[np.ndarray] = []
    for caminho in caminhos:
        with np.load(caminho, allow_pickle=False) as dados:
            todos_ids.append(dados["ids"])
            todos_vetores.append(dados["embeddings"])
    np.savez_compressed(
        destino,
        ids=np.concatenate(todos_ids),
        embeddings=np.vstack(todos_vetores).astype(np.float32),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--planejar", action="store_true", help="valida e estima sem chamar a API")
    args = parser.parse_args()

    load_dotenv(RAIZ / ".env")
    parquets = sorted((RAIZ / "dados").glob("*.parquet"))
    if len(parquets) != 1:
        raise RuntimeError(f"Esperado exatamente um parquet em dados/: {parquets}")
    perguntas_path = RAIZ / "avaliacao/perguntas_referencia.json"
    df = pd.read_parquet(parquets[0])
    texto = df["TextoDiscursoIntegral"].fillna("").astype(str).str.strip()
    corpus = df.loc[texto.ne(""), ["CodigoPronunciamento", "TextoDiscursoIntegral"]].copy()
    perguntas = json.loads(perguntas_path.read_text(encoding="utf-8"))

    codificador = tiktoken.get_encoding("cl100k_base")
    itens_documentos: list[Item] = []
    truncados = 0
    for linha in corpus.itertuples(index=False):
        texto_pronto, quantidade, foi_truncado = preparar_texto(
            str(linha.TextoDiscursoIntegral), codificador
        )
        truncados += int(foi_truncado)
        itens_documentos.append(Item(str(linha.CodigoPronunciamento), texto_pronto, quantidade))

    itens_perguntas: list[Item] = []
    for pergunta in perguntas:
        texto_pronto, quantidade, _ = preparar_texto(pergunta["pergunta"], codificador)
        itens_perguntas.append(Item(pergunta["id"], texto_pronto, quantidade))

    total_tokens = sum(item.tokens for item in itens_documentos + itens_perguntas)
    lotes_documentos = list(criar_lotes(itens_documentos))
    plano = {
        "modelo": MODELO,
        "dimensoes": DIMENSOES,
        "documentos": len(itens_documentos),
        "perguntas": len(itens_perguntas),
        "documentos_truncados": truncados,
        "max_tokens_texto": MAX_TOKENS_TEXTO,
        "tokens_estimados": total_tokens,
        "lotes_documentos": len(lotes_documentos),
        "parquet_sha256": sha256(parquets[0]),
    }
    print(json.dumps(plano, ensure_ascii=False, indent=2))
    if args.planejar:
        return
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("Preencha OPENAI_API_KEY no arquivo .env antes da execução.")

    cliente = OpenAI(max_retries=5, timeout=120.0)
    cache = RAIZ / "cache_embeddings" / "text_embedding_3_large_512"
    caminhos_documentos = processar_lotes(cliente, itens_documentos, cache / "lotes", "documentos")
    caminhos_perguntas = processar_lotes(cliente, itens_perguntas, cache / "lotes", "perguntas")
    consolidar(caminhos_documentos, cache / "documentos_openai.npz")
    consolidar(caminhos_perguntas, cache / "perguntas_openai.npz")

    plano.update({
        "gerado_em_utc": datetime.now(timezone.utc).isoformat(),
        "arquivo_documentos": "documentos_openai.npz",
        "arquivo_perguntas": "perguntas_openai.npz",
    })
    (cache / "manifesto.json").write_text(
        json.dumps(plano, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("Embeddings consolidados em:", cache)


if __name__ == "__main__":
    main()

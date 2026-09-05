"""Compara recuperação lexical, vetorial OpenAI e híbrida por RRF."""

from __future__ import annotations

import json
import re
from copy import copy
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


RAIZ = Path(__file__).resolve().parents[1]
RRF_K = 60
TOP_K_POOL = 10


def normalizar(vetores: np.ndarray) -> np.ndarray:
    normas = np.linalg.norm(vetores, axis=1, keepdims=True)
    return vetores / np.maximum(normas, 1e-12)


def ranks(escores: np.ndarray) -> np.ndarray:
    ordem = np.argsort(-escores, axis=1, kind="stable")
    resultado = np.empty_like(ordem)
    linhas = np.arange(escores.shape[0])[:, None]
    resultado[linhas, ordem] = np.arange(1, escores.shape[1] + 1)
    return resultado


def avaliar(metodo: str, escores: np.ndarray, ids: list[str], perguntas: list[dict]) -> list[dict]:
    linhas: list[dict] = []
    for indice, pergunta in enumerate(perguntas):
        ordem = np.argsort(-escores[indice], kind="stable")
        ids_ordenados = [ids[posicao] for posicao in ordem]
        melhores = [ids_ordenados.index(item) + 1 for item in pergunta["documentos_relevantes"]]
        melhor_rank = min(melhores)
        linhas.append({
            "metodo": metodo, "id": pergunta["id"], "tema": pergunta["tema"],
            "melhor_rank": melhor_rank, "hit_1": int(melhor_rank <= 1),
            "hit_5": int(melhor_rank <= 5), "hit_10": int(melhor_rank <= 10),
            "reciprocal_rank": 1 / melhor_rank, "primeiro_resultado": ids_ordenados[0],
        })
    return linhas


def trecho_informativo(texto: str, pergunta: str, limite: int = 1200) -> str:
    """Seleciona um trecho próximo ao primeiro termo informativo da pergunta."""
    texto_limpo = re.sub(r"\s+", " ", str(texto)).strip()
    termos = [
        termo for termo in re.findall(r"[\wÀ-ÿ-]{5,}", pergunta.lower())
        if termo not in {"qual", "discurso", "pronunciamento", "sobre", "como", "para"}
    ]
    posicoes = [texto_limpo.lower().find(termo) for termo in termos]
    posicoes = [posicao for posicao in posicoes if posicao >= 0]
    centro = min(posicoes) if posicoes else 0
    inicio = max(0, centro - 250)
    fim = min(len(texto_limpo), inicio + limite)
    return f"{'…' if inicio else ''}{texto_limpo[inicio:fim]}{'…' if fim < len(texto_limpo) else ''}"


def gerar_pool(
    perguntas: list[dict],
    corpus: pd.DataFrame,
    matrizes: dict[str, np.ndarray],
    resultados: Path,
) -> int:
    """Exporta planilha cega e chave separada com os rankings dos métodos."""
    ids = corpus["CodigoPronunciamento"].astype(str).tolist()
    rankings = {metodo: ranks(escores) for metodo, escores in matrizes.items()}
    linhas_revisao: list[dict] = []
    linhas_chave: list[dict] = []
    for indice_pergunta, pergunta in enumerate(perguntas):
        candidatos: set[int] = set()
        for escores in matrizes.values():
            candidatos.update(np.argsort(-escores[indice_pergunta], kind="stable")[:TOP_K_POOL])
        for indice_documento in sorted(candidatos, key=lambda indice: ids[indice]):
            linha = corpus.iloc[indice_documento]
            item_id = f"{pergunta['id']}-{ids[indice_documento]}"
            linhas_revisao.append({
                "item_id": item_id,
                "pergunta_id": pergunta["id"],
                "tema": pergunta["tema"],
                "pergunta": pergunta["pergunta"],
                "codigo_pronunciamento": ids[indice_documento],
                "autor": linha.get("NomeAutor"),
                "data": linha.get("Data"),
                "partido": linha.get("Partido"),
                "uf": linha.get("UF"),
                "resumo_oficial": linha.get("Resumo"),
                "trecho_texto_integral": trecho_informativo(
                    linha.get("TextoDiscursoIntegral", ""), pergunta["pergunta"]
                ),
                "url_texto_integral": linha.get("TextoIntegral"),
            })
            chave = {
                "item_id": item_id,
                "documento_originalmente_rotulado": int(
                    ids[indice_documento] in pergunta["documentos_relevantes"]
                ),
            }
            for metodo, matriz_ranks in rankings.items():
                chave[f"rank_{metodo}"] = int(matriz_ranks[indice_pergunta, indice_documento])
            linhas_chave.append(chave)

    revisao = pd.DataFrame(linhas_revisao).sort_values(["pergunta_id", "item_id"], kind="stable")
    chave = pd.DataFrame(linhas_chave).sort_values("item_id", kind="stable")
    revisao.to_csv(resultados / "pool_avaliacao.csv", index=False)
    chave.to_csv(resultados / "pool_chave_metodos.csv", index=False)
    with pd.ExcelWriter(resultados / "pool_avaliacao.xlsx", engine="openpyxl") as escritor:
        revisao.to_excel(escritor, sheet_name="Pool", index=False)
        planilha = escritor.book["Pool"]
        planilha.freeze_panes = "A2"
        planilha.auto_filter.ref = planilha.dimensions
        larguras = {
            "A": 20, "B": 12, "C": 28, "D": 65, "E": 22, "F": 25,
            "G": 13, "H": 12, "I": 8, "J": 70, "K": 90, "L": 45,
            "M": 24, "N": 45,
        }
        for coluna, largura in larguras.items():
            planilha.column_dimensions[coluna].width = largura
        for linha in planilha.iter_rows(min_row=2):
            for celula in linha:
                alinhamento = copy(celula.alignment)
                alinhamento.vertical = "top"
                alinhamento.wrap_text = True
                celula.alignment = alinhamento
    return len(revisao)


def main() -> None:
    cache = RAIZ / "cache_embeddings" / "text_embedding_3_large_512"
    documentos_path = cache / "documentos_openai.npz"
    perguntas_path = cache / "perguntas_openai.npz"
    if not documentos_path.exists() or not perguntas_path.exists():
        raise RuntimeError("Gere primeiro os embeddings com scripts/gerar_embeddings_openai.py")

    parquets = sorted((RAIZ / "dados").glob("*.parquet"))
    if len(parquets) != 1:
        raise RuntimeError(f"Esperado exatamente um parquet: {parquets}")
    df = pd.read_parquet(parquets[0])
    texto = df["TextoDiscursoIntegral"].fillna("").astype(str).str.strip()
    corpus = df.loc[texto.ne("")].reset_index(drop=True)
    perguntas = json.loads((RAIZ / "avaliacao/perguntas_referencia.json").read_text(encoding="utf-8"))

    with np.load(documentos_path, allow_pickle=False) as dados:
        ids_documentos = dados["ids"].astype(str).tolist()
        emb_documentos = normalizar(dados["embeddings"].astype(np.float32))
    with np.load(perguntas_path, allow_pickle=False) as dados:
        ids_perguntas = dados["ids"].astype(str).tolist()
        emb_perguntas = normalizar(dados["embeddings"].astype(np.float32))

    ids_corpus = corpus["CodigoPronunciamento"].astype(str).tolist()
    if ids_documentos != ids_corpus:
        raise ValueError("A ordem dos embeddings não corresponde à ordem atual do corpus.")
    if ids_perguntas != [item["id"] for item in perguntas]:
        raise ValueError("A ordem dos embeddings não corresponde às perguntas atuais.")

    vetorizador = TfidfVectorizer(
        lowercase=True, strip_accents="unicode", ngram_range=(1, 2), min_df=2,
        max_df=.95, max_features=80_000, sublinear_tf=True,
    )
    matriz_documentos = vetorizador.fit_transform(corpus["TextoDiscursoIntegral"].astype(str))
    matriz_perguntas = vetorizador.transform([item["pergunta"] for item in perguntas])
    escores_lexicais = cosine_similarity(matriz_perguntas, matriz_documentos)
    escores_vetoriais = emb_perguntas @ emb_documentos.T
    ranks_lexicais, ranks_vetoriais = ranks(escores_lexicais), ranks(escores_vetoriais)
    escores_hibridos = 1 / (RRF_K + ranks_lexicais) + 1 / (RRF_K + ranks_vetoriais)

    matrizes = {
        "TF-IDF": escores_lexicais,
        "OpenAI": escores_vetoriais,
        "Híbrido RRF": escores_hibridos,
    }
    linhas = []
    for metodo, matriz in matrizes.items():
        linhas.extend(avaliar(metodo, matriz, ids_documentos, perguntas))
    detalhado = pd.DataFrame(linhas)
    resumo = detalhado.groupby("metodo", sort=False).agg(
        consultas=("id", "size"), hit_1=("hit_1", "mean"), hit_5=("hit_5", "mean"),
        hit_10=("hit_10", "mean"), mrr=("reciprocal_rank", "mean"),
        mediana_rank=("melhor_rank", "median"),
    ).reset_index()
    resultados = RAIZ / "resultados"
    resultados.mkdir(exist_ok=True)
    detalhado.to_csv(resultados / "avaliacao_comparativa.csv", index=False)
    resumo.to_csv(resultados / "metricas_comparativas.csv", index=False)
    resumo.to_latex(resultados / "metricas_comparativas.tex", index=False,
                    float_format="%.3f", caption="Comparação dos métodos de recuperação.",
                    label="tab:recuperacao")
    print(resumo.to_string(index=False))
    quantidade_pool = gerar_pool(perguntas, corpus, matrizes, resultados)
    print(f"Pool cego criado com {quantidade_pool} itens em pool_avaliacao.xlsx")


if __name__ == "__main__":
    main()

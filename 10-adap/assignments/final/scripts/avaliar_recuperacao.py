"""Compara recuperação lexical, vetorial OpenAI e híbrida por RRF."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


RAIZ = Path(__file__).resolve().parents[1]
RRF_K = 60


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

    linhas = []
    for metodo, matriz in (("TF-IDF", escores_lexicais), ("OpenAI", escores_vetoriais), ("Híbrido RRF", escores_hibridos)):
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


if __name__ == "__main__":
    main()

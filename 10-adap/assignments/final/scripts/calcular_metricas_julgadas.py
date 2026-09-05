"""Calcula métricas de recuperação com os julgamentos finais do LLM."""

from __future__ import annotations

import math
from pathlib import Path

import pandas as pd


RAIZ = Path(__file__).resolve().parents[1]
METODOS = ("TF-IDF", "OpenAI", "Híbrido RRF")


def dcg(relevancias: list[int]) -> float:
    return sum((2**rel - 1) / math.log2(posicao + 2) for posicao, rel in enumerate(relevancias))


def main() -> None:
    resultados = RAIZ / "resultados"
    revisao = pd.read_csv(resultados / "pool_julgado_llm.csv")
    valores = pd.to_numeric(revisao["relevancia_final"], errors="coerce")
    chave = pd.read_csv(resultados / "pool_chave_metodos.csv")
    invalidos = revisao.loc[~valores.isin([0, 1, 2]), "item_id"].tolist()
    if invalidos:
        raise ValueError(
            f"Há {len(invalidos)} julgamentos LLM vazios ou inválidos."
        )
    revisao = revisao.assign(relevancia=valores.astype(int)).merge(
        chave, on="item_id", how="left", validate="one_to_one"
    )

    linhas = []
    for metodo in METODOS:
        coluna_rank = f"rank_{metodo}"
        for pergunta_id, grupo in revisao.groupby("pergunta_id", sort=True):
            ordenado = grupo.sort_values(coluna_rank)
            top10 = ordenado.loc[ordenado[coluna_rank] <= 10]
            if len(top10) != 10:
                raise ValueError(f"Top 10 incompleto para {metodo}/{pergunta_id}")
            binaria = (top10["relevancia"] >= 1).astype(int)
            ranks_relevantes = top10.loc[binaria.eq(1), coluna_rank]
            total_relevantes_pool = int((grupo["relevancia"] >= 1).sum())
            rel_ordenada = top10["relevancia"].astype(int).tolist()
            ideal = sorted(grupo["relevancia"].astype(int).tolist(), reverse=True)[:10]
            idcg = dcg(ideal)
            linhas.append({
                "metodo": metodo,
                "pergunta_id": pergunta_id,
                "precision_5": float(binaria.iloc[:5].mean()),
                "precision_10": float(binaria.mean()),
                "recall_pool_10": (
                    float(binaria.sum() / total_relevantes_pool) if total_relevantes_pool else 0.0
                ),
                "mrr_pool": float(1 / ranks_relevantes.min()) if len(ranks_relevantes) else 0.0,
                "ndcg_10": float(dcg(rel_ordenada) / idcg) if idcg else 0.0,
            })
    detalhado = pd.DataFrame(linhas)
    resumo = detalhado.groupby("metodo", sort=False).agg(
        precision_5=("precision_5", "mean"),
        precision_10=("precision_10", "mean"),
        recall_pool_10=("recall_pool_10", "mean"),
        mrr_pool=("mrr_pool", "mean"),
        ndcg_10=("ndcg_10", "mean"),
    ).reset_index()
    detalhado.to_csv(resultados / "metricas_julgadas_llm_por_pergunta.csv", index=False)
    resumo.to_csv(resultados / "metricas_julgadas_llm_resumo.csv", index=False)
    resumo.to_latex(
        resultados / "metricas_julgadas_llm_resumo.tex", index=False,
        float_format="%.3f", caption="Desempenho no pool com julgamento por LLM.",
        label="tab:metricas-julgadas",
    )
    print(resumo.to_string(index=False))


if __name__ == "__main__":
    main()

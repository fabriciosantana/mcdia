"""Confere se os principais resultados reproduzidos aparecem no artigo."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


RAIZ = Path(__file__).resolve().parents[1]


def exigir(texto: str, trecho: str, origem: str) -> None:
    if trecho not in texto:
        raise AssertionError(f"Valor de {origem} ausente do artigo: {trecho!r}")


def main() -> None:
    artigo = (RAIZ / "main.tex").read_text(encoding="utf-8")
    resultados = RAIZ / "resultados"

    caracterizacao = pd.read_csv(
        resultados / "caracterizacao_corpus.csv", index_col=0
    )["valor"]
    qualidade = pd.read_csv(resultados / "resumo_qualidade.csv").set_index("indicador")["valor"]
    comparativas = pd.read_csv(resultados / "metricas_comparativas.csv").set_index("metodo")
    julgadas = pd.read_csv(resultados / "metricas_julgadas_llm_resumo.csv").set_index("metodo")
    juiz = json.loads((resultados / "resumo_julgamento_llm.json").read_text(encoding="utf-8"))

    verificacoes = {
        "registros": f"{int(caracterizacao['pronunciamentos']):,}".replace(",", "."),
        "textos disponíveis": f"{int(caracterizacao['textos_disponiveis']):,}".replace(",", "."),
        "cobertura textual": f"{float(caracterizacao['cobertura_textual_pct']):.2f}".replace(".", ",") + r"\%",
        "partido ausente": f"{int(qualidade['Partido ausente']):,}".replace(",", "."),
        "Hit@1 TF--IDF": f"Hit@1 de {comparativas.loc['TF-IDF', 'hit_1']:.0%}".replace("%", r"\%"),
        "MRR TF--IDF": f"{comparativas.loc['TF-IDF', 'mrr']:.3f}".replace(".", ","),
        "itens julgados": str(int(juiz["itens"])),
        "concordância": f"{juiz['concordancia_exata_passagens']:.1%}".replace(".", ",").replace("%", r"\%"),
        "kappa": f"{juiz['kappa_ponderado_quadratico']:.3f}".replace(".", ","),
        "adjudicações": str(int(juiz["adjudicacoes"])),
        "Precision@5 híbrido": f"{julgadas.loc['Híbrido RRF', 'precision_5']:.2f}".replace(".", ","),
        "nDCG@10 híbrido": f"{julgadas.loc['Híbrido RRF', 'ndcg_10']:.3f}".replace(".", ","),
    }
    for origem, trecho in verificacoes.items():
        exigir(artigo, trecho, origem)

    print(f"Consistência confirmada para {len(verificacoes)} indicadores do artigo.")


if __name__ == "__main__":
    main()

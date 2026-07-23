"""Prepara a base analítica municipal usada no notebook.

Entradas brutas:
  - série histórica do Programa Mais Médicos (Ministério da Saúde);
  - internações classificadas como ICSAP (SES-GO/SIH-SUS);
  - estimativas populacionais municipais (SIDRA/IBGE).

A saída é pequena e fica versionada para que o notebook execute sem rede.
"""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd


BASE = Path(__file__).resolve().parent
RAW = BASE / "data" / "raw"
OUT = BASE / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)


def ler_pmm() -> pd.DataFrame:
    arquivo = RAW / "ppf_mais_medicos_serie_historica.csv.zip"
    with zipfile.ZipFile(arquivo) as zf:
        nome = zf.namelist()[0]
        pmm = pd.read_csv(
            zf.open(nome),
            sep=";",
            encoding="latin1",
            dtype={"ibge": "string"},
            low_memory=False,
        )
    pmm["data"] = pd.to_datetime(pmm["dt_referencia"], dayfirst=True)
    pmm["cod_mun"] = pmm["ibge"].str.zfill(6)
    inicial = pmm.loc[
        pmm["uf"].eq("GO")
        & pmm["cod_mun"].str.match(r"^52\d{4}$", na=False)
        & pmm["data"].eq(pd.Timestamp("2013-11-29"))
    ].copy()
    if inicial["cod_mun"].duplicated().any():
        raise ValueError("Há municípios duplicados na fotografia inicial do PMM.")
    return inicial[["cod_mun", "total_prof_ativos"]].rename(
        columns={"total_prof_ativos": "medicos_pmm_inicial"}
    )


def agregar_internacoes() -> pd.DataFrame:
    arquivo = RAW / "internacoes_icsap_go.csv"
    usar = [
        "mun_res_cod_ibge",
        "municipio_residencia",
        "regiao_saude_residencia",
        "ano_mes_internacao",
        "tipo",
        "Quantidade_internacao",
    ]
    partes: list[pd.DataFrame] = []
    for bloco in pd.read_csv(
        arquivo,
        sep=";",
        encoding="utf-8",
        usecols=usar,
        dtype="string",
        chunksize=250_000,
    ):
        bloco["ano"] = pd.to_numeric(
            bloco["ano_mes_internacao"].str[:4], errors="coerce"
        )
        bloco["mes"] = pd.to_numeric(
            bloco["ano_mes_internacao"].str[4:6], errors="coerce"
        )
        bloco = bloco.loc[bloco["ano"].isin([2013, 2014, 2015])]
        bloco["internacoes"] = pd.to_numeric(
            bloco["Quantidade_internacao"], errors="coerce"
        ).fillna(0)
        partes.append(
            bloco.groupby(
                [
                    "mun_res_cod_ibge",
                    "municipio_residencia",
                    "regiao_saude_residencia",
                    "ano",
                    "mes",
                    "tipo",
                ],
                as_index=False,
                dropna=False,
            )["internacoes"].sum()
        )
    mensal = pd.concat(partes, ignore_index=True)
    mensal = (
        mensal.groupby(
            [
                "mun_res_cod_ibge",
                "municipio_residencia",
                "regiao_saude_residencia",
                "ano",
                "mes",
                "tipo",
            ],
            as_index=False,
        )["internacoes"]
        .sum()
        .pivot_table(
            index=[
                "mun_res_cod_ibge",
                "municipio_residencia",
                "regiao_saude_residencia",
                "ano",
                "mes",
            ],
            columns="tipo",
            values="internacoes",
            fill_value=0,
        )
        .reset_index()
        .rename_axis(columns=None)
        .rename(columns={"Numerador": "icsap", "Denominador": "outras_clinicas"})
    )
    for coluna in ["icsap", "outras_clinicas"]:
        if coluna not in mensal:
            mensal[coluna] = 0
    mensal["cod_mun"] = mensal["mun_res_cod_ibge"].str[:6]
    return mensal


def ler_populacao() -> pd.DataFrame:
    with (RAW / "populacao_go_2013_2015.json").open(encoding="utf-8") as f:
        registros = json.load(f)[1:]
    pop = pd.DataFrame(registros)
    return pd.DataFrame(
        {
            "cod_mun": pop["D1C"].str[:6],
            "ano": pd.to_numeric(pop["D3C"]),
            "populacao": pd.to_numeric(pop["V"], errors="coerce"),
            "municipio_ibge": pop["D1N"],
        }
    )


def construir_base() -> pd.DataFrame:
    pmm = ler_pmm()
    mensal = agregar_internacoes()
    pop = ler_populacao()

    # Linha de base: jan-out/2013, antes da fotografia inicial de 29/11/2013.
    pre = mensal.loc[(mensal["ano"] == 2013) & mensal["mes"].between(1, 10)]
    pre = pre.groupby(
        ["cod_mun", "municipio_residencia", "regiao_saude_residencia"],
        as_index=False,
    )[["icsap", "outras_clinicas"]].sum()
    pre = pre.merge(pop.loc[pop["ano"].eq(2013), ["cod_mun", "populacao"]])
    # Anualização por 12/10 torna a escala comparável à média anual pós.
    pre["taxa_icsap_pre"] = pre["icsap"] * (12 / 10) / pre["populacao"] * 10_000
    pre["taxa_clinicas_pre"] = (
        (pre["icsap"] + pre["outras_clinicas"])
        * (12 / 10)
        / pre["populacao"]
        * 10_000
    )

    pos = mensal.loc[mensal["ano"].isin([2014, 2015])]
    pos = pos.groupby(["cod_mun", "ano"], as_index=False)[
        ["icsap", "outras_clinicas"]
    ].sum()
    pos = pos.merge(pop[["cod_mun", "ano", "populacao"]])
    pos["taxa_icsap"] = pos["icsap"] / pos["populacao"] * 10_000
    pos = pos.groupby("cod_mun", as_index=False).agg(
        taxa_icsap_pos=("taxa_icsap", "mean"),
        populacao_2014=("populacao", "first"),
    )

    base = pre.merge(pos, on="cod_mun", how="inner").merge(
        pmm, on="cod_mun", how="left"
    )
    base["medicos_pmm_inicial"] = base["medicos_pmm_inicial"].fillna(0)
    base["tratado"] = (base["medicos_pmm_inicial"] > 0).astype(int)
    base["log_populacao"] = np.log(base["populacao_2014"])
    base["mudanca_taxa_icsap"] = (
        base["taxa_icsap_pos"] - base["taxa_icsap_pre"]
    )

    colunas = [
        "cod_mun",
        "municipio_residencia",
        "regiao_saude_residencia",
        "tratado",
        "medicos_pmm_inicial",
        "populacao_2014",
        "log_populacao",
        "taxa_icsap_pre",
        "taxa_clinicas_pre",
        "taxa_icsap_pos",
        "mudanca_taxa_icsap",
    ]
    base = base[colunas].sort_values("cod_mun").reset_index(drop=True)
    if len(base) != 246:
        raise ValueError(f"Esperados 246 municípios de Goiás; obtidos {len(base)}.")
    return base


if __name__ == "__main__":
    analitica = construir_base()
    destino = OUT / "mais_medicos_icsap_go.csv"
    analitica.to_csv(destino, index=False)
    print(f"{len(analitica)} municípios salvos em {destino}")
    print(analitica["tratado"].value_counts().sort_index())

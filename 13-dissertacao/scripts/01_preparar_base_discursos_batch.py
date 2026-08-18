#!/usr/bin/env python3
"""Prepara, em lotes retomáveis, uma base de discursos do Senado Federal.

Adaptação não interativa do notebook
``01-icd/assignments/02-final/01-preparar-base-discursos.ipynb``.

Para cada janela de datas, o script:
1. consulta a lista de pronunciamentos na API de Dados Abertos do Senado;
2. baixa os textos integrais em paralelo e em grupos limitados;
3. salva um parquet intermediário em ``<saida>/lotes``;
4. consolida os lotes em um parquet final e, opcionalmente, em CSV.

Lotes existentes são reutilizados por padrão, permitindo retomar execuções.
"""

from __future__ import annotations

import argparse
import calendar
import csv
import datetime as dt
import logging
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


BASE_URL = "https://legis.senado.leg.br/dadosabertos/"
MAX_DIAS_POR_LOTE = 29
STATUS_FORCELIST = (429, 500, 502, 503, 504)
COLUNAS_TEXTO = (
    "CodigoPronunciamento",
    "TextoDiscursoIntegral",
    "ok",
    "status",
    "msg",
)

# Ordem observada no dataset versionado usado pelo projeto anterior. Manter um
# esquema explícito evita que colunas raras mudem de posição conforme o mês em
# que aparecem pela primeira vez durante a consolidação dos lotes.
COLUNAS_CANONICAS = (
    "id",
    "CodigoPronunciamento",
    "Casa",
    "Data",
    "Resumo",
    "Indexacao",
    "TextoIntegral",
    "TextoIntegralTxt",
    "UrlTextoBinario",
    "TipoAutor",
    "FuncaoAutor",
    "NomeAutor",
    "CodigoParlamentar",
    "Partido",
    "UF",
    "TipoUsoPalavra.Codigo",
    "TipoUsoPalavra.Sigla",
    "TipoUsoPalavra.Descricao",
    "TipoUsoPalavra.IndicadorAtivo",
    "Publicacoes.Publicacao",
    "Apartes.Aparteante",
    "__janela_inicio",
    "__janela_fim",
    "CargoAutor",
    "OrgaoAutor",
    "PaisAutor",
    "TextoDiscursoIntegral",
    "ok",
    "status",
    "msg",
)

LOG = logging.getLogger("discursos_batch")


def parse_data(valor: str) -> dt.date:
    """Converte uma data ISO (AAAA-MM-DD) em ``date`` para o argparse."""
    try:
        return dt.datetime.strptime(valor, "%Y-%m-%d").date()
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"data inválida: {valor!r}; use AAAA-MM-DD"
        ) from exc


def montar_intervalos(
    inicio: dt.date, fim: dt.date, dias_por_lote: int
) -> list[tuple[dt.date, dt.date]]:
    """Gera janelas inclusivas e contíguas com até ``dias_por_lote`` dias."""
    if dias_por_lote < 1 or dias_por_lote > MAX_DIAS_POR_LOTE:
        raise ValueError(
            "dias_por_lote deve estar entre 1 e 29; a API do Senado limita "
            "cada consulta a, no máximo, um mês de calendário"
        )
    if fim < inicio:
        raise ValueError("a data final deve ser igual ou posterior à inicial")

    intervalos: list[tuple[dt.date, dt.date]] = []
    atual = inicio
    while atual <= fim:
        fim_lote = min(atual + dt.timedelta(days=dias_por_lote - 1), fim)
        intervalos.append((atual, fim_lote))
        atual = fim_lote + dt.timedelta(days=1)
    return intervalos


def montar_intervalos_calendario(
    inicio: dt.date, fim: dt.date
) -> list[tuple[dt.date, dt.date]]:
    """Gera janelas contidas em cada mês civil do período solicitado."""
    if fim < inicio:
        raise ValueError("a data final deve ser igual ou posterior à inicial")

    intervalos: list[tuple[dt.date, dt.date]] = []
    atual = inicio
    while atual <= fim:
        ultimo_dia = calendar.monthrange(atual.year, atual.month)[1]
        fim_do_mes = dt.date(atual.year, atual.month, ultimo_dia)
        fim_lote = min(fim_do_mes, fim)
        intervalos.append((atual, fim_lote))
        atual = fim_lote + dt.timedelta(days=1)
    return intervalos


def obter_intervalos(args: argparse.Namespace) -> list[tuple[dt.date, dt.date]]:
    """Seleciona a estratégia de particionamento solicitada."""
    if args.modo_lotes == "calendario":
        return montar_intervalos_calendario(args.data_inicio, args.data_fim)
    return montar_intervalos(
        args.data_inicio, args.data_fim, args.dias_por_lote
    )


def criar_sessao(
    tentativas: int, backoff: float, pool_size: int
) -> requests.Session:
    """Cria sessão HTTP com repetição automática para falhas transitórias."""
    retry = Retry(
        total=tentativas,
        connect=tentativas,
        read=tentativas,
        status=tentativas,
        backoff_factor=backoff,
        status_forcelist=STATUS_FORCELIST,
        allowed_methods=frozenset({"GET"}),
        respect_retry_after_header=True,
        raise_on_status=False,
    )
    adapter = HTTPAdapter(
        max_retries=retry,
        pool_connections=pool_size,
        pool_maxsize=pool_size,
    )
    sessao = requests.Session()
    sessao.mount("https://", adapter)
    sessao.headers.update({"User-Agent": "mcdia-dissertacao-discursos/1.0"})
    return sessao


def extrair_discursos(objeto: Any) -> list[dict[str, Any]]:
    """Localiza listas sob a chave ``Pronunciamento`` em envelopes aninhados."""
    encontrados: list[dict[str, Any]] = []

    def visitar(valor: Any) -> None:
        if isinstance(valor, dict):
            for chave, item in valor.items():
                if (
                    isinstance(chave, str)
                    and chave.casefold() == "pronunciamento"
                    and isinstance(item, list)
                ):
                    encontrados.extend(x for x in item if isinstance(x, dict))
                else:
                    visitar(item)
        elif isinstance(valor, list):
            for item in valor:
                visitar(item)

    visitar(objeto)
    return encontrados


def recuperar_lista_discursos(
    sessao: requests.Session,
    inicio: dt.date,
    fim: dt.date,
    timeout: float,
) -> pd.DataFrame:
    """Consulta os metadados dos pronunciamentos de uma única janela."""
    url = (
        f"{BASE_URL}plenario/lista/discursos/"
        f"{inicio:%Y%m%d}/{fim:%Y%m%d}.json"
    )
    LOG.info("Consultando lista: %s", url)
    resposta = sessao.get(
        url, headers={"Accept": "application/json"}, timeout=timeout
    )
    resposta.raise_for_status()
    discursos = extrair_discursos(resposta.json())
    if not discursos:
        return pd.DataFrame()

    df = pd.json_normalize(discursos, sep=".")
    df["__janela_inicio"] = inicio.isoformat()
    df["__janela_fim"] = fim.isoformat()
    return df


def encontrar_coluna(df: pd.DataFrame, alvo: str) -> str:
    """Encontra coluna por igualdade e, depois, por contenção sem caixa."""
    for coluna in df.columns:
        if coluna.casefold() == alvo.casefold():
            return coluna
    candidatas = [c for c in df.columns if alvo.casefold() in c.casefold()]
    if candidatas:
        return min(candidatas, key=len)
    raise KeyError(f"coluna obrigatória ausente: {alvo}; disponíveis: {list(df.columns)}")


def preparar_para_download(df_discursos: pd.DataFrame) -> pd.DataFrame:
    """Normaliza código/URL e mantém somente URLs HTTP(S) válidas."""
    if df_discursos.empty:
        return df_discursos.copy()

    df = df_discursos.copy()
    renomear: dict[str, str] = {}
    for alvo in ("TextoIntegralTxt", "CodigoPronunciamento"):
        real = encontrar_coluna(df, alvo)
        if real != alvo:
            renomear[real] = alvo
    if renomear:
        df = df.rename(columns=renomear)

    for coluna in ("TextoIntegralTxt", "CodigoPronunciamento"):
        df[coluna] = df[coluna].astype("string").str.strip()

    urls_validas = df["TextoIntegralTxt"].str.startswith(
        ("http://", "https://"), na=False
    )
    return df.loc[urls_validas].copy()


def normalizar_objeto_aninhado(valor: Any) -> Any:
    """Ordena chaves recursivamente para serialização Parquet determinística."""
    if isinstance(valor, np.ndarray):
        valor = valor.tolist()
    if isinstance(valor, list):
        return [normalizar_objeto_aninhado(item) for item in valor]
    if isinstance(valor, dict):
        return {
            chave: normalizar_objeto_aninhado(valor[chave])
            for chave in sorted(valor)
        }
    return valor


def normalizar_estrutura(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica ordem canônica de colunas e de campos aninhados.

    Colunas novas eventualmente introduzidas pela API são preservadas entre os
    metadados canônicos e os campos de resultado, evitando perda silenciosa.
    """
    resultado = df.copy()

    for coluna in COLUNAS_CANONICAS:
        if coluna not in resultado.columns:
            resultado[coluna] = pd.NA

    for coluna in ("Publicacoes.Publicacao",):
        resultado[coluna] = resultado[coluna].map(normalizar_objeto_aninhado)

    extras = [
        coluna for coluna in resultado.columns if coluna not in COLUNAS_CANONICAS
    ]
    campos_resultado = list(COLUNAS_TEXTO[1:])
    prefixo = [
        coluna for coluna in COLUNAS_CANONICAS if coluna not in campos_resultado
    ]
    ordem = prefixo + extras + campos_resultado
    return resultado.loc[:, ordem]


def validar_estrutura_canonica(df: pd.DataFrame) -> None:
    """Interrompe a gravação se o esquema mínimo estiver fora do padrão."""
    ausentes = [coluna for coluna in COLUNAS_CANONICAS if coluna not in df.columns]
    if ausentes:
        raise ValueError(f"colunas canônicas ausentes: {ausentes}")

    posicoes = {coluna: df.columns.get_loc(coluna) for coluna in COLUNAS_CANONICAS}
    for anterior, posterior in zip(COLUNAS_CANONICAS, COLUNAS_CANONICAS[1:]):
        if posicoes[anterior] >= posicoes[posterior]:
            raise ValueError(
                "ordem de colunas incompatível com o esquema canônico: "
                f"{anterior} deve anteceder {posterior}"
            )


def recuperar_texto(
    sessao: requests.Session,
    codigo: str,
    url: str,
    timeout: float,
) -> dict[str, Any]:
    """Baixa e higieniza o texto integral de um pronunciamento."""
    resultado: dict[str, Any] = {
        "CodigoPronunciamento": codigo,
        "TextoDiscursoIntegral": "",
        "ok": False,
        "status": None,
        "msg": "",
    }
    try:
        resposta = sessao.get(
            url,
            timeout=timeout,
            headers={"Accept": "text/plain, */*;q=0.1"},
            allow_redirects=True,
        )
        resultado["status"] = resposta.status_code
        if resposta.status_code == 404:
            resultado["msg"] = "404 (sem texto integral)"
            return resultado
        if resposta.status_code == 204:
            resultado["msg"] = "204 (sem conteúdo)"
            return resultado
        resposta.raise_for_status()

        texto = resposta.text or ""
        texto = re.sub(r"\s+\n", "\n", texto)
        texto = re.sub(r"[ \t]+", " ", texto).strip()
        if not texto:
            tipo = (resposta.headers.get("Content-Type") or "").lower()
            resultado["msg"] = f"vazio (Content-Type={tipo})"
            return resultado

        resultado["TextoDiscursoIntegral"] = texto
        resultado["ok"] = True
    except Exception as exc:  # registra falha por item sem abortar o lote
        resultado["msg"] = str(exc)
    return resultado


def fatiar(itens: pd.DataFrame, tamanho: int) -> Iterable[pd.DataFrame]:
    """Divide um DataFrame em grupos de tamanho limitado."""
    for inicio in range(0, len(itens), tamanho):
        yield itens.iloc[inicio : inicio + tamanho]


def baixar_textos(
    sessao: requests.Session,
    df_download: pd.DataFrame,
    max_workers: int,
    tamanho_lote: int,
    timeout: float,
) -> pd.DataFrame:
    """Baixa textos em grupos, usando paralelismo limitado dentro de cada grupo."""
    resultados: list[dict[str, Any]] = []
    total_grupos = max(1, (len(df_download) + tamanho_lote - 1) // tamanho_lote)

    for numero, grupo in enumerate(fatiar(df_download, tamanho_lote), start=1):
        LOG.info(
            "Baixando grupo de textos %d/%d (%d itens)",
            numero,
            total_grupos,
            len(grupo),
        )
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futuros = {
                executor.submit(
                    recuperar_texto,
                    sessao,
                    str(linha["CodigoPronunciamento"]),
                    str(linha["TextoIntegralTxt"]),
                    timeout,
                ): str(linha["CodigoPronunciamento"])
                for _, linha in grupo.iterrows()
            }
            for futuro in as_completed(futuros):
                codigo = futuros[futuro]
                try:
                    resultados.append(futuro.result())
                except Exception as exc:
                    resultados.append(
                        {
                            "CodigoPronunciamento": codigo,
                            "TextoDiscursoIntegral": "",
                            "ok": False,
                            "status": None,
                            "msg": str(exc),
                        }
                    )

    return pd.DataFrame(resultados, columns=COLUNAS_TEXTO)


def caminho_lote(diretorio: Path, inicio: dt.date, fim: dt.date) -> Path:
    return diretorio / f"discursos_{inicio.isoformat()}_{fim.isoformat()}.parquet"


def processar_lote(
    sessao: requests.Session,
    inicio: dt.date,
    fim: dt.date,
    destino: Path,
    args: argparse.Namespace,
) -> pd.DataFrame:
    """Processa uma janela ou reutiliza seu parquet intermediário."""
    if destino.exists() and not args.sobrescrever:
        LOG.info("Reutilizando lote existente: %s", destino)
        return normalizar_estrutura(pd.read_parquet(destino))

    discursos = recuperar_lista_discursos(
        sessao, inicio, fim, args.timeout_lista
    )
    LOG.info("Metadados recuperados no lote: %d", len(discursos))
    if discursos.empty:
        vazio = normalizar_estrutura(discursos)
        vazio.to_parquet(destino, index=False, compression="zstd")
        return vazio

    para_download = preparar_para_download(discursos)
    LOG.info("Discursos com URL de texto integral: %d", len(para_download))
    textos = baixar_textos(
        sessao,
        para_download,
        args.trabalhadores,
        args.tamanho_lote_textos,
        args.timeout_texto,
    )

    final = discursos.merge(textos, on="CodigoPronunciamento", how="left")
    final["ok"] = final["ok"].fillna(False).astype(bool)
    final = normalizar_estrutura(final)
    validar_estrutura_canonica(final)
    final.to_parquet(destino, index=False, engine="pyarrow", compression="zstd")
    LOG.info(
        "Lote salvo: %s (%d discursos; %d textos obtidos)",
        destino,
        len(final),
        int(final["ok"].sum()),
    )
    return final


def salvar_csv(df: pd.DataFrame, caminho: Path) -> None:
    copia = df.copy()
    colunas_objeto = copia.select_dtypes(include=["object", "string"]).columns
    if len(colunas_objeto):
        copia[colunas_objeto] = copia[colunas_objeto].replace(
            {r"\r\n?": "\n"}, regex=True
        )
    copia.to_csv(
        caminho,
        index=False,
        sep=";",
        quoting=csv.QUOTE_ALL,
        escapechar="\\",
        encoding="utf-8",
        lineterminator="\n",
    )


def criar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Baixa discursos do Senado em lotes retomáveis."
    )
    parser.add_argument("--data-inicio", required=True, type=parse_data)
    parser.add_argument("--data-fim", required=True, type=parse_data)
    parser.add_argument(
        "--diretorio-saida", type=Path, default=Path("_data")
    )
    parser.add_argument(
        "--modo-lotes",
        choices=("calendario", "dias"),
        default="calendario",
        help=(
            "estratégia: um mês civil por lote (calendario, padrão) "
            "ou quantidade fixa de dias (dias)"
        ),
    )
    parser.add_argument(
        "--dias-por-lote",
        type=int,
        default=MAX_DIAS_POR_LOTE,
        help=(
            "dias por consulta quando --modo-lotes=dias "
            "(1 a 29; padrão seguro: 29)"
        ),
    )
    parser.add_argument(
        "--tamanho-lote-textos",
        type=int,
        default=250,
        help="quantidade de textos por grupo de download (padrão: 250)",
    )
    parser.add_argument(
        "--trabalhadores",
        type=int,
        default=8,
        help="downloads simultâneos (padrão: 8)",
    )
    parser.add_argument("--timeout-lista", type=float, default=90.0)
    parser.add_argument("--timeout-texto", type=float, default=60.0)
    parser.add_argument("--tentativas", type=int, default=8)
    parser.add_argument("--backoff", type=float, default=0.6)
    parser.add_argument(
        "--pausa-entre-lotes",
        type=float,
        default=0.0,
        help="segundos de pausa entre janelas de datas",
    )
    parser.add_argument(
        "--sobrescrever",
        action="store_true",
        help="refaz lotes intermediários que já existem",
    )
    parser.add_argument(
        "--csv", action="store_true", help="gera também uma cópia CSV"
    )
    parser.add_argument(
        "--log-level",
        choices=("DEBUG", "INFO", "WARNING", "ERROR"),
        default="INFO",
    )
    return parser


def validar_argumentos(args: argparse.Namespace) -> None:
    obter_intervalos(args)
    if args.tamanho_lote_textos < 1:
        raise ValueError("tamanho_lote_textos deve ser positivo")
    if args.trabalhadores < 1:
        raise ValueError("trabalhadores deve ser positivo")
    if args.tentativas < 0:
        raise ValueError("tentativas não pode ser negativo")
    if args.pausa_entre_lotes < 0:
        raise ValueError("pausa_entre_lotes não pode ser negativa")


def executar(args: argparse.Namespace) -> Path:
    validar_argumentos(args)
    saida = args.diretorio_saida.resolve()
    lotes_dir = saida / "lotes"
    lotes_dir.mkdir(parents=True, exist_ok=True)

    intervalos = obter_intervalos(args)
    LOG.info(
        "Período dividido em %d lote(s), no modo %s",
        len(intervalos),
        args.modo_lotes,
    )
    sessao = criar_sessao(args.tentativas, args.backoff, args.trabalhadores)
    dataframes: list[pd.DataFrame] = []

    try:
        for numero, (inicio, fim) in enumerate(intervalos, start=1):
            LOG.info("Processando lote %d/%d: %s a %s", numero, len(intervalos), inicio, fim)
            destino = caminho_lote(lotes_dir, inicio, fim)
            dataframes.append(
                processar_lote(sessao, inicio, fim, destino, args)
            )
            if args.pausa_entre_lotes and numero < len(intervalos):
                time.sleep(args.pausa_entre_lotes)
    finally:
        sessao.close()

    nao_vazios = [df for df in dataframes if not df.empty]
    consolidado = (
        pd.concat(nao_vazios, ignore_index=True, sort=False)
        if nao_vazios
        else pd.DataFrame()
    )
    if "CodigoPronunciamento" in consolidado.columns:
        consolidado = consolidado.drop_duplicates(
            subset=["CodigoPronunciamento"], keep="last"
        )

    consolidado = normalizar_estrutura(consolidado)
    validar_estrutura_canonica(consolidado)

    nome = f"discursos_{args.data_inicio.isoformat()}_{args.data_fim.isoformat()}"
    parquet = saida / f"{nome}.parquet"
    consolidado.to_parquet(
        parquet, index=False, engine="pyarrow", compression="zstd"
    )
    if args.csv:
        csv_path = saida / f"{nome}.csv"
        salvar_csv(consolidado, csv_path)
        LOG.info("CSV consolidado salvo: %s", csv_path)

    sucessos = int(consolidado["ok"].fillna(False).sum()) if "ok" in consolidado else 0
    LOG.info(
        "Concluído: %d discursos, %d textos obtidos; parquet: %s",
        len(consolidado),
        sucessos,
        parquet,
    )
    return parquet


def main() -> int:
    parser = criar_parser()
    args = parser.parse_args()
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    try:
        executar(args)
    except (ValueError, KeyError, OSError, requests.RequestException) as exc:
        LOG.error("Falha: %s", exc)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

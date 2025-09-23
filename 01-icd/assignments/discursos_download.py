import os
import math
import time
import json
import datetime as dt
import logging
import requests
import pandas as pd
import re
from typing import List, Dict, Any, Iterable
from requests.adapters import HTTPAdapter, Retry
from concurrent.futures import ThreadPoolExecutor, as_completed
from pprint import pformat

BASE = "https://legis.senado.leg.br/dadosabertos/"

TIMEOUT_JSON = 90
TIMEOUT_TXT  = 60
RETRY_TOTAL  = 8
RETRY_BACKOFF = 0.6
STATUS_FORCELIST = [429, 500, 502, 503, 504]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger("discursos")

def make_session() -> requests.Session:
    s = requests.Session()
    retries = Retry(
        total=RETRY_TOTAL,
        backoff_factor=RETRY_BACKOFF,
        status_forcelist=STATUS_FORCELIST,
        allowed_methods=["GET"],
    )
    s.mount("https://", HTTPAdapter(max_retries=retries))

    log.info(f">>> Headers: {pformat(dict(s.headers))}")
    log.info(f">>> Cookies: {s.cookies}")
    log.info(f">>> Auth: {s.auth}")

    return s

log.info(f"Construindo sessão HTTP")
sess = make_session()

def montar_intervalo_de_datas(start: dt.date, end: dt.date, days_per_window: int = 31) -> List[tuple]:
    """Gera janelas [ini, fim] inclusive, com no máx. 'days_per_window' dias cada."""

    log.info(f">>> Montando intervalos de {days_per_window} dias para fazer download dos discursos em blocos")

    windows = []
    cur = start
    one_day = dt.timedelta(days=1)

    while cur <= end:
        w_end = min(cur + dt.timedelta(days=days_per_window - 1), end)
        windows.append((cur, w_end))
        log.info(f">>> >>> Janela {len(windows)}: {(cur, w_end)}")
        cur = w_end + one_day

    log.info(f">>> O download dos discursos será realizado em {len(windows)} intervalos")
    return windows

def extrair_discurso(obj: Any) -> List[Dict[str, Any]]:
    """
    Procura, recursivamente, qualquer lista sob a chave 'Pronunciamento'.
    Isso torna o parser resiliente a pequenas mudanças de envelope.
    """
    out = []

    def rec(x):
        if isinstance(x, dict):
            for k, v in x.items():
                if isinstance(k, str) and k.lower() == "pronunciamento" and isinstance(v, list):
                    out.extend(v)
                else:
                    rec(v)
        elif isinstance(x, list):
            for it in x:
                rec(it)

    rec(obj)
    return out

def recuperar_lista_discursos_por_periodo(data_inicio: dt.date, data_fim: dt.date, sleep_s: float = 0.0) -> pd.DataFrame:
    """
    Busca discursos do Plenário por janelas de data, agregando tudo num DataFrame.
    Endpoint: /plenario/lista/discursos/{AAAAMMDD}/{AAAAMMDD}.json
    """

    log.info(f">>> Preparando intervalos para download dos discursos de {data_inicio} a {data_fim}")
    windows = montar_intervalo_de_datas(data_inicio, data_fim, days_per_window=31)  # janelas de ~1 mês

    log.info(f">>> Iniciando download dos discursos em {len(windows)} intervalos")
    all_rows = []

    for i, (data_ini, data_fim) in enumerate(windows, 1):
        url = f"{BASE}plenario/lista/discursos/{data_ini.strftime('%Y%m%d')}/{data_fim.strftime('%Y%m%d')}.json"

        log.info(f">>> >>> GET: {url}")
        r = sess.get(url, headers={"Accept": "application/json"}, timeout=TIMEOUT_JSON)
        r.raise_for_status()
        j = r.json()

        log.info(f">>> >>> Extraindo discurso")
        pron = extrair_discurso(j)
        if pron:
            # flatten resiliente
            df = pd.json_normalize(pron, sep=".")
            # anexa janela de coleta (útil para auditoria)
            df["__janela_inicio"] = data_ini.isoformat()
            df["__janela_fim"] = data_fim.isoformat()
            all_rows.append(df)
            log.info(f">>> >>> Discursos extraídos: {len(all_rows)}")

        if sleep_s:
            time.sleep(sleep_s)

    if not all_rows:
        return pd.DataFrame()

    df_all = pd.concat(all_rows, ignore_index=True, sort=False)
    log.info(f">>> Discursos recuperados: {len(df_all)}")

    return df_all

def recuperar_e_gravar_texto_discurso(codigo_pron: str, url_txt: str) -> dict:
    out = {"CodigoPronunciamento": codigo_pron, "ArquivoTextoIntegral": "", "ok": False, "status": None, "msg": ""}

    try:
        log.info(f">>> GET: {url_txt}")
        r = sess.get(url_txt, timeout=TIMEOUT_TXT, headers={"Accept": "text/plain, */*;q=0.1"}, allow_redirects=True)
        out["status"] = r.status_code

        # log auxiliar para diagnosticar
        ct = (r.headers.get("Content-Type") or "").lower()
        if r.status_code == 404:
            out["msg"] = "404 (sem texto integral)";  return out
        if r.status_code == 204:
            out["msg"] = "204 (sem conteúdo)";        return out

        r.raise_for_status()

        # conteúdo
        txt = r.text or ""
        # limpeza leve (uso de re.sub, não r.sub)
        txt = re.sub(r"\s+\n", "\n", txt)
        txt = re.sub(r"[ \t]+", " ", txt).strip()

        # proteção: se veio vazio, registra e sai
        if not txt:
            out["msg"] = f"vazio (Content-Type={ct})"
            return out

        # salva
        TEXT_DIR = "_textos"
        os.makedirs(TEXT_DIR, exist_ok=True)
        path = os.path.join(TEXT_DIR, f"{codigo_pron}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(txt)

        out["ArquivoTextoIntegral"] = path
        out["ok"] = True
        return out

    except Exception as e:
        out["msg"] = str(e)
        return out

def _match_col(df: pd.DataFrame, alvo: str) -> str:
    """
    Tenta encontrar em df.columns a coluna equivalente a `alvo`.
    Estratégia: match exato (case-insensitive) -> contém (case-insensitive).
    Retorna o nome da coluna encontrada ou levanta KeyError.
    """
    cols = list(df.columns)
    # 1) exato (case-insensitive)
    for c in cols:
        if c.lower() == alvo.lower():
            return c
    # 2) contém (case-insensitive)
    candidatos = [c for c in cols if alvo.lower() in c.lower()]
    if candidatos:
        # prioriza o mais curto (geralmente o nome mais "limpo")
        return sorted(candidatos, key=len)[0]
    raise KeyError(f"Coluna obrigatória não encontrada: {alvo}. Disponíveis: {cols}")

def preparar_discursos_para_download(
    df_discursos: pd.DataFrame,
    cols_necessarias=("TextoIntegralTxt", "CodigoPronunciamento"),
    inplace: bool = False
) -> pd.DataFrame:
    """
    - Faz rename tolerante das colunas necessárias para os nomes canônicos em `cols_necessarias`.
    - Converte para string e strip.
    - Retorna APENAS as linhas com URL válida em `TextoIntegralTxt` (http/https).
    """
    df = df_discursos if inplace else df_discursos.copy()

    # 1) garantir/renomear colunas
    ren = {}
    for alvo in cols_necessarias:
        col_real = _match_col(df, alvo)
        if col_real != alvo:
            ren[col_real] = alvo
    if ren:
        df = df.rename(columns=ren)

    # 2) normalizar valores
    for alvo in cols_necessarias:
        df[alvo] = df[alvo].astype(str).str.strip()

    # 3) filtrar URLs válidas
    df_filtrado = df[df["TextoIntegralTxt"].str.startswith(("http://", "https://"), na=False)].copy()

    return df_filtrado

def fazer_download_texto_discursos(
    df_download,
    fetch_fn,                 # ex.: fetch_and_save_txt(codigo_pron, url_txt)
    max_workers: int = 8
):
    """
    Executa fetch_fn(CodigoPronunciamento, TextoIntegralTxt) em paralelo
    para cada linha de df_download e retorna a lista 'resultados'.

    - fetch_fn deve retornar um dict (ex.: {"CodigoPronunciamento":..., "ok":..., ...})
    """
    resultados = []
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futs = {
            ex.submit(fetch_fn, row["CodigoPronunciamento"], row["TextoIntegralTxt"]): row
            for _, row in df_download.iterrows()
        }
        for fut in as_completed(futs):
            row = futs[fut]
            try:
                resultados.append(fut.result())
            except Exception as e:
                resultados.append({
                    "CodigoPronunciamento": row.get("CodigoPronunciamento"),
                    "ok": False,
                    "msg": str(e),
                })
    return pd.DataFrame(resultados)

def _parse_data(s: str) -> dt.date:
    s = (s or "").strip()
    formatos = ("%Y-%m-%d", "%d/%m/%Y")
    for fmt in formatos:
        try:
            return dt.datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    raise ValueError(f"Data inválida: '{s}'. Use YYYY-MM-DD ou DD/MM/AAAA.")

def ler_intervalo_datas() -> tuple[dt.date, dt.date]:
    print("Informe o intervalo de datas (ex.: 2019-03-29 ou 29/03/2019).")
    s_ini = input("Data inicial: ").strip()
    s_fim = input("Data final  : ").strip()
    ini = _parse_data(s_ini)
    fim = _parse_data(s_fim)
    if fim < ini:
        # se o usuário inverteu, trocamos
        ini, fim = fim, ini
        print(f"Aviso: datas invertidas. Usando {ini} → {fim}.")
    return ini, fim

def main():
    ini, fim = ler_intervalo_datas()

    log.info(f"Recuperando lista de discursos realizados no período de {ini} a {fim}")
    df_discursos = recuperar_lista_discursos_por_periodo(ini, fim, sleep_s=0.0)
    log.info(f"Lista de discursos recuperados: {len(df_discursos)}")

    log.info(f"Prepando discursos para download")
    df_download = preparar_discursos_para_download(df_discursos)
    log.info(f"Discursos com link para download do texto integral {len(df_download)}")    

    log.info(f"Iniciando download do texto integral do discurso com link para texto integral: {len(df_download)}")    
    df_txt = fazer_download_texto_discursos(df_download, recuperar_e_gravar_texto_discurso, max_workers=8)
    log.info(f"Foi realizado o download dos textos de discursos: {len(df_txt)}")

    df_final = df_discursos.merge(
        df_txt[["CodigoPronunciamento", "ArquivoTextoIntegral", "ok", "status", "msg"]],
        on="CodigoPronunciamento",
        how="left"
    )
    log.info(f"Textos no data frame final: {len(df_final)}")

    log.info(f"Discursos por período: {len(df_discursos):,} linhas")

    log.info(f"Salvando arquivo com a lista dos discursos")    
    os.makedirs("_data", exist_ok=True)
    out_path2 = f"_data/discursos_{ini.isoformat()}_{fim.isoformat()}.csv"
    df_final.to_csv(out_path2, index=False, sep=";", encoding="utf-8-sig")
    log.info(f"OK: {df_txt['ok'].sum()} textos baixados, {len(df_txt)-df_txt['ok'].sum()} sem texto. Arquivo salvo em: {out_path2}")

if __name__ == "__main__":
    main()

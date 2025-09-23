import os
import math
import time
import json
import datetime as dt
from typing import List, Dict, Any, Iterable

import requests
import pandas as pd
import re
from requests.adapters import HTTPAdapter, Retry
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = "https://legis.senado.leg.br/dadosabertos/"

# ---------- Sessão HTTP com retries ----------
def make_session() -> requests.Session:
    s = requests.Session()
    retries = Retry(
        total=8,
        backoff_factor=0.6,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    s.mount("https://", HTTPAdapter(max_retries=retries))
    s.headers.update({"Accept": "application/json"})
    return s

sess = make_session()

# ---------- Util: datas e janelas ----------
def yyyymmdd(d: dt.date) -> str:
    return d.strftime("%Y%m%d")

def make_windows(start: dt.date, end: dt.date, days_per_window: int = 31) -> List[tuple]:
    """Gera janelas [ini, fim] inclusive, com no máx. 'days_per_window' dias cada."""
    windows = []
    cur = start
    one_day = dt.timedelta(days=1)
    while cur <= end:
        w_end = min(cur + dt.timedelta(days=days_per_window - 1), end)
        windows.append((cur, w_end))
        cur = w_end + one_day
    return windows

# ---------- Util: extrair lista "Pronunciamento" de qualquer JSON ----------
def extract_pronunciamentos(obj: Any) -> List[Dict[str, Any]]:
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

def fetch_discursos_periodo(data_inicio: dt.date, data_fim: dt.date, sleep_s: float = 0.0) -> pd.DataFrame:
    """
    Busca discursos do Plenário por janelas de data, agregando tudo num DataFrame.
    Endpoint: /plenario/lista/discursos/{AAAAMMDD}/{AAAAMMDD}.json
    """
    windows = make_windows(data_inicio, data_fim, days_per_window=31)  # janelas de ~1 mês
    all_rows = []

    for i, (ini, fim) in enumerate(windows, 1):
        url = f"{BASE}plenario/lista/discursos/{yyyymmdd(ini)}/{yyyymmdd(fim)}.json"
        print(url)
        r = sess.get(url, timeout=90)
        r.raise_for_status()
        j = r.json()

        pron = extract_pronunciamentos(j)
        if pron:
            # flatten resiliente
            df = pd.json_normalize(pron, sep=".")
            # anexa janela de coleta (útil para auditoria)
            df["__janela_inicio"] = ini.isoformat()
            df["__janela_fim"] = fim.isoformat()
            all_rows.append(df)

        if sleep_s:
            time.sleep(sleep_s)

    if not all_rows:
        return pd.DataFrame()

    df_all = pd.concat(all_rows, ignore_index=True, sort=False)
    return df_all

def fetch_and_save_txt(codigo_pron: str, url_txt: str) -> dict:
    out = {"CodigoPronunciamento": codigo_pron, "ArquivoTextoIntegral": "", "ok": False, "status": None, "msg": ""}

    try:
        print("GET:", url_txt)
        sess.headers.update({"Accept": "text/plain, */*;q=0.1"})
        r = sess.get(url_txt, timeout=60, allow_redirects=True)
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

if __name__ == "__main__":
    ini = dt.date(2019, 3, 29)
    fim = dt.date(2019, 3, 31)
    
    df_discursos = fetch_discursos_periodo(ini, fim, sleep_s=0.0)
    print(f"Discursos recuperados: ", len(df_discursos))

    for needed in ["TextoIntegralTxt", "CodigoPronunciamento"]:
        if needed not in df_discursos.columns:
            # tenta localizar nomes equivalentes
            candidatos = [c for c in df_discursos.columns if needed.lower() in c.lower()]
            if candidatos:
                df_discursos = df_discursos.rename(columns={candidatos[0]: needed})
            else:
                raise KeyError(f"Coluna obrigatória não encontrada: {needed}")

    df_discursos["TextoIntegralTxt"] = df_discursos["TextoIntegralTxt"].astype(str).str.strip()
    df_discursos["CodigoPronunciamento"] = df_discursos["CodigoPronunciamento"].astype(str).str.strip()
    
    # remove linhas sem URL
    df_download = df_discursos[df_discursos["TextoIntegralTxt"].str.startswith("http")].copy()
    print(f"Discursos com link para texto integral: ", len(df_download))    

    TEXT_DIR = "_textos"
    os.makedirs(TEXT_DIR, exist_ok=True)

    # --- 3) Download em paralelo (rápido)
    resultados = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {
            ex.submit(fetch_and_save_txt, row["CodigoPronunciamento"], row["TextoIntegralTxt"]): i
            for i, row in df_download.iterrows()
        }
        for fut in as_completed(futs):
            resultados.append(fut.result())

    df_txt = pd.DataFrame(resultados)
    print(f"Textos baixados: ", len(df_txt))

    # --- 4) Merge de volta no DataFrame principal
    df_final = df_discursos.merge(
        df_txt[["CodigoPronunciamento", "ArquivoTextoIntegral", "ok", "status", "msg"]],
        on="CodigoPronunciamento",
        how="left"
    )
    print(f"Textos no data frame final: ", len(df_final))

    print(f"Discursos por período: {len(df_discursos):,} linhas")
    
    os.makedirs("_data", exist_ok=True)
    out_path2 = f"_data/discursos_{ini.isoformat()}_{fim.isoformat()}.csv"
    df_final.to_csv(out_path2, index=False, sep=";", encoding="utf-8-sig")
    print(f"OK: {df_txt['ok'].sum()} textos baixados, {len(df_txt)-df_txt['ok'].sum()} sem texto. Arquivo salvo em: {out_path2}")

import os
import math
import time
import json
import datetime as dt
from typing import List, Dict, Any, Iterable

import requests
import pandas as pd
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

if __name__ == "__main__":
    ini = dt.date(2019, 1, 1)
    fim = dt.date(2023, 1, 31)
    
    df_discursos = fetch_discursos_periodo(ini, fim, sleep_s=0.0)
    print(f"Discursos por período: {len(df_discursos):,} linhas")
    
    # Salvar CSV final
    os.makedirs("_data", exist_ok=True)
    out_path = f"_data/discursos_{ini.isoformat()}_{fim.isoformat()}.csv"
    df_discursos.to_csv(out_path, index=False, sep=";", encoding="utf-8-sig")
    print(f"Salvo em: {out_path}")

#!/usr/bin/env python3
"""Teste de conexao com Chroma Cloud via chromadb.CloudClient.

Variaveis esperadas:
  CHROMA_API_KEY=...
  CHROMA_TENANT=...
  CHROMA_DATABASE=...
"""

from __future__ import annotations

import os
import sys

import chromadb


def require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        print(f"[erro] Variavel ausente: {name}")
        sys.exit(1)
    return value


def main() -> int:
    api_key = require_env("CHROMA_API_KEY")
    tenant = require_env("CHROMA_TENANT")
    database = require_env("CHROMA_DATABASE")

    print("== Chroma CloudClient test ==")
    print(f"tenant: {tenant}")
    print(f"database: {database}")

    try:
        client = chromadb.CloudClient(
            api_key=api_key,
            tenant=tenant,
            database=database,
        )
        collections = client.list_collections()
        print("conexao ok")
        print(f"collections: {len(collections)}")
        return 0
    except Exception as exc:
        print(f"falha no CloudClient: {type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

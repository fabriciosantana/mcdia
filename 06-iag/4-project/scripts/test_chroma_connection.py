#!/usr/bin/env python3
"""Teste de conectividade/autenticacao com Chroma remoto via env vars.

Compatível com o estilo de configuracao do Open WebUI:
  CHROMA_HTTP_HOST=api.trychroma.com
  CHROMA_HTTP_PORT=443
  CHROMA_HTTP_SSL=true
  CHROMA_HTTP_HEADERS=X-Chroma-Token=...
  CHROMA_TENANT=...
  CHROMA_DATABASE=...

Tambem aceita aliases:
  CHROMA_HOST
  CHROMA_PORT
  CHROMA_SSL
  CHROMA_API_KEY
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any

import chromadb
import requests
from chromadb.config import Settings


def env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        print(f"[erro] Variavel ausente: {name}")
        sys.exit(1)
    return value


def first_env(*names: str, default: str | None = None) -> str | None:
    for name in names:
        value = os.getenv(name)
        if value is not None and value.strip() != "":
            return value.strip()
    return default


def parse_headers(raw: str) -> dict[str, str]:
    headers: dict[str, str] = {}
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        if "=" not in item:
            raise ValueError(f"Header invalido: {item!r}")
        key, value = item.split("=", 1)
        headers[key.strip()] = value.strip()
    return headers


def print_response(label: str, response: requests.Response) -> None:
    print(f"\n[{label}]")
    print(f"status: {response.status_code}")
    print(f"url: {response.url}")
    try:
        body: Any = response.json()
        print("body:", json.dumps(body, ensure_ascii=True))
    except Exception:
        text = response.text.strip()
        print("body:", text[:500] if text else "<vazio>")


def main() -> int:
    host = first_env("CHROMA_HTTP_HOST", "CHROMA_HOST")
    if not host:
        print("[erro] Variavel ausente: CHROMA_HTTP_HOST/CHROMA_HOST")
        return 1
    tenant = require_env("CHROMA_TENANT")
    database = require_env("CHROMA_DATABASE")
    port = int(first_env("CHROMA_HTTP_PORT", "CHROMA_PORT", default="443"))
    ssl = env_bool("CHROMA_HTTP_SSL", env_bool("CHROMA_SSL", True))

    scheme = "https" if ssl else "http"
    base_url = f"{scheme}://{host}:{port}"
    headers_raw = first_env("CHROMA_HTTP_HEADERS", default="")
    api_key = first_env("CHROMA_API_KEY", default="")

    headers: dict[str, str] = {}
    if headers_raw:
        headers = parse_headers(headers_raw)
    elif api_key:
        # Chroma CloudClient usa X-Chroma-Token; mantemos o mesmo fallback aqui.
        headers = {"X-Chroma-Token": api_key}

    auth_provider = first_env("CHROMA_CLIENT_AUTH_PROVIDER", default="")
    auth_credentials = first_env("CHROMA_CLIENT_AUTH_CREDENTIALS", default="")

    print("== Chroma connection test ==")
    print(f"base_url: {base_url}")
    print(f"tenant: {tenant}")
    print(f"database: {database}")
    print(f"headers: {sorted(headers.keys())}")
    if auth_provider:
        print(f"auth_provider: {auth_provider}")

    try:
        resp = requests.get(f"{base_url}/api/v2/heartbeat", headers=headers, timeout=15)
        print_response("heartbeat", resp)
    except Exception as exc:
        print(f"\n[heartbeat]\nfalha de rede: {exc}")
        return 2

    try:
        resp = requests.get(f"{base_url}/api/v2/auth/identity", headers=headers, timeout=15)
        print_response("auth_identity", resp)
    except Exception as exc:
        print(f"\n[auth_identity]\nfalha de rede: {exc}")
        return 3

    print("\n[chromadb.HttpClient]")
    try:
        settings = Settings()
        if auth_provider:
            settings.chroma_client_auth_provider = auth_provider
        if auth_credentials:
            settings.chroma_client_auth_credentials = auth_credentials
        client = chromadb.HttpClient(
            host=host,
            port=port,
            ssl=ssl,
            headers=headers,
            tenant=tenant,
            database=database,
            settings=settings,
        )
        collections = client.list_collections()
        print("conexao ok")
        print(f"collections: {len(collections)}")
        return 0
    except Exception as exc:
        print(f"falha no cliente chromadb: {type(exc).__name__}: {exc}")
        return 4


if __name__ == "__main__":
    raise SystemExit(main())

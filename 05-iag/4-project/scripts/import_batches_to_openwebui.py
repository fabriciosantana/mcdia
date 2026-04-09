#!/usr/bin/env python3
"""Importa batches para uma Knowledge Base do Open WebUI via API.

Fluxo:
1. Faz upload do arquivo em /api/v1/files/
2. Espera o processamento terminar em /api/v1/files/{id}/process/status
3. Adiciona o arquivo ao Knowledge em /api/v1/knowledge/{knowledge_id}/file/add

Exemplo:
  OPENWEBUI_URL=http://localhost:8080 \
  OPENWEBUI_API_KEY=seu_token \
  python scripts/import_batches_to_openwebui.py \
    --knowledge-id SEU_KNOWLEDGE_ID \
    --pattern 'knowledge_openwebui/md_batches/batch_*.md'
"""

from __future__ import annotations

import argparse
import glob
import os
import random
import sys
import time
from pathlib import Path

import requests


def load_dotenv(dotenv_path: Path) -> None:
    if not dotenv_path.exists():
        return

    for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()

        if not key:
            continue

        if value and len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]

        os.environ.setdefault(key, value)


def require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise SystemExit(f"Variavel obrigatoria ausente: {name}")
    return value


def api_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }


def upload_file(base_url: str, token: str, file_path: Path) -> dict:
    with file_path.open("rb") as f:
        response = requests.post(
            f"{base_url}/api/v1/files/",
            headers=api_headers(token),
            files={"file": (file_path.name, f)},
            timeout=120,
        )
    if response.status_code != 200:
        raise RuntimeError(f"Upload falhou para {file_path.name}: {response.status_code} {response.text}")
    return response.json()


def wait_for_processing(
    base_url: str,
    token: str,
    file_id: str,
    timeout_seconds: int,
    poll_interval: float,
) -> dict:
    deadline = time.time() + timeout_seconds
    url = f"{base_url}/api/v1/files/{file_id}/process/status"

    while time.time() < deadline:
        response = requests.get(url, headers=api_headers(token), timeout=30)
        if response.status_code != 200:
            raise RuntimeError(f"Falha ao consultar status do arquivo {file_id}: {response.status_code} {response.text}")

        payload = response.json()
        status = payload.get("status")

        if status == "completed":
            return payload
        if status == "failed":
            raise RuntimeError(f"Processamento falhou para arquivo {file_id}: {payload}")

        time.sleep(poll_interval)

    raise TimeoutError(f"Timeout aguardando processamento do arquivo {file_id}")


def add_file_to_knowledge(base_url: str, token: str, knowledge_id: str, file_id: str) -> dict:
    response = requests.post(
        f"{base_url}/api/v1/knowledge/{knowledge_id}/file/add",
        headers={**api_headers(token), "Content-Type": "application/json"},
        json={"file_id": file_id},
        timeout=60,
    )
    if response.status_code != 200:
        raise RuntimeError(
            f"Falha ao adicionar file_id={file_id} ao knowledge_id={knowledge_id}: "
            f"{response.status_code} {response.text}"
    )
    return response.json()


def is_openai_rate_limit_error(exc: Exception) -> bool:
    text = str(exc)
    return "429" in text and "api.openai.com/v1/embeddings" in text


def add_file_to_knowledge_with_retry(
    base_url: str,
    token: str,
    knowledge_id: str,
    file_id: str,
    max_retries: int,
    initial_backoff: float,
    max_backoff: float,
) -> dict:
    attempt = 0

    while True:
        try:
            return add_file_to_knowledge(
                base_url=base_url,
                token=token,
                knowledge_id=knowledge_id,
                file_id=file_id,
            )
        except Exception as exc:  # noqa: BLE001
            attempt += 1
            if not is_openai_rate_limit_error(exc) or attempt > max_retries:
                raise

            sleep_seconds = min(initial_backoff * (2 ** (attempt - 1)), max_backoff)
            sleep_seconds += random.uniform(0, 1)
            print(
                f"  rate limit da OpenAI ao adicionar ao knowledge; "
                f"tentativa {attempt}/{max_retries}, aguardando {sleep_seconds:.1f}s"
            )
            time.sleep(sleep_seconds)


def main() -> int:
    parser = argparse.ArgumentParser(description="Importa batches para Open WebUI Knowledge via API.")
    parser.add_argument("--knowledge-id", required=True, help="ID da Knowledge Base no Open WebUI.")
    parser.add_argument(
        "--pattern",
        default="knowledge_openwebui/md_batches/batch_*.md",
        help="Glob dos arquivos a importar.",
    )
    parser.add_argument(
        "--start-from",
        default="",
        help="Nome do arquivo a partir do qual iniciar, ex.: batch_00031.md",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Numero maximo de arquivos a importar nesta execucao. 0 = sem limite.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=1800,
        help="Tempo maximo de espera por arquivo.",
    )
    parser.add_argument(
        "--poll-interval",
        type=float,
        default=2.0,
        help="Intervalo de polling do status de processamento.",
    )
    parser.add_argument(
        "--max-add-retries",
        type=int,
        default=8,
        help="Numero maximo de retries ao receber rate limit da OpenAI na etapa de add.",
    )
    parser.add_argument(
        "--initial-backoff",
        type=float,
        default=10.0,
        help="Backoff inicial em segundos para retries de rate limit.",
    )
    parser.add_argument(
        "--max-backoff",
        type=float,
        default=120.0,
        help="Backoff maximo em segundos para retries de rate limit.",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    load_dotenv(project_root / ".env")

    base_url = require_env("OPENWEBUI_URL").rstrip("/")
    token = require_env("OPENWEBUI_API_KEY")

    file_paths = sorted(Path(p) for p in glob.glob(args.pattern))
    if not file_paths:
        raise SystemExit(f"Nenhum arquivo encontrado para o padrao: {args.pattern}")

    if args.start_from:
        file_paths = [p for p in file_paths if p.name >= args.start_from]

    if args.limit > 0:
        file_paths = file_paths[: args.limit]

    if not file_paths:
        raise SystemExit("Nenhum arquivo restante apos aplicar os filtros.")

    print(f"Base URL: {base_url}")
    print(f"Knowledge ID: {args.knowledge_id}")
    print(f"Arquivos a importar: {len(file_paths)}")

    imported = 0
    failed = 0
    imported_files: list[str] = []
    failed_files: list[str] = []

    for index, file_path in enumerate(file_paths, start=1):
        print(f"\n[{index}/{len(file_paths)}] Importando {file_path.name}")
        try:
            upload_payload = upload_file(base_url, token, file_path)
            file_id = upload_payload["id"]
            print(f"  upload ok -> file_id={file_id}")

            wait_for_processing(
                base_url=base_url,
                token=token,
                file_id=file_id,
                timeout_seconds=args.timeout_seconds,
                poll_interval=args.poll_interval,
            )
            print("  processamento concluido")

            add_file_to_knowledge_with_retry(
                base_url=base_url,
                token=token,
                knowledge_id=args.knowledge_id,
                file_id=file_id,
                max_retries=args.max_add_retries,
                initial_backoff=args.initial_backoff,
                max_backoff=args.max_backoff,
            )
            print("  adicionado ao knowledge")
            imported += 1
            imported_files.append(file_path.name)
        except Exception as exc:  # noqa: BLE001
            failed += 1
            failed_files.append(file_path.name)
            print(f"  erro: {exc}", file=sys.stderr)

    print("\nResumo:")
    print(f"  importados: {imported}")
    print(f"  falharam: {failed}")
    if imported_files:
        print("  arquivos importados com sucesso:")
        for name in imported_files:
            print(f"    - {name}")
    if failed_files:
        print("  arquivos que falharam:")
        for name in failed_files:
            print(f"    - {name}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

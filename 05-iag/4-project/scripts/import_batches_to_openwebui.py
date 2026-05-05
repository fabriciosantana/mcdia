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
import hashlib
import json
import logging
import os
import random
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

LOGGER = logging.getLogger("import_batches_to_openwebui")
STATE_VERSION = 1


def configure_logging(verbose: bool = False) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(levelname)s %(message)s",
    )


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


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file_obj:
        for chunk in iter(lambda: file_obj.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_import_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"version": STATE_VERSION, "imports": {}}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Estado de importacao invalido em {path}")
    payload.setdefault("version", STATE_VERSION)
    payload.setdefault("imports", {})
    return payload


def write_import_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    state["updated_at_utc"] = utc_timestamp()
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def state_files_for_knowledge(state: dict[str, Any], knowledge_id: str) -> dict[str, Any]:
    imports = state.setdefault("imports", {})
    knowledge_state = imports.setdefault(knowledge_id, {"files": {}})
    return knowledge_state.setdefault("files", {})


def build_state_entry(
    *,
    file_path: Path,
    knowledge_id: str,
    status: str,
    attempts: int,
    file_id: str = "",
    error: str = "",
) -> dict[str, Any]:
    return {
        "file_name": file_path.name,
        "file_path": str(file_path),
        "knowledge_id": knowledge_id,
        "sha256": sha256_file(file_path),
        "size_bytes": file_path.stat().st_size,
        "status": status,
        "attempts": attempts,
        "file_id": file_id,
        "error": error,
        "updated_at_utc": utc_timestamp(),
    }


def should_skip_imported_file(
    *,
    state: dict[str, Any],
    knowledge_id: str,
    file_path: Path,
) -> bool:
    entry = state.get("imports", {}).get(knowledge_id, {}).get("files", {}).get(file_path.name)
    if not isinstance(entry, dict) or entry.get("status") != "added":
        return False
    return entry.get("sha256") == sha256_file(file_path)


def update_import_state_entry(
    *,
    state: dict[str, Any],
    state_path: Path,
    knowledge_id: str,
    file_path: Path,
    status: str,
    file_id: str = "",
    error: str = "",
) -> dict[str, Any]:
    files = state_files_for_knowledge(state, knowledge_id)
    previous = files.get(file_path.name, {})
    previous_attempts = int(previous.get("attempts", 0))
    if status == "uploaded":
        attempts = previous_attempts + 1
    elif status == "failed" and previous.get("status") not in {"uploaded", "processed"}:
        attempts = previous_attempts + 1
    else:
        attempts = previous_attempts or 1
    entry = build_state_entry(
        file_path=file_path,
        knowledge_id=knowledge_id,
        status=status,
        attempts=attempts,
        file_id=file_id or str(previous.get("file_id", "")),
        error=error,
    )
    files[file_path.name] = entry
    write_import_state(state_path, state)
    return entry


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
            LOGGER.warning(
                "rate limit da OpenAI ao adicionar ao knowledge; tentativa %s/%s, aguardando %.1fs",
                attempt,
                max_retries,
                sleep_seconds,
            )
            time.sleep(sleep_seconds)


def summarize_numeric(values: list[float]) -> dict[str, float | None]:
    if not values:
        return {"min": None, "avg": None, "max": None}
    return {
        "min": round(min(values), 3),
        "avg": round(sum(values) / len(values), 3),
        "max": round(max(values), 3),
    }


def build_import_summary(
    *,
    executed_at_utc: str,
    finished_at_utc: str,
    duration_seconds: float,
    base_url: str,
    knowledge_id: str,
    pattern: str,
    start_from: str,
    limit: int,
    total_matched_files: int,
    skipped_by_start_from: int,
    selected_files: list[Path],
    rows: list[dict[str, Any]],
    summary_path: Path,
    state_path: Path,
    resume: bool,
    dry_run: bool,
) -> dict[str, Any]:
    imported_count = sum(1 for row in rows if row.get("status") == "imported")
    failed_count = sum(1 for row in rows if row.get("status") == "failed")
    skipped_count = sum(1 for row in rows if row.get("status") == "skipped_already_imported")
    dry_run_count = sum(1 for row in rows if row.get("status") == "dry_run")
    durations = [
        float(row["duration_seconds"])
        for row in rows
        if row.get("duration_seconds") not in ("", None)
    ]
    return {
        "executed_at_utc": executed_at_utc,
        "finished_at_utc": finished_at_utc,
        "duration_seconds": round(duration_seconds, 3),
        "openwebui_base_url": base_url,
        "knowledge_id": knowledge_id,
        "resume_enabled": resume,
        "dry_run": dry_run,
        "selection": {
            "pattern": pattern,
            "start_from": start_from,
            "limit": limit,
            "total_matched_files": total_matched_files,
            "selected_files": len(selected_files),
            "skipped_by_start_from": skipped_by_start_from,
        },
        "files": {
            "imported": imported_count,
            "failed": failed_count,
            "skipped_already_imported": skipped_count,
            "dry_run": dry_run_count,
            "attempted": len(rows),
        },
        "timing": {
            "file_duration_seconds": summarize_numeric(durations),
        },
        "file_results": rows,
        "artifacts": {
            "import_summary": str(summary_path),
            "import_state": str(state_path),
        },
    }


def write_import_summary(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


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
    parser.add_argument(
        "--state-file",
        default="knowledge_openwebui/import_state.json",
        help="Arquivo JSON de checkpoint da importacao.",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Pula automaticamente batches ja marcados como adicionados no estado.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Mostra os batches que seriam importados sem chamar a API nem atualizar o estado.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Exibe logs detalhados da importacao.",
    )
    args = parser.parse_args()
    configure_logging(args.verbose)

    project_root = Path(__file__).resolve().parents[1]
    load_dotenv(project_root / ".env")

    base_url = os.getenv("OPENWEBUI_URL", "").strip().rstrip("/") if args.dry_run else require_env("OPENWEBUI_URL").rstrip("/")
    token = "" if args.dry_run else require_env("OPENWEBUI_API_KEY")
    state_path = (project_root / args.state_file).resolve() if not Path(args.state_file).is_absolute() else Path(args.state_file)
    import_state = load_import_state(state_path)

    matched_file_paths = sorted(Path(p) for p in glob.glob(args.pattern))
    if not matched_file_paths:
        raise SystemExit(f"Nenhum arquivo encontrado para o padrao: {args.pattern}")

    file_paths = matched_file_paths
    skipped_by_start_from = 0
    if args.start_from:
        skipped_by_start_from = sum(1 for p in file_paths if p.name < args.start_from)
        file_paths = [p for p in file_paths if p.name >= args.start_from]

    if args.limit > 0:
        file_paths = file_paths[: args.limit]

    if not file_paths:
        raise SystemExit("Nenhum arquivo restante apos aplicar os filtros.")

    ts = utc_timestamp()
    summary_path = project_root / "knowledge_openwebui" / f"import_summary_{ts}.json"

    LOGGER.info("Base URL: %s", base_url or "<dry-run>")
    LOGGER.info("Knowledge ID: %s", args.knowledge_id)
    LOGGER.info("Arquivos a importar: %s", len(file_paths))
    LOGGER.info("State file: %s", state_path)
    if args.resume:
        LOGGER.info("Resume habilitado: batches ja adicionados serao pulados quando hash e knowledge_id coincidirem")
    if args.dry_run:
        LOGGER.info("Dry-run habilitado: nenhuma chamada de API sera realizada")

    imported = 0
    failed = 0
    skipped = 0
    dry_run_count = 0
    imported_files: list[str] = []
    failed_files: list[str] = []
    skipped_files: list[str] = []
    rows: list[dict[str, Any]] = []
    run_started_monotonic = time.monotonic()

    for index, file_path in enumerate(file_paths, start=1):
        file_started_monotonic = time.monotonic()
        row: dict[str, Any] = {
            "file_name": file_path.name,
            "file_path": str(file_path),
            "status": "failed",
            "file_id": "",
            "duration_seconds": None,
            "error": "",
            "attempts": 0,
        }
        if args.resume and should_skip_imported_file(
            state=import_state,
            knowledge_id=args.knowledge_id,
            file_path=file_path,
        ):
            skipped += 1
            skipped_files.append(file_path.name)
            row["status"] = "skipped_already_imported"
            row["duration_seconds"] = round(time.monotonic() - file_started_monotonic, 3)
            rows.append(row)
            LOGGER.info("[%s/%s] Pulando %s: ja consta como adicionado no estado", index, len(file_paths), file_path.name)
            continue

        if args.dry_run:
            dry_run_count += 1
            row["status"] = "dry_run"
            row["duration_seconds"] = round(time.monotonic() - file_started_monotonic, 3)
            rows.append(row)
            LOGGER.info("[%s/%s] Dry-run: importaria %s", index, len(file_paths), file_path.name)
            continue

        LOGGER.info("[%s/%s] Importando %s", index, len(file_paths), file_path.name)
        try:
            upload_payload = upload_file(base_url, token, file_path)
            file_id = upload_payload["id"]
            row["file_id"] = file_id
            state_entry = update_import_state_entry(
                state=import_state,
                state_path=state_path,
                knowledge_id=args.knowledge_id,
                file_path=file_path,
                status="uploaded",
                file_id=file_id,
            )
            row["attempts"] = state_entry["attempts"]
            LOGGER.info("upload ok para %s -> file_id=%s", file_path.name, file_id)

            wait_for_processing(
                base_url=base_url,
                token=token,
                file_id=file_id,
                timeout_seconds=args.timeout_seconds,
                poll_interval=args.poll_interval,
            )
            state_entry = update_import_state_entry(
                state=import_state,
                state_path=state_path,
                knowledge_id=args.knowledge_id,
                file_path=file_path,
                status="processed",
                file_id=file_id,
            )
            row["attempts"] = state_entry["attempts"]
            LOGGER.info("processamento concluido para %s", file_path.name)

            add_file_to_knowledge_with_retry(
                base_url=base_url,
                token=token,
                knowledge_id=args.knowledge_id,
                file_id=file_id,
                max_retries=args.max_add_retries,
                initial_backoff=args.initial_backoff,
                max_backoff=args.max_backoff,
            )
            state_entry = update_import_state_entry(
                state=import_state,
                state_path=state_path,
                knowledge_id=args.knowledge_id,
                file_path=file_path,
                status="added",
                file_id=file_id,
            )
            row["attempts"] = state_entry["attempts"]
            LOGGER.info("%s adicionado ao knowledge", file_path.name)
            imported += 1
            imported_files.append(file_path.name)
            row["status"] = "imported"
        except Exception as exc:  # noqa: BLE001
            failed += 1
            failed_files.append(file_path.name)
            row["error"] = str(exc)
            state_entry = update_import_state_entry(
                state=import_state,
                state_path=state_path,
                knowledge_id=args.knowledge_id,
                file_path=file_path,
                status="failed",
                file_id=str(row.get("file_id", "")),
                error=str(exc),
            )
            row["attempts"] = state_entry["attempts"]
            LOGGER.error("erro ao importar %s: %s", file_path.name, exc)
        row["duration_seconds"] = round(time.monotonic() - file_started_monotonic, 3)
        rows.append(row)
        LOGGER.info(
            "%s finalizado com status=%s em %.3fs",
            file_path.name,
            row["status"],
            row["duration_seconds"],
        )

    finished_at_utc = utc_timestamp()
    import_summary = build_import_summary(
        executed_at_utc=ts,
        finished_at_utc=finished_at_utc,
        duration_seconds=time.monotonic() - run_started_monotonic,
        base_url=base_url,
        knowledge_id=args.knowledge_id,
        pattern=args.pattern,
        start_from=args.start_from,
        limit=args.limit,
        total_matched_files=len(matched_file_paths),
        skipped_by_start_from=skipped_by_start_from,
        selected_files=file_paths,
        rows=rows,
        summary_path=summary_path,
        state_path=state_path,
        resume=args.resume,
        dry_run=args.dry_run,
    )
    write_import_summary(summary_path, import_summary)

    LOGGER.info(
        "Resumo: importados=%s falharam=%s pulados=%s dry_run=%s",
        imported,
        failed,
        skipped,
        dry_run_count,
    )
    if imported_files:
        LOGGER.info("arquivos importados com sucesso:")
        for name in imported_files:
            LOGGER.info("- %s", name)
    if failed_files:
        LOGGER.error("arquivos que falharam:")
        for name in failed_files:
            LOGGER.error("- %s", name)
    if skipped_files:
        LOGGER.info("arquivos pulados por resume:")
        for name in skipped_files:
            LOGGER.info("- %s", name)
    LOGGER.info("Resumo da importacao salvo em: %s", summary_path)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

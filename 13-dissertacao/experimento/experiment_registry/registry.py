"""Operações do registro persistente de experimentos."""

from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid
from pathlib import Path
from typing import Any, Mapping


def canonical_json(value: Mapping[str, Any]) -> str:
    """Serializa configurações de forma estável para hashing e auditoria."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def create_run(connection: sqlite3.Connection, name: str, configuration: Mapping[str, Any]) -> str:
    """Persiste a configuração e cria uma execução no estado `created`."""
    if not name.strip():
        raise ValueError("name é obrigatório")
    if not configuration:
        raise ValueError("configuration é obrigatório")
    serialized = canonical_json(configuration)
    configuration_hash = sha256_text(serialized)
    run_id = str(uuid.uuid4())
    with connection:
        connection.execute(
            "INSERT OR IGNORE INTO configurations(configuration_hash, configuration_json) VALUES (?, ?)",
            (configuration_hash, serialized),
        )
        connection.execute(
            "INSERT INTO experiment_runs(run_id, name, configuration_hash) VALUES (?, ?, ?)",
            (run_id, name.strip(), configuration_hash),
        )
    return run_id


def get_run(connection: sqlite3.Connection, run_id: str) -> dict[str, Any] | None:
    row = connection.execute(
        "SELECT run_id, name, state, configuration_hash, started_at, finished_at "
        "FROM experiment_runs WHERE run_id = ?", (run_id,)
    ).fetchone()
    if row is None:
        return None
    result = dict(row)
    result["artifacts"] = [
        dict(item)
        for item in connection.execute(
            "SELECT artifact_id, artifact_type, path, sha256, created_at "
            "FROM artifacts WHERE run_id = ? ORDER BY created_at, artifact_id", (run_id,)
        )
    ]
    return result


def list_runs(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = connection.execute(
        "SELECT run_id, name, state, configuration_hash, started_at, finished_at "
        "FROM experiment_runs ORDER BY started_at, run_id"
    ).fetchall()
    return [dict(row) for row in rows]


def register_artifact(
    connection: sqlite3.Connection,
    run_id: str,
    artifact_type: str,
    path: str | Path,
) -> str:
    """Registra um arquivo existente e seu hash, recusando associações inválidas."""
    if connection.execute("SELECT 1 FROM experiment_runs WHERE run_id = ?", (run_id,)).fetchone() is None:
        raise ValueError(f"execução inexistente: {run_id}")
    artifact_path = Path(path).expanduser().resolve()
    if not artifact_path.is_file():
        raise FileNotFoundError(artifact_path)
    artifact_id = str(uuid.uuid4())
    with connection:
        connection.execute(
            "INSERT INTO artifacts(artifact_id, run_id, artifact_type, path, sha256) VALUES (?, ?, ?, ?, ?)",
            (artifact_id, run_id, artifact_type, str(artifact_path), sha256_file(artifact_path)),
        )
    return artifact_id


def validate_run(connection: sqlite3.Connection, run_id: str) -> dict[str, Any]:
    """Compara hashes registrados com os arquivos atuais."""
    run = get_run(connection, run_id)
    if run is None:
        raise ValueError(f"execução inexistente: {run_id}")
    config = connection.execute(
        "SELECT configuration_json, configuration_hash FROM configurations WHERE configuration_hash = ?",
        (run["configuration_hash"],),
    ).fetchone()
    config_ok = config is not None and sha256_text(config["configuration_json"]) == config["configuration_hash"]
    artifacts = []
    for artifact in run["artifacts"]:
        path = Path(artifact["path"])
        exists = path.is_file()
        current_hash = sha256_file(path) if exists else None
        artifacts.append({
            "artifact_id": artifact["artifact_id"],
            "path": str(path),
            "exists": exists,
            "registered_sha256": artifact["sha256"],
            "current_sha256": current_hash,
            "ok": exists and current_hash == artifact["sha256"],
        })
    return {"run_id": run_id, "configuration_ok": config_ok, "artifacts": artifacts,
            "ok": config_ok and all(item["ok"] for item in artifacts)}

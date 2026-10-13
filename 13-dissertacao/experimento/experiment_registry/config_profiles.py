"""Perfis de configuração gerenciados pela interface."""
from __future__ import annotations

import json
import uuid
from typing import Any, Mapping

from .registry import canonical_json, sha256_text


def save_profile(connection, name: str, configuration: Mapping[str, Any], profile_id: str | None = None) -> str:
    name = name.strip()
    if not name:
        raise ValueError("o nome do perfil é obrigatório")
    if not isinstance(configuration, Mapping) or not configuration:
        raise ValueError("a configuração deve ser um objeto JSON não vazio")
    serialized = canonical_json(configuration)
    profile_id = profile_id or str(uuid.uuid4())
    with connection:
        connection.execute(
            "INSERT INTO configuration_profiles(profile_id,name,configuration_json,configuration_hash) VALUES (?,?,?,?) "
            "ON CONFLICT(name) DO UPDATE SET configuration_json=excluded.configuration_json, "
            "configuration_hash=excluded.configuration_hash, updated_at=CURRENT_TIMESTAMP",
            (profile_id, name, serialized, sha256_text(serialized)),
        )
        row = connection.execute("SELECT profile_id FROM configuration_profiles WHERE name=?", (name,)).fetchone()
    return str(row["profile_id"])


def list_profiles(connection) -> list[dict[str, Any]]:
    return [dict(row) for row in connection.execute(
        "SELECT profile_id,name,configuration_json,configuration_hash,created_at,updated_at "
        "FROM configuration_profiles ORDER BY name"
    )]


def get_profile(connection, profile_id: str) -> dict[str, Any] | None:
    row = connection.execute("SELECT * FROM configuration_profiles WHERE profile_id=?", (profile_id,)).fetchone()
    if row is None:
        return None
    result = dict(row)
    result["configuration"] = json.loads(result["configuration_json"])
    return result

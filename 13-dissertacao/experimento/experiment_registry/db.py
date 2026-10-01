"""Conexão e aplicação das migrações do registro SQLite."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterator

from .config import ExperimentPaths


SCHEMA_VERSION_TABLE = "schema_migrations"


def connect(database: str | Path) -> sqlite3.Connection:
    """Abre uma conexão SQLite com integridade referencial ativada."""
    connection = sqlite3.connect(str(database))
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def _migration_files(directory: Path) -> Iterator[Path]:
    yield from sorted(directory.glob("[0-9][0-9][0-9]_*.sql"))


def initialize_database(paths: ExperimentPaths) -> Path:
    """Cria diretórios, aplica migrações pendentes e retorna o banco."""
    paths.ensure_directories()
    with connect(paths.database) as connection:
        connection.execute(
            f"CREATE TABLE IF NOT EXISTS {SCHEMA_VERSION_TABLE} ("
            "version INTEGER PRIMARY KEY, filename TEXT NOT NULL, applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)"
        )
        applied = {
            row["version"]
            for row in connection.execute(
                f"SELECT version FROM {SCHEMA_VERSION_TABLE}"
            )
        }
        for migration in _migration_files(paths.migrations):
            version = int(migration.name.split("_", 1)[0])
            if version in applied:
                continue
            connection.executescript(migration.read_text(encoding="utf-8"))
            connection.execute(
                f"INSERT INTO {SCHEMA_VERSION_TABLE}(version, filename) VALUES (?, ?)",
                (version, migration.name),
            )
    return paths.database

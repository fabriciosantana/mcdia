"""Caminhos locais do subprojeto experimental."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ExperimentPaths:
    """Layout de arquivos derivados do gerenciador de experimentos."""

    root: Path

    @classmethod
    def from_environment(cls, root: str | Path | None = None) -> "ExperimentPaths":
        base = Path(root or os.environ.get("EXPERIMENTO_ROOT", Path.cwd()))
        return cls(base.expanduser().resolve())

    @property
    def database(self) -> Path:
        return self.root / "data" / "experiment_registry.sqlite3"

    @property
    def artifacts(self) -> Path:
        return self.root / "data" / "artifacts"

    @property
    def outputs(self) -> Path:
        return self.root / "data" / "outputs"

    @property
    def migrations(self) -> Path:
        return Path(__file__).resolve().parent / "migrations"

    def ensure_directories(self) -> None:
        self.database.parent.mkdir(parents=True, exist_ok=True)
        self.artifacts.mkdir(parents=True, exist_ok=True)
        self.outputs.mkdir(parents=True, exist_ok=True)

#!/usr/bin/env python3
"""Inicializa o banco local do registro de experimentos."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from experiment_registry.cli import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())

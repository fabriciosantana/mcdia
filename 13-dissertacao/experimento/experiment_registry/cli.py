"""Comandos de manutenção do registro experimental."""

from __future__ import annotations

import argparse
from pathlib import Path

from .config import ExperimentPaths
from .db import initialize_database


def main() -> int:
    parser = argparse.ArgumentParser(description="Gerencia o registro experimental local.")
    parser.add_argument("command", choices=("init",), help="comando a executar")
    parser.add_argument("--root", type=Path, help="raiz do subprojeto experimental")
    args = parser.parse_args()
    paths = ExperimentPaths.from_environment(args.root)
    database = initialize_database(paths)
    print(database)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

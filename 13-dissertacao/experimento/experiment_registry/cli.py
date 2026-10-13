"""Comandos de manutenção do registro experimental."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import ExperimentPaths
from .db import connect, initialize_database
from .registry import create_run, get_run, list_runs, register_artifact, validate_run
from .retrieval import run_retrieval
from .response_evaluation import ingest_jsonl, list_responses
from .openai_adapter import generate_responses


def _paths(root: Path | None) -> ExperimentPaths:
    paths = ExperimentPaths.from_environment(root)
    initialize_database(paths)
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(description="Gerencia o registro experimental local.")
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="cria o banco e aplica migrações")
    init.add_argument("--root", type=Path)
    demo = sub.add_parser("demo", help="cria uma execução sintética e produz um relatório JSON")
    demo.add_argument("--root", type=Path)
    demo.add_argument("--output", type=Path, help="arquivo JSON do relatório")
    ls = sub.add_parser("list", help="lista execuções")
    ls.add_argument("--root", type=Path)
    show = sub.add_parser("show", help="exibe uma execução")
    show.add_argument("run_id")
    show.add_argument("--root", type=Path)
    validate = sub.add_parser("validate", help="valida hashes de uma execução")
    validate.add_argument("run_id")
    validate.add_argument("--root", type=Path)
    retrieval = sub.add_parser("run-retrieval", help="executa um baseline de recuperação")
    retrieval.add_argument("--documents", type=Path, required=True)
    retrieval.add_argument("--questions", type=Path, required=True)
    retrieval.add_argument("--method", choices=("bm25", "tfidf", "hybrid"), default="bm25")
    retrieval.add_argument("--name", default="retrieval-run")
    retrieval.add_argument("--root", type=Path)
    ingest = sub.add_parser("ingest-responses", help="ingere respostas JSONL")
    ingest.add_argument("input", type=Path)
    ingest.add_argument("--root", type=Path)
    responses = sub.add_parser("responses", help="lista respostas de uma execução")
    responses.add_argument("run_id")
    responses.add_argument("--root", type=Path)
    generate = sub.add_parser("generate-responses", help="gera respostas via OpenAI")
    generate.add_argument("run_id")
    generate.add_argument("--documents", type=Path, required=True)
    generate.add_argument("--model")
    generate.add_argument("--root", type=Path)
    args = parser.parse_args()
    paths = _paths(args.root)
    if args.command == "init":
        print(paths.database)
        return 0
    if args.command == "run-retrieval":
        print(json.dumps(run_retrieval(paths, args.documents, args.questions, args.method, args.name), ensure_ascii=False, indent=2))
        return 0
    if args.command == "ingest-responses":
        with connect(paths.database) as connection: print(json.dumps({"ingested": ingest_jsonl(connection, args.input)}))
        return 0
    if args.command == "generate-responses":
        print(json.dumps(generate_responses(paths, args.run_id, args.documents, args.model), ensure_ascii=False, indent=2))
        return 0
    with connect(paths.database) as connection:
        if args.command == "demo":
            run_id = create_run(connection, "demo", {"retrieval": {"method": "bm25", "k": 5}})
            report = get_run(connection, run_id)
            output = args.output or (paths.outputs / "demo-run.json")
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(output)
        elif args.command == "list":
            print(json.dumps(list_runs(connection), ensure_ascii=False, indent=2))
        elif args.command == "show":
            result = get_run(connection, args.run_id)
            if result is None:
                parser.error(f"execução inexistente: {args.run_id}")
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif args.command == "validate":
            print(json.dumps(validate_run(connection, args.run_id), ensure_ascii=False, indent=2))
        elif args.command == "responses":
            print(json.dumps(list_responses(connection, args.run_id), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

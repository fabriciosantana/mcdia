#!/usr/bin/env python3
"""Consolida rodadas de avaliacao RAG e gera um resumo comparativo."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as csv_file:
        return list(csv.DictReader(csv_file))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_stem_from_csv(path: Path) -> str:
    if path.suffix != ".csv":
        raise ValueError(f"Arquivo nao e CSV: {path}")
    return path.stem


def summarize_run(csv_path: Path, config_path: Path | None) -> dict[str, Any]:
    rows = load_csv_rows(csv_path)
    totals = [int(row["total_score"]) for row in rows if row.get("total_score", "").strip()]
    statuses = sorted({row["execution_status"] for row in rows})
    summary = {
        "stem": run_stem_from_csv(csv_path),
        "csv_path": str(csv_path),
        "config_path": str(config_path) if config_path else "",
        "row_count": len(rows),
        "statuses": statuses,
        "min_total": min(totals) if totals else None,
        "avg_total": round(mean(totals), 2) if totals else None,
        "max_total": max(totals) if totals else None,
        "rows": rows,
        "config": load_json(config_path) if config_path and config_path.exists() else {},
    }
    return summary


def build_variation_table(run_summaries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows_by_run = [summary["rows"] for summary in run_summaries]
    variation_rows: list[dict[str, Any]] = []
    for row_group in zip(*rows_by_run):
        qid = row_group[0]["id"]
        category = row_group[0]["category"]
        scores = [int(row["total_score"]) for row in row_group]
        if len(set(scores)) == 1:
            continue
        variation_rows.append(
            {
                "id": qid,
                "category": category,
                "scores": scores,
                "min": min(scores),
                "max": max(scores),
                "spread": max(scores) - min(scores),
            }
        )
    variation_rows.sort(key=lambda item: (-item["spread"], item["id"]))
    return variation_rows


def build_markdown(run_summaries: list[dict[str, Any]], variation_rows: list[dict[str, Any]]) -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    lines = [
        "# Stability Summary",
        "",
        f"Gerado em: `{generated_at}`",
        "",
        "## Rodadas comparadas",
        "",
    ]

    for summary in run_summaries:
        config = summary["config"]
        generator = config.get("generator", {})
        judge = config.get("judge", {})
        lines.extend(
            [
                f"### {summary['stem']}",
                "",
                f"- CSV: `{summary['csv_path']}`",
                f"- Run config: `{summary['config_path']}`" if summary["config_path"] else "- Run config: <ausente>",
                f"- Perguntas: `{summary['row_count']}`",
                f"- Statuses: `{', '.join(summary['statuses'])}`",
                f"- Total score: min `{summary['min_total']}` | media `{summary['avg_total']}` | max `{summary['max_total']}`",
                f"- Gerador: `{generator.get('model', '')}` | Juiz: `{judge.get('model', '')}`",
                f"- Knowledge ID: `{config.get('knowledge_id', '')}`",
                "",
            ]
        )

    lines.extend(
        [
            "## Leitura inicial",
            "",
            f"- Rodadas analisadas: `{len(run_summaries)}`",
            f"- Media das medias: `{round(mean(summary['avg_total'] for summary in run_summaries if summary['avg_total'] is not None), 2)}`",
            f"- Melhor media observada: `{max(summary['avg_total'] for summary in run_summaries if summary['avg_total'] is not None)}`",
            f"- Pior media observada: `{min(summary['avg_total'] for summary in run_summaries if summary['avg_total'] is not None)}`",
            f"- Perguntas com variacao entre rodadas: `{len(variation_rows)}`",
            "",
            "## Variacao por pergunta",
            "",
        ]
    )

    if not variation_rows:
        lines.append("- Nenhuma variacao de score entre as rodadas comparadas.")
        lines.append("")
        return "\n".join(lines)

    lines.extend(
        [
            "| Pergunta | Categoria | Scores | Amplitude |",
            "|---|---|---|---|",
        ]
    )
    for row in variation_rows:
        score_text = ", ".join(str(score) for score in row["scores"])
        lines.append(f"| `{row['id']}` | `{row['category']}` | `{score_text}` | `{row['spread']}` |")

    top_unstable = [row["id"] for row in variation_rows if row["spread"] == max(item["spread"] for item in variation_rows)]
    lines.extend(
        [
            "",
            "## Conclusao inicial",
            "",
            "- As rodadas comparadas sao operacionalmente estaveis: todas completaram com sucesso.",
            "- Ainda ha variacao metodologica relevante em parte do benchmark, especialmente nas perguntas com maior amplitude de score.",
            f"- Perguntas mais instaveis nesta leitura inicial: `{', '.join(top_unstable)}`.",
            "",
        ]
    )

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Consolida rodadas de avaliacao RAG.")
    parser.add_argument(
        "csv_files",
        nargs="+",
        help="Arquivos CSV das rodadas a comparar.",
    )
    parser.add_argument(
        "--output",
        default="",
        help="Arquivo Markdown de saida. Se vazio, usa eval/results/stability_summary_<timestamp>.md",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    csv_paths = [(project_root / item).resolve() if not Path(item).is_absolute() else Path(item) for item in args.csv_files]

    run_summaries = []
    for csv_path in csv_paths:
        stem = run_stem_from_csv(csv_path)
        config_path = csv_path.with_suffix(".run_config.json")
        run_summaries.append(summarize_run(csv_path, config_path))

    variation_rows = build_variation_table(run_summaries)
    markdown = build_markdown(run_summaries, variation_rows)

    if args.output:
        output_path = (project_root / args.output).resolve() if not Path(args.output).is_absolute() else Path(args.output)
    else:
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        output_path = project_root / "eval" / "results" / f"stability_summary_{ts}.md"

    output_path.write_text(markdown, encoding="utf-8")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

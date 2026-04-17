#!/usr/bin/env python3
"""Gera um pacote Markdown para validacao manual amostral."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_jsonl_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as jsonl_file:
        for line in jsonl_file:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def build_markdown(
    rows: list[dict[str, Any]],
    selected_ids: list[str],
    source_jsonl: Path,
    source_csv: Path | None,
) -> str:
    row_map = {row["id"]: row for row in rows}
    selected_rows = [row_map[item] for item in selected_ids if item in row_map]

    lines = [
        "# Pacote de Validacao Manual Amostral",
        "",
        "## Objetivo",
        "",
        "Revisar manualmente uma amostra curta da bateria automatizada para comparar o julgamento humano com o julgamento automatico.",
        "",
        "## Rodada de origem",
        "",
        f"- JSONL: `{source_jsonl}`",
        f"- CSV: `{source_csv}`" if source_csv else "- CSV: <nao informado>",
        f"- Perguntas selecionadas: `{len(selected_rows)}`",
        "",
        "## Amostra recomendada",
        "",
        "- `q03`: caso forte de controle positivo",
        "- `q11`: comparacao com cobertura parcial na rodada base",
        "- `q14`: pergunta multi-hop com referencias apenas parciais",
        "- `q15`: item mais instavel entre as rodadas identicas",
        "- `q16`: risco de extrapolacao alem do contexto",
        "- `q18`: risco de confusao entre autores",
        "- `q20`: controle de alucinacao e cautela metodologica",
        "",
        "## Instrucoes de revisao",
        "",
        "Para cada pergunta, registrar:",
        "",
        "- classificacao humana: `adequada`, `parcialmente adequada` ou `inadequada`",
        "- fidelidade ao contexto: `alta`, `media` ou `baixa`",
        "- uso de referencias: `correto`, `parcial` ou `ausente`",
        "- principal problema observado, se houver",
        "- observacao sobre convergencia ou divergencia em relacao ao juiz automatico",
        "",
        "## Ficha por pergunta",
        "",
    ]

    for row in selected_rows:
        lines.extend(
            [
                f"### {row['id']} - {row.get('category', '')}",
                "",
                f"**Pergunta**: {row.get('question', '')}",
                "",
                f"**Status automatico**: `{row.get('status', '')}`",
                "",
                (
                    "**Notas automaticas**: "
                    f"aderencia=`{row.get('adherence_score', '')}` | "
                    f"factual=`{row.get('factual_score', '')}` | "
                    f"fontes=`{row.get('source_focus_score', '')}` | "
                    f"sintese=`{row.get('synthesis_score', '')}` | "
                    f"confianca=`{row.get('hallucination_score', '')}` | "
                    f"total=`{row.get('total_score', '')}`"
                ),
                "",
                f"**Review notes do juiz**: {row.get('review_notes', '') or '<vazio>'}",
                "",
                "**Resposta gerada**:",
                "",
                row.get("answer", "").strip() or "<vazio>",
                "",
                "**Preenchimento humano**:",
                "",
                "- Classificacao humana: ",
                "- Fidelidade ao contexto: ",
                "- Uso de referencias: ",
                "- Principal problema observado: ",
                "- Convergencia/divergencia em relacao ao juiz automatico: ",
                "",
                "---",
                "",
            ]
        )

    lines.extend(
        [
            "## Sintese final",
            "",
            "- Concordancia geral humano x juiz automatico: ",
            "- Perguntas com maior divergencia: ",
            "- Leitura metodologica curta: ",
            "",
        ]
    )

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Gera um pacote Markdown para validacao manual amostral.")
    parser.add_argument("jsonl_file", help="Arquivo JSONL da rodada.")
    parser.add_argument(
        "--questions",
        nargs="+",
        default=["q03", "q11", "q14", "q15", "q16", "q18", "q20"],
        help="Lista de IDs de perguntas a incluir na amostra.",
    )
    parser.add_argument(
        "--output",
        default="",
        help="Arquivo Markdown de saida. Default: <stem>.manual_validation_sample.md no mesmo diretorio do JSONL.",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    jsonl_path = (project_root / args.jsonl_file).resolve() if not Path(args.jsonl_file).is_absolute() else Path(args.jsonl_file)
    csv_path = jsonl_path.with_suffix(".csv")
    rows = load_jsonl_rows(jsonl_path)

    if args.output:
        output_path = (project_root / args.output).resolve() if not Path(args.output).is_absolute() else Path(args.output)
    else:
        output_path = jsonl_path.parent / f"{jsonl_path.stem}.manual_validation_sample.md"

    markdown = build_markdown(
        rows=rows,
        selected_ids=args.questions,
        source_jsonl=jsonl_path,
        source_csv=csv_path if csv_path.exists() else None,
    )
    output_path.write_text(markdown, encoding="utf-8")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

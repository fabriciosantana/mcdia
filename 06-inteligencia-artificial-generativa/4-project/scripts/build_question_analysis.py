#!/usr/bin/env python3
"""Gera uma leitura analitica sintetica por pergunta a partir do JSONL da avaliacao."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


QUESTION_CODE_RE = re.compile(r"\[(\d{6}-\d{3})\]")
URL_RE = re.compile(r"https?://\S+")


def load_jsonl_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as jsonl_file:
        for line in jsonl_file:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def as_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def extract_source_stats(response: Any) -> dict[str, Any]:
    if not isinstance(response, dict):
        return {
            "source_entries": 0,
            "retrieved_chunks": 0,
            "unique_files": 0,
            "score_count": 0,
            "avg_retrieval_score": None,
        }

    source_entries = 0
    retrieved_chunks = 0
    files: set[str] = set()
    scores: list[float] = []

    for source in response.get("sources", []):
        if not isinstance(source, dict):
            continue
        source_entries += 1
        document = source.get("document")
        if isinstance(document, list):
            retrieved_chunks += len(document)
        metadata = source.get("metadata")
        if isinstance(metadata, list):
            for item in metadata:
                if not isinstance(item, dict):
                    continue
                file_id = item.get("file_id")
                if file_id:
                    files.add(str(file_id))
                score = item.get("score")
                if isinstance(score, (int, float)):
                    scores.append(float(score))
        elif isinstance(metadata, dict):
            file_id = metadata.get("file_id")
            if file_id:
                files.add(str(file_id))
            score = metadata.get("score")
            if isinstance(score, (int, float)):
                scores.append(float(score))

    avg_score = round(sum(scores) / len(scores), 4) if scores else None
    return {
        "source_entries": source_entries,
        "retrieved_chunks": retrieved_chunks,
        "unique_files": len(files),
        "score_count": len(scores),
        "avg_retrieval_score": avg_score,
    }


def classify_retrieval_quality(row: dict[str, Any], stats: dict[str, Any]) -> str:
    if row.get("status") != "ok" or stats["retrieved_chunks"] == 0:
        return "baixa"

    source_focus = as_int(row.get("source_focus_score"))
    unique_files = stats["unique_files"]
    retrieved_chunks = stats["retrieved_chunks"]

    if source_focus == 2 and unique_files >= 5 and retrieved_chunks >= 8:
        return "alta"
    if (source_focus is not None and source_focus >= 1) or unique_files >= 3:
        return "media"
    return "baixa"


def classify_context_faithfulness(row: dict[str, Any]) -> str:
    if row.get("status") != "ok":
        return "baixa"

    factual = as_int(row.get("factual_score"))
    hallucination = as_int(row.get("hallucination_score"))
    adherence = as_int(row.get("adherence_score"))

    if factual == 2 and hallucination == 2 and adherence == 2:
        return "alta"
    if all(score is not None and score >= 1 for score in (factual, hallucination, adherence)):
        return "media"
    return "baixa"


def classify_reference_use(row: dict[str, Any]) -> str:
    if row.get("status") != "ok":
        return "ausente"

    answer = str(row.get("answer", ""))
    source_focus = as_int(row.get("source_focus_score")) or 0
    code_count = len(QUESTION_CODE_RE.findall(answer))
    url_count = len(URL_RE.findall(answer))
    has_date_marker = "Data:" in answer
    has_link_marker = "Link:" in answer
    has_citation_section = "Citações:" in answer or "Citacoes:" in answer

    if source_focus >= 2 and (code_count >= 1 or url_count >= 1 or has_date_marker or has_link_marker):
        return "correta"
    if has_citation_section or code_count >= 1 or url_count >= 1 or source_focus >= 1:
        return "parcial"
    return "ausente"


def infer_main_limitation(row: dict[str, Any]) -> str:
    if row.get("status") != "ok":
        return str(row.get("status", "falha de execucao"))

    notes = str(row.get("review_notes", "")).strip()
    notes_lower = notes.lower()

    keyword_rules = [
        ("nao atende totalmente", "cobertura incompleta da pergunta"),
        ("não atende totalmente", "cobertura incompleta da pergunta"),
        ("nao fornece comparacao", "comparacao incompleta"),
        ("não fornece comparação", "comparacao incompleta"),
        ("foca apenas", "foco excessivamente estreito"),
        ("risco de imprecis", "necessidade de checagem factual"),
        ("duvidosa", "necessidade de checagem factual"),
        ("duvidosas", "necessidade de checagem factual"),
        ("checagem", "necessidade de checagem factual"),
        ("verificacao", "necessidade de checagem factual"),
        ("verificação", "necessidade de checagem factual"),
        ("nao encontrei", "contexto insuficiente para sustentar toda a resposta"),
        ("não encontrei", "contexto insuficiente para sustentar toda a resposta"),
        ("nao foi possivel", "contexto insuficiente para sustentar toda a resposta"),
        ("não foi possível", "contexto insuficiente para sustentar toda a resposta"),
        ("limitacoes", "limitacoes do proprio contexto"),
        ("limitações", "limitacoes do proprio contexto"),
        ("extrapola", "risco de extrapolacao"),
        ("cautela", "demanda resposta mais cautelosa"),
    ]
    for needle, label in keyword_rules:
        if needle in notes_lower:
            return label

    total = as_int(row.get("total_score"))
    if total == 10:
        return "nenhum limite relevante observado"
    if notes:
        first_sentence = notes.split(".")[0].strip()
        return first_sentence[:160]
    return "sem limite sintetizado"


def build_short_note(
    row: dict[str, Any],
    retrieval_quality: str,
    context_faithfulness: str,
    reference_use: str,
    main_limitation: str,
    stats: dict[str, Any],
) -> str:
    parts = [
        f"Recuperacao {retrieval_quality}",
        f"fidelidade {context_faithfulness}",
        f"referencias {reference_use}",
    ]
    if stats["retrieved_chunks"]:
        parts.append(
            f"{stats['retrieved_chunks']} chunks de {stats['unique_files']} arquivos"
        )
    return "; ".join(parts) + f". Limite principal: {main_limitation}."


def analyze_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    analyses: list[dict[str, Any]] = []
    for row in rows:
        stats = extract_source_stats(row.get("response"))
        retrieval_quality = classify_retrieval_quality(row, stats)
        context_faithfulness = classify_context_faithfulness(row)
        reference_use = classify_reference_use(row)
        main_limitation = infer_main_limitation(row)
        analyses.append(
            {
                "id": row["id"],
                "category": row.get("category", ""),
                "question": row.get("question", ""),
                "execution_status": row.get("status", ""),
                "total_score": row.get("total_score", ""),
                "retrieval_quality": retrieval_quality,
                "context_faithfulness": context_faithfulness,
                "reference_use": reference_use,
                "main_limitation": main_limitation,
                "source_entries": stats["source_entries"],
                "retrieved_chunks": stats["retrieved_chunks"],
                "unique_files": stats["unique_files"],
                "avg_retrieval_score": stats["avg_retrieval_score"] if stats["avg_retrieval_score"] is not None else "",
                "review_notes": row.get("review_notes", ""),
                "short_analytical_note": build_short_note(
                    row=row,
                    retrieval_quality=retrieval_quality,
                    context_faithfulness=context_faithfulness,
                    reference_use=reference_use,
                    main_limitation=main_limitation,
                    stats=stats,
                ),
            }
        )
    return analyses


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "id",
        "category",
        "question",
        "execution_status",
        "total_score",
        "retrieval_quality",
        "context_faithfulness",
        "reference_use",
        "main_limitation",
        "source_entries",
        "retrieved_chunks",
        "unique_files",
        "avg_retrieval_score",
        "review_notes",
        "short_analytical_note",
    ]
    with path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, Any]], source_jsonl: Path) -> None:
    retrieval_counter = Counter(row["retrieval_quality"] for row in rows)
    faithfulness_counter = Counter(row["context_faithfulness"] for row in rows)
    reference_counter = Counter(row["reference_use"] for row in rows)

    lines = [
        "# Question Analysis",
        "",
        f"Fonte: `{source_jsonl}`",
        "",
        "## Resumo",
        "",
        f"- Perguntas analisadas: `{len(rows)}`",
        f"- Recuperacao: `alta={retrieval_counter.get('alta', 0)}`, `media={retrieval_counter.get('media', 0)}`, `baixa={retrieval_counter.get('baixa', 0)}`",
        f"- Fidelidade ao contexto: `alta={faithfulness_counter.get('alta', 0)}`, `media={faithfulness_counter.get('media', 0)}`, `baixa={faithfulness_counter.get('baixa', 0)}`",
        f"- Referencias: `correta={reference_counter.get('correta', 0)}`, `parcial={reference_counter.get('parcial', 0)}`, `ausente={reference_counter.get('ausente', 0)}`",
        "",
        "## Matriz curta por pergunta",
        "",
        "| Pergunta | Categoria | Recuperacao | Fidelidade | Referencias | Limite principal |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['id']}` | `{row['category']}` | `{row['retrieval_quality']}` | "
            f"`{row['context_faithfulness']}` | `{row['reference_use']}` | {row['main_limitation']} |"
        )

    lines.extend(["", "## Notas sintéticas", ""])
    for row in rows:
        lines.append(f"### {row['id']} - {row['category']}")
        lines.append("")
        lines.append(f"- Pergunta: {row['question']}")
        lines.append(f"- Nota total: `{row['total_score']}` | Status: `{row['execution_status']}`")
        lines.append(
            f"- Sinais de retrieval: `{row['retrieved_chunks']}` chunks, `{row['unique_files']}` arquivos, "
            f"`{row['source_entries']}` entradas de source"
        )
        lines.append(f"- Leitura curta: {row['short_analytical_note']}")
        if row["review_notes"]:
            lines.append(f"- Review notes: {row['review_notes']}")
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Gera leitura analitica sintetica por pergunta.")
    parser.add_argument("jsonl_file", help="Arquivo JSONL da rodada de avaliacao.")
    parser.add_argument(
        "--output-prefix",
        default="",
        help="Prefixo dos arquivos de saida. Default: usa o stem do JSONL dentro de eval/results.",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    jsonl_path = (project_root / args.jsonl_file).resolve() if not Path(args.jsonl_file).is_absolute() else Path(args.jsonl_file)
    rows = load_jsonl_rows(jsonl_path)
    analyses = analyze_rows(rows)

    if args.output_prefix:
        output_prefix = (
            (project_root / args.output_prefix).resolve()
            if not Path(args.output_prefix).is_absolute()
            else Path(args.output_prefix)
        )
    else:
        output_prefix = jsonl_path.parent / f"{jsonl_path.stem}.question_analysis"

    csv_path = output_prefix.parent / f"{output_prefix.name}.csv"
    md_path = output_prefix.parent / f"{output_prefix.name}.md"
    write_csv(csv_path, analyses)
    write_markdown(md_path, analyses, jsonl_path)
    print(csv_path)
    print(md_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

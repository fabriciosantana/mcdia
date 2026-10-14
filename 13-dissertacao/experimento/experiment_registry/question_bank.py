"""Catálogo persistente e curadoria de perguntas no SQLite."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable


def _json(value: Any, default: Any) -> str:
    if value is None or value == "":
        value = default
    if isinstance(value, str):
        if value.startswith("[") or value.startswith("{"):
            try:
                json.loads(value)
                return value
            except json.JSONDecodeError:
                pass
        value = [item.strip() for item in value.split(";") if item.strip()]
    return json.dumps(value, ensure_ascii=False)


def _list(value: Any) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return [str(item) for item in parsed]
        except json.JSONDecodeError:
            pass
        return [item.strip() for item in value.split(";") if item.strip()]
    return [str(item) for item in value]


def _row(row) -> dict[str, Any]:
    result = dict(row)
    for field in ("secondary_categories_json", "expected_authors_json", "reference_doc_ids_json", "reference_chunk_ids_json", "relevance_judgments_json"):
        result[field.removesuffix("_json")] = json.loads(result.pop(field) or ("{}" if "judgments" in field else "[]"))
    result["respondible"] = bool(result["respondible"])
    return result


def list_catalog(connection, status: str | None = None) -> list[dict[str, Any]]:
    if status:
        rows = connection.execute("SELECT * FROM question_catalog WHERE status=? ORDER BY question_id", (status,))
    else:
        rows = connection.execute("SELECT * FROM question_catalog WHERE status <> 'arquivada' ORDER BY question_id")
    return [_row(row) for row in rows]


def get_catalog_question(connection, question_id: str) -> dict[str, Any] | None:
    row = connection.execute("SELECT * FROM question_catalog WHERE question_id=?", (question_id,)).fetchone()
    return _row(row) if row else None


def save_catalog_question(connection, question: dict[str, Any]) -> str:
    question_id = str(question.get("question_id", "")).strip()
    query = str(question.get("query", "")).strip()
    category = str(question.get("category", "")).strip()
    status = str(question.get("status", "rascunho")).strip().lower()
    if not question_id or not query or not category:
        raise ValueError("question_id, pergunta e categoria são obrigatórios")
    if status not in {"rascunho", "revisar", "validada", "arquivada"}:
        raise ValueError("status de pergunta inválido")
    with connection:
        connection.execute(
            """INSERT INTO question_catalog(
                question_id,source_question_id,query,category,source_category,secondary_categories_json,
                difficulty,answerability,respondible,expected_authors_json,reference_doc_ids_json,
                reference_chunk_ids_json,relevance_judgments_json,expected_answer_criteria,evaluation_risks,
                status,curation_notes,source_file
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(question_id) DO UPDATE SET source_question_id=excluded.source_question_id,
                query=excluded.query,category=excluded.category,source_category=excluded.source_category,
                secondary_categories_json=excluded.secondary_categories_json,difficulty=excluded.difficulty,
                answerability=excluded.answerability,respondible=excluded.respondible,
                expected_authors_json=excluded.expected_authors_json,reference_doc_ids_json=excluded.reference_doc_ids_json,
                reference_chunk_ids_json=excluded.reference_chunk_ids_json,relevance_judgments_json=excluded.relevance_judgments_json,
                expected_answer_criteria=excluded.expected_answer_criteria,evaluation_risks=excluded.evaluation_risks,
                status=excluded.status,curation_notes=excluded.curation_notes,source_file=excluded.source_file,
                updated_at=CURRENT_TIMESTAMP""",
            (question_id, question.get("source_question_id"), query, category, question.get("source_category"), _json(question.get("secondary_categories"), []),
             question.get("difficulty"), question.get("answerability"), int(bool(question.get("respondible", True))), _json(question.get("expected_authors"), []), _json(question.get("reference_doc_ids"), []),
             _json(question.get("reference_chunk_ids"), []), _json(question.get("relevance_judgments"), {}), question.get("expected_answer_criteria"), question.get("evaluation_risks"), status,
             question.get("curation_notes"), question.get("source_file")),
        )
    return question_id


def seed_question_catalog(connection, source: str | Path, overwrite: bool = False) -> int:
    """Importa uma vez o catálogo derivado; a operação normal passa a ser SQLite."""
    path = Path(source)
    records = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise ValueError("o arquivo inicial de perguntas deve conter uma lista JSON")
    if overwrite:
        with connection:
            connection.execute("DELETE FROM question_catalog")
    inserted = 0
    for record in records:
        if not get_catalog_question(connection, record.get("question_id", "")):
            save_catalog_question(connection, record)
            inserted += 1
    return inserted


def catalog_questions_for_run(connection, question_ids: Iterable[str] | None = None) -> list[dict[str, Any]]:
    params: list[str] = []
    query = "SELECT * FROM question_catalog WHERE status='validada'"
    if question_ids is not None:
        ids = [str(item) for item in question_ids]
        if not ids:
            return []
        query += " AND question_id IN (" + ",".join("?" for _ in ids) + ")"
        params.extend(ids)
    query += " ORDER BY question_id"
    return [_row(row) for row in connection.execute(query, params)]

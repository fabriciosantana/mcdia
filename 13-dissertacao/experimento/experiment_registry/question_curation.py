"""Curadoria das perguntas e do conjunto de referência."""
from __future__ import annotations

import json


STATUSES = {"rascunho", "revisar", "validada", "validated"}


def save_question_metadata(connection, run_id: str, question_id: str, category: str, status: str, reference_chunks: list[str], judgments: dict[str, int], notes: str = "") -> None:
    if status not in STATUSES:
        raise ValueError(f"status inválido: {status}")
    if connection.execute("SELECT 1 FROM questions WHERE run_id=? AND question_id=?", (run_id, question_id)).fetchone() is None:
        raise ValueError("pergunta inexistente")
    if any(value not in (0, 1, 2) for value in judgments.values()):
        raise ValueError("grau de relevância deve estar entre 0 e 2")
    with connection:
        connection.execute(
            "INSERT INTO question_metadata(run_id,question_id,category,validation_status,curation_notes,reference_chunks_json,relevance_judgments_json) VALUES (?,?,?,?,?,?,?) "
            "ON CONFLICT(run_id,question_id) DO UPDATE SET category=excluded.category, validation_status=excluded.validation_status, curation_notes=excluded.curation_notes, reference_chunks_json=excluded.reference_chunks_json, relevance_judgments_json=excluded.relevance_judgments_json",
            (run_id, question_id, category.strip() or None, status, notes, json.dumps(reference_chunks, ensure_ascii=False), json.dumps(judgments, ensure_ascii=False)),
        )


def get_question_metadata(connection, run_id: str, question_id: str) -> dict:
    row = connection.execute("SELECT category,validation_status,curation_notes,reference_chunks_json,relevance_judgments_json FROM question_metadata WHERE run_id=? AND question_id=?", (run_id, question_id)).fetchone()
    if row is None:
        return {"category": None, "validation_status": "validated", "curation_notes": "", "reference_chunks": [], "judgments": {}}
    return {"category": row["category"], "validation_status": row["validation_status"], "curation_notes": row["curation_notes"] or "", "reference_chunks": json.loads(row["reference_chunks_json"]), "judgments": json.loads(row["relevance_judgments_json"])}

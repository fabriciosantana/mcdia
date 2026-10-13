"""Julgamento automatizado e comparação transparente com avaliações humanas."""
from __future__ import annotations

import json
import uuid
from typing import Any

FIELDS = ("factual_correctness", "context_adherence", "citation_support", "proportional_completeness", "insufficiency_recognition")


def record_automated_evaluation(connection, response_id: str, model: str, scores: dict[str, int], prompt_hash: str | None = None, notes: str = "") -> str:
    if connection.execute("SELECT 1 FROM responses WHERE response_id=?", (response_id,)).fetchone() is None:
        raise ValueError(f"resposta inexistente: {response_id}")
    values = []
    for field in FIELDS:
        value = scores.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or value not in (0, 1, 2):
            raise ValueError(f"nota inválida: {field}")
        values.append(value)
    evaluation_id = str(uuid.uuid4())
    with connection:
        connection.execute(
            "INSERT INTO automated_evaluations(evaluation_id,response_id,evaluator_model,prompt_hash,factual_correctness,context_adherence,citation_support,proportional_completeness,insufficiency_recognition,notes) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (evaluation_id, response_id, model, prompt_hash, *values, notes),
        )
    return evaluation_id


def _weighted_kappa(human: list[int], automated: list[int]) -> float | None:
    if not human or len(human) != len(automated):
        return None
    categories = (0, 1, 2)
    observed = sum(1 - abs(a - b) / 2 for a, b in zip(human, automated)) / len(human)
    human_mean = {c: human.count(c) / len(human) for c in categories}
    auto_mean = {c: automated.count(c) / len(automated) for c in categories}
    expected = sum(human_mean[a] * auto_mean[b] * (1 - abs(a - b) / 2) for a in categories for b in categories)
    return (observed - expected) / (1 - expected) if expected < 1 else 1.0


def agreement_report(connection, run_id: str) -> dict[str, Any]:
    rows = connection.execute(
        "SELECT h.response_id, h.factual_correctness, h.context_adherence, h.citation_support, h.proportional_completeness, h.insufficiency_recognition, "
        "a.factual_correctness AS af, a.context_adherence AS ac, a.citation_support AS asup, a.proportional_completeness AS ap, a.insufficiency_recognition AS ai "
        "FROM human_evaluations h JOIN responses r ON r.response_id=h.response_id JOIN automated_evaluations a ON a.response_id=h.response_id WHERE r.run_id=?",
        (run_id,),
    ).fetchall()
    dimensions = {}
    aliases = dict(zip(FIELDS, ("factual_correctness", "context_adherence", "citation_support", "proportional_completeness", "insufficiency_recognition")))
    auto_aliases = dict(zip(FIELDS, ("af", "ac", "asup", "ap", "ai")))
    for field in FIELDS:
        pairs = [(row[field], row[auto_aliases[field]]) for row in rows if row[field] is not None and row[auto_aliases[field]] is not None]
        dimensions[field] = {"n": len(pairs), "exact_agreement": (sum(a == b for a, b in pairs) / len(pairs) if pairs else None), "weighted_kappa": _weighted_kappa([a for a, _ in pairs], [b for _, b in pairs])}
    return {"run_id": run_id, "paired_responses": len(rows), "dimensions": dimensions}


def parse_judge_json(text: str) -> dict[str, Any]:
    """Valida a saída JSON do juiz sem aceitar texto parcial ou notas fora da escala."""
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError("saída do juiz não é JSON válido") from exc
    if not isinstance(value, dict) or any(field not in value for field in FIELDS):
        raise ValueError("saída do juiz deve conter as cinco dimensões")
    scores = {field: value[field] for field in FIELDS}
    for field, score in scores.items():
        if not isinstance(score, int) or score not in (0, 1, 2):
            raise ValueError(f"nota inválida no juiz: {field}")
    return {"scores": scores, "notes": str(value.get("notes", ""))}


def judge_response(connection, response_id: str, model: str, client=None) -> str:
    """Executa um juiz estruturado; o cliente pode ser substituído em testes."""
    row = connection.execute("SELECT answer, prompt_hash FROM responses WHERE response_id=?", (response_id,)).fetchone()
    if row is None:
        raise ValueError(f"resposta inexistente: {response_id}")
    if client is None:
        from dotenv import load_dotenv
        from openai import OpenAI
        load_dotenv(); client = OpenAI()
    prompt = (
        "Avalie a resposta RAG exclusivamente segundo a rubrica. Retorne somente JSON com "
        "factual_correctness, context_adherence, citation_support, proportional_completeness, "
        "insufficiency_recognition, cada um inteiro 0, 1 ou 2, e notes.\n\nResposta:\n" + row["answer"]
    )
    result = client.responses.create(model=model, input=prompt)
    parsed = parse_judge_json(result.output_text)
    return record_automated_evaluation(connection, response_id, model, parsed["scores"], prompt_hash=row["prompt_hash"], notes=parsed["notes"])

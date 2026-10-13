"""Análises estatísticas simples e registro de casos críticos."""
from __future__ import annotations

import random
import uuid
from typing import Iterable


def bootstrap_mean(values: Iterable[float], repetitions: int = 1000, seed: int = 42, confidence: float = 0.95) -> dict[str, float | int | None]:
    values = [float(value) for value in values]
    if not values:
        return {"n": 0, "mean": None, "lower": None, "upper": None, "seed": seed}
    rng = random.Random(seed); means = []
    for _ in range(repetitions):
        sample = [values[rng.randrange(len(values))] for _ in values]
        means.append(sum(sample) / len(sample))
    means.sort(); alpha = (1 - confidence) / 2
    low = means[max(0, int(alpha * len(means)))]
    high = means[min(len(means) - 1, int((1 - alpha) * len(means)))]
    return {"n": len(values), "mean": sum(values) / len(values), "lower": low, "upper": high, "seed": seed}


def record_error_case(connection, response_id: str, error_type: str, severity: str = "moderate", notes: str = "") -> str:
    if connection.execute("SELECT 1 FROM responses WHERE response_id=?", (response_id,)).fetchone() is None:
        raise ValueError("resposta inexistente")
    if severity not in {"low", "moderate", "high", "critical"}:
        raise ValueError("severidade inválida")
    error_id = str(uuid.uuid4())
    with connection:
        connection.execute("INSERT INTO error_cases(error_id,response_id,error_type,severity,notes) VALUES (?,?,?,?,?)", (error_id, response_id, error_type.strip(), severity, notes))
    return error_id


def list_error_cases(connection, response_id: str) -> list[dict]:
    return [dict(row) for row in connection.execute("SELECT * FROM error_cases WHERE response_id=? ORDER BY created_at,error_id", (response_id,))]

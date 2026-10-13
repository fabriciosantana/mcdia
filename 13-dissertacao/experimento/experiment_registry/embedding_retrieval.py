"""Recuperação densa opcional com embeddings persistíveis."""
from __future__ import annotations

import os
from typing import Any

import numpy as np


def _client(client=None):
    if client is not None:
        return client
    from dotenv import load_dotenv
    from openai import OpenAI
    load_dotenv()
    return OpenAI()


def embed(texts: list[str], model: str, client=None) -> np.ndarray:
    result = _client(client).embeddings.create(model=model, input=texts)
    data = sorted(result.data, key=lambda item: item.index)
    return np.asarray([item.embedding for item in data], dtype=np.float32)


def rank_dense(documents: list[dict[str, Any]], query: str, model: str | None = None, client=None) -> list[dict[str, Any]]:
    model = model or os.environ.get("OPENAI_EMBEDDING_MODEL")
    if not model:
        raise ValueError("OPENAI_EMBEDDING_MODEL é obrigatório para recuperação densa")
    matrix = embed([item["text"] for item in documents], model, client)
    query_vector = embed([query], model, client)[0]
    denominator = np.linalg.norm(matrix, axis=1) * np.linalg.norm(query_vector)
    scores = (matrix @ query_vector) / np.maximum(denominator, 1e-12)
    order = np.argsort(-scores, kind="stable")
    return [{"id": documents[i]["id"], "document_id": str(documents[i].get("document_id", documents[i]["id"]).split(":", 1)[0]), "score": float(scores[i])} for i in order]

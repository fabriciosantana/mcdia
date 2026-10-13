"""Recuperação densa com índice local persistente."""
from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
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


def _digest(payload: Any) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _safe_model(model: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", model).strip("._") or "model"


def _atomic_save_npz(path: Path, **arrays: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False) as stream:
        temporary = Path(stream.name)
    try:
        np.savez_compressed(temporary, **arrays)
        generated = temporary.with_suffix(temporary.suffix + ".npz")
        generated.replace(path)
    finally:
        temporary.unlink(missing_ok=True)
        temporary.with_suffix(temporary.suffix + ".npz").unlink(missing_ok=True)


def _atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", delete=False) as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
        temporary = Path(stream.name)
    temporary.replace(path)


class EmbeddingStore:
    """Armazena matrizes de documentos e vetores de consultas por hash."""

    def __init__(self, root: str | Path):
        self.root = Path(root)

    def _document_key(self, documents: list[dict[str, Any]], model: str) -> str:
        return _digest({"model": model, "documents": [(str(item["id"]), item["text"]) for item in documents]})

    def _document_paths(self, documents: list[dict[str, Any]], model: str) -> tuple[Path, Path, str]:
        key = self._document_key(documents, model)
        prefix = f"documents-{_safe_model(model)}-{key}"
        return self.root / f"{prefix}.npz", self.root / f"{prefix}.json", key

    def document_manifest(self, documents: list[dict[str, Any]], model: str) -> Path:
        return self._document_paths(documents, model)[1]

    def documents(self, documents: list[dict[str, Any]], model: str, client=None, batch_size: int = 128) -> tuple[np.ndarray, Path]:
        matrix_path, manifest_path, key = self._document_paths(documents, model)
        if matrix_path.is_file() and manifest_path.is_file():
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if manifest.get("cache_key") == key and manifest.get("model") == model:
                matrix = np.load(matrix_path, allow_pickle=False)["vectors"]
                if matrix.shape[0] == len(documents) and manifest.get("document_ids") == [str(item["id"]) for item in documents]:
                    return matrix, matrix_path

        batches = [embed([item["text"] for item in documents[start:start + batch_size]], model, client) for start in range(0, len(documents), batch_size)]
        matrix = np.vstack(batches).astype(np.float32, copy=False) if batches else np.empty((0, 0), dtype=np.float32)
        _atomic_save_npz(matrix_path, vectors=matrix)
        _atomic_write_json(manifest_path, {
            "kind": "document-embeddings",
            "cache_key": key,
            "model": model,
            "document_ids": [str(item["id"]) for item in documents],
            "count": int(matrix.shape[0]),
            "dimensions": int(matrix.shape[1]) if matrix.ndim == 2 else 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
        return matrix, matrix_path

    def query(self, query: str, model: str, client=None) -> tuple[np.ndarray, Path]:
        key = _digest({"model": model, "query": query})
        path = self.root / "queries" / _safe_model(model) / f"{key}.npy"
        manifest_path = path.with_suffix(".json")
        if path.is_file() and manifest_path.is_file():
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if manifest.get("cache_key") == key:
                return np.load(path, allow_pickle=False), path
        path.parent.mkdir(parents=True, exist_ok=True)
        vector = embed([query], model, client)[0].astype(np.float32, copy=False)
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
        try:
            np.save(temporary, vector)
            temporary.with_suffix(temporary.suffix + ".npy").replace(path)
        finally:
            temporary.unlink(missing_ok=True)
            temporary.with_suffix(temporary.suffix + ".npy").unlink(missing_ok=True)
        _atomic_write_json(manifest_path, {"kind": "query-embedding", "cache_key": key, "model": model, "query": query, "dimensions": int(vector.shape[0]), "created_at": datetime.now(timezone.utc).isoformat()})
        return vector, path


def rank_dense(documents: list[dict[str, Any]], query: str, model: str | None = None, client=None, embedding_cache: str | Path | None = None) -> list[dict[str, Any]]:
    model = model or os.environ.get("OPENAI_EMBEDDING_MODEL")
    if not model:
        raise ValueError("OPENAI_EMBEDDING_MODEL é obrigatório para recuperação densa")
    if embedding_cache is None:
        matrix = embed([item["text"] for item in documents], model, client)
        query_vector = embed([query], model, client)[0]
    else:
        store = EmbeddingStore(embedding_cache)
        matrix, _ = store.documents(documents, model, client)
        query_vector, _ = store.query(query, model, client)
    denominator = np.linalg.norm(matrix, axis=1) * np.linalg.norm(query_vector)
    scores = (matrix @ query_vector) / np.maximum(denominator, 1e-12)
    order = np.argsort(-scores, kind="stable")
    return [{"id": documents[i]["id"], "document_id": str(documents[i].get("document_id", documents[i]["id"]).split(":", 1)[0]), "score": float(scores[i])} for i in order]

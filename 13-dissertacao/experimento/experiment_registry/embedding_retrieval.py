"""Recuperação densa com índice local persistente."""
from __future__ import annotations

import hashlib
import json
import os
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


def _atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", delete=False) as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
        temporary = Path(stream.name)
    temporary.replace(path)


class EmbeddingStore:
    """Armazena embeddings em coleções persistentes do ChromaDB."""

    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.chroma_root = self.root / "chroma"
        self.manifest_root = self.root / "manifests"

    def _client(self):
        import chromadb
        self.chroma_root.mkdir(parents=True, exist_ok=True)
        return chromadb.PersistentClient(path=str(self.chroma_root))

    def _document_key(self, documents: list[dict[str, Any]], model: str) -> str:
        return _digest({"model": model, "documents": [(str(item["id"]), item["text"]) for item in documents]})

    def _document_paths(self, documents: list[dict[str, Any]], model: str) -> tuple[Path, str]:
        key = self._document_key(documents, model)
        return self.manifest_root / f"documents-{key}.json", key

    def document_manifest(self, documents: list[dict[str, Any]], model: str) -> Path:
        return self._document_paths(documents, model)[0]

    def documents(self, documents: list[dict[str, Any]], model: str, client=None, batch_size: int = 128) -> tuple[np.ndarray, Path]:
        manifest_path, key = self._document_paths(documents, model)
        collection_name = f"documents_{key[:40]}"
        chroma = self._client()
        try:
            collection = chroma.get_collection(collection_name)
            if collection.metadata and collection.metadata.get("cache_key") == key and collection.count() == len(documents):
                stored = collection.get(ids=[str(item["id"]) for item in documents], include=["embeddings"])
                by_id = dict(zip(stored["ids"], stored["embeddings"]))
                if len(by_id) == len(documents):
                    matrix = np.asarray([by_id[str(item["id"])] for item in documents], dtype=np.float32)
                    return matrix, manifest_path
        except Exception:
            collection = None

        try:
            chroma.delete_collection(collection_name)
        except Exception:
            pass
        collection = chroma.get_or_create_collection(collection_name, metadata={"kind": "document-embeddings", "cache_key": key, "model": model})
        for start in range(0, len(documents), batch_size):
            batch = documents[start:start + batch_size]
            vectors = embed([item["text"] for item in batch], model, client)
            collection.add(ids=[str(item["id"]) for item in batch], documents=[item["text"] for item in batch], embeddings=vectors.tolist(), metadatas=[{"document_id": str(item.get("document_id", item["id"]))} for item in batch])
        matrix = np.asarray(collection.get(ids=[str(item["id"]) for item in documents], include=["embeddings"])["embeddings"], dtype=np.float32)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        _atomic_write_json(manifest_path, {
            "kind": "document-embeddings",
            "cache_key": key,
            "model": model,
            "document_ids": [str(item["id"]) for item in documents],
            "count": int(matrix.shape[0]),
            "dimensions": int(matrix.shape[1]) if matrix.ndim == 2 else 0,
            "backend": "chromadb",
            "collection": collection_name,
            "persist_directory": str(self.chroma_root),
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
        return matrix, manifest_path

    def query(self, query: str, model: str, client=None) -> tuple[np.ndarray, Path]:
        key = _digest({"model": model, "query": query})
        collection_name = f"queries_{_digest({'model': model})[:40]}"
        chroma = self._client()
        collection = chroma.get_or_create_collection(collection_name, metadata={"kind": "query-embeddings", "model": model})
        found = collection.get(ids=[key], include=["embeddings"])
        if found["ids"]:
            return np.asarray(found["embeddings"][0], dtype=np.float32), self.root / "chroma" / collection_name
        vector = embed([query], model, client)[0].astype(np.float32, copy=False)
        collection.add(ids=[key], documents=[query], embeddings=[vector.tolist()], metadatas=[{"cache_key": key, "model": model}])
        return vector, self.root / "chroma" / collection_name


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

"""Ingestão, normalização e segmentação determinística do corpus."""
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from .config import ExperimentPaths
from .registry import sha256_file

TOKEN = re.compile(r"\S+", re.UNICODE)


def _jsonl_documents(path: Path) -> list[dict[str, Any]]:
    documents = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"JSONL inválido na linha {line_no}") from exc
        if not isinstance(item, dict) or not item.get("id") or not isinstance(item.get("text"), str):
            raise ValueError(f"documento inválido na linha {line_no}: requer id e text")
        documents.append({"id": str(item["id"]), "text": item["text"], "metadata": item.get("metadata", {})})
    return documents


def load_corpus(path: str | Path) -> list[dict[str, Any]]:
    """Lê JSONL canônico ou Parquet do corpus de discursos."""
    source = Path(path).expanduser()
    if source.suffix.lower() in {".jsonl", ".json"}:
        documents = _jsonl_documents(source)
    elif source.suffix.lower() == ".parquet":
        try:
            import pandas as pd
        except ImportError as exc:
            raise RuntimeError("Parquet requer pandas e pyarrow instalados") from exc
        frame = pd.read_parquet(source)
        text_column = "TextoDiscursoIntegral" if "TextoDiscursoIntegral" in frame.columns else "text"
        summary_column = "Resumo" if "Resumo" in frame.columns else None
        id_column = "id" if "id" in frame.columns else None
        if not id_column or text_column not in frame.columns:
            raise ValueError("Parquet requer as colunas id e TextoDiscursoIntegral (ou text)")
        metadata_columns = [c for c in ("Data", "Casa", "NomeAutor", "URL") if c in frame.columns]
        documents = []
        for row in frame.to_dict("records"):
            text = row.get(text_column)
            if not isinstance(text, str) or len(text.strip()) < 20:
                text = row.get(summary_column) if summary_column else text
            if not isinstance(text, str) or not text.strip():
                continue
            documents.append({
                "id": str(row[id_column]),
                "text": text,
                "metadata": {key: (None if row.get(key) is None else str(row.get(key))) for key in metadata_columns},
            })
    else:
        raise ValueError("formato de corpus não suportado; use JSONL ou Parquet")
    if not documents:
        raise ValueError("o corpus não contém documentos utilizáveis")
    return documents


def chunk_documents(documents: list[dict[str, Any]], window: int = 160, overlap: int = 32) -> list[dict[str, Any]]:
    if window <= 0 or overlap < 0 or overlap >= window:
        raise ValueError("window deve ser positivo e overlap deve estar entre 0 e window-1")
    chunks = []
    step = window - overlap
    for document in documents:
        tokens = TOKEN.findall(document["text"])
        for start in range(0, max(1, len(tokens)), step):
            selected = tokens[start : start + window]
            if len(selected) < 20 and len(tokens) > window:
                break
            chunks.append({
                "id": f'{document["id"]}:{start}',
                "document_id": document["id"],
                "text": " ".join(selected),
                "metadata": {**document.get("metadata", {}), "start_token": start, "end_token": start + len(selected)},
            })
            if start + window >= len(tokens):
                break
    if not chunks:
        raise ValueError("nenhum chunk foi produzido")
    return chunks


def prepare_documents(paths: ExperimentPaths, source_path: str | Path, window: int = 160, overlap: int = 32) -> dict[str, Any]:
    source = Path(source_path).expanduser().resolve()
    documents = load_corpus(source)
    chunks = chunk_documents(documents, window, overlap)
    output = paths.outputs / f"chunks-{hashlib.sha256(str(source).encode()).hexdigest()[:12]}-{window}-{overlap}.jsonl"
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as stream:
        for chunk in chunks:
            stream.write(json.dumps(chunk, ensure_ascii=False) + "\n")
    return {"source": str(source), "source_sha256": sha256_file(source), "output": str(output), "output_sha256": sha256_file(output), "documents": len(documents), "chunks": len(chunks), "window": window, "overlap": overlap}


def load_chunks(path: str | Path) -> list[dict[str, Any]]:
    chunks = []
    for line_no, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        item = json.loads(line)
        if not isinstance(item, dict) or not item.get("id") or not item.get("text"):
            raise ValueError(f"chunk inválido na linha {line_no}")
        chunks.append({"id": str(item["id"]), "document_id": str(item.get("document_id", str(item["id"]).split(":", 1)[0])), "text": item["text"], "metadata": item.get("metadata", {})})
    if not chunks:
        raise ValueError("arquivo de chunks vazio")
    return chunks

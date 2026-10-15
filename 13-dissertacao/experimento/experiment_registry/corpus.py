"""Ingestão, normalização e segmentação determinística do corpus."""
from __future__ import annotations

import csv
import hashlib
import json
import re
import uuid
from collections import Counter
from pathlib import Path
from typing import Any

from .config import ExperimentPaths
from .registry import sha256_file
from .db import connect, initialize_database

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
        metadata=item.get("metadata", {})
        if not isinstance(metadata,dict): raise ValueError(f"metadata deve ser um objeto na linha {line_no}")
        if not item["text"].strip(): raise ValueError(f"texto vazio na linha {line_no}")
        text_source=item.get("text_source") or ("resumo" if metadata.get("text_source")=="resumo" else "integral")
        documents.append({"id": str(item["id"]), "text": item["text"], "original_text": item.get("original_text",item["text"]), "text_source":text_source, "metadata": metadata})
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
        documents = []
        excluded=[]
        for row in frame.to_dict("records"):
            original = row.get(text_column)
            summary = row.get(summary_column) if summary_column else None
            if isinstance(original,str) and len(original.strip())>=20:
                text=original; text_source="integral"
            elif isinstance(summary,str) and summary.strip():
                text=summary; text_source="resumo"
            else:
                text=None; text_source="ausente"
            documents.append({
                "id": str(row[id_column]),
                "text": text or "",
                "original_text": original if isinstance(original,str) else None,
                "text_source": text_source,
                "metadata": {key: (None if pd.isna(row.get(key)) else str(row.get(key))) for key in row if key not in {"TextoDiscursoIntegral","Resumo","text"}},
            })
            if text_source=="ausente": excluded.append({"id":str(row[id_column]),"reason":"texto integral e resumo ausentes"})
    else:
        raise ValueError("formato de corpus não suportado; use JSONL ou Parquet")
    if not documents:
        raise ValueError("o corpus não contém documentos utilizáveis")
    duplicates=sorted(identifier for identifier,count in Counter(d['id'] for d in documents).items() if count>1)
    if duplicates: raise ValueError(f"IDs documentais duplicados: {', '.join(duplicates[:10])}")
    return documents


def chunk_documents(documents: list[dict[str, Any]], window: int = 160, overlap: int = 32, tokenizer: str = "whitespace-regex") -> list[dict[str, Any]]:
    if window <= 0 or overlap < 0 or overlap >= window:
        raise ValueError("window deve ser positivo e overlap deve estar entre 0 e window-1")
    chunks = []
    step = window - overlap
    for document in documents:
        if tokenizer == "whitespace-regex":
            tokens = TOKEN.findall(document["text"])
            decode=lambda values:" ".join(values)
        else:
            try:
                import tiktoken
            except ImportError as exc:
                raise RuntimeError("tokenização por modelo requer tiktoken instalado") from exc
            encoding=tiktoken.encoding_for_model(tokenizer.removeprefix("tiktoken:"))
            tokens=encoding.encode(document["text"])
            decode=encoding.decode
        for start in range(0, max(1, len(tokens)), step):
            selected = tokens[start : start + window]
            if len(selected) < 20 and len(tokens) > window:
                break
            chunks.append({
                "id": f'{document["id"]}:{start}',
                "document_id": document["id"],
                "text": decode(selected),
                "metadata": {**document.get("metadata", {}), "start_token": start, "end_token": start + len(selected)},
            })
            if start + window >= len(tokens):
                break
    if not chunks:
        raise ValueError("nenhum chunk foi produzido")
    return chunks


def prepare_documents(paths: ExperimentPaths, source_path: str | Path, window: int = 160, overlap: int = 32, tokenizer: str = "whitespace-regex") -> dict[str, Any]:
    source = Path(source_path).expanduser().resolve()
    imported_documents = load_corpus(source)
    documents=[document for document in imported_documents if document["text_source"]!="ausente"]
    excluded=[document for document in imported_documents if document["text_source"]=="ausente"]
    if not documents: raise ValueError("nenhum documento utilizável no corpus")
    source_sha256 = sha256_file(source)
    chunks = chunk_documents(documents, window, overlap, tokenizer)
    output = paths.outputs / f"chunks-{hashlib.sha256(str(source).encode()).hexdigest()[:12]}-{tokenizer.replace(':','-')}-{window}-{overlap}.jsonl"
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as stream:
        for chunk in chunks:
            stream.write(json.dumps(chunk, ensure_ascii=False) + "\n")
    initialize_database(paths)
    with connect(paths.database) as connection:
        corpus_version_id=f"cv-{source_sha256[:20]}"
        metadata_coverage={key:sum(1 for d in imported_documents if d.get("metadata",{}).get(key) not in (None,""))/len(imported_documents) for key in sorted({k for d in imported_documents for k in d.get("metadata",{})})}
        connection.execute("INSERT OR IGNORE INTO corpus_versions(corpus_version_id,name,source_sha256,source_path,document_count,excluded_count,metadata_coverage_json) VALUES (?,?,?,?,?,?,?)",(corpus_version_id,source.name,source_sha256,str(source),len(imported_documents),len(excluded),json.dumps(metadata_coverage)))
        for document in imported_documents:
            metadata=document.get("metadata",{})
            connection.execute("INSERT OR IGNORE INTO documents(corpus_version_id,document_id,original_text,indexed_text,text_source,source_url,author,document_date,metadata_json,exclusion_reason) VALUES (?,?,?,?,?,?,?,?,?,?)",(corpus_version_id,document["id"],document.get("original_text",document.get("text")),document.get("text") or None,document.get("text_source","integral"),metadata.get("URL"),metadata.get("NomeAutor"),metadata.get("Data"),json.dumps(metadata,ensure_ascii=False),"texto integral e resumo ausentes" if document.get("text_source")=="ausente" else None))
        config={"tokenizer":tokenizer,"tokenizer_version":"legacy" if tokenizer=="whitespace-regex" else __import__('tiktoken').__version__,"unit":"tokens","window":window,"overlap":overlap}
        config_hash=hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest()
        chunk_set_id=f"cs-{hashlib.sha256((corpus_version_id+config_hash).encode()).hexdigest()[:20]}"
        connection.execute("INSERT OR IGNORE INTO chunk_sets(chunk_set_id,corpus_version_id,config_hash,tokenizer,tokenizer_version,segmentation_unit,window_size,overlap_size,chunk_count) VALUES (?,?,?,?,?,?,?,?,?)",(chunk_set_id,corpus_version_id,config_hash,tokenizer,config["tokenizer_version"],"tokens",window,overlap,len(chunks)))
        for chunk in chunks:
            metadata = {**chunk.get("metadata", {}), "source_path": str(source), "window": window, "overlap": overlap, "tokenizer":tokenizer}
            connection.execute(
                "INSERT OR IGNORE INTO document_chunks(chunk_set_id,chunk_id,corpus_version_id,document_id,text,metadata_json,source_sha256,position_start,position_end) VALUES (?,?,?,?,?,?,?,?,?)",
                (chunk_set_id,chunk["id"],corpus_version_id, chunk["document_id"], chunk["text"], json.dumps(metadata, ensure_ascii=False), source_sha256,chunk["metadata"]["start_token"],chunk["metadata"]["end_token"]),
            )
    return {"source": str(source), "source_sha256": source_sha256,"corpus_version_id":corpus_version_id,"chunk_set_id":chunk_set_id, "output": str(output), "output_sha256": sha256_file(output), "documents": len(imported_documents),"excluded":len(excluded), "chunks": len(chunks), "persisted_chunks": len(chunks), "window": window, "overlap": overlap,"tokenizer":tokenizer,"tokenizer_version":config["tokenizer_version"],"metadata_coverage":metadata_coverage}


def search_chunks(connection, text: str = "", document_id: str = "", limit: int = 100, offset: int = 0, author: str = "", date_from: str = "", date_to: str = "", chunk_set_id: str = "") -> list[dict[str, Any]]:
    """Consulta chunks persistidos para a curadoria manual."""
    clauses = []
    params: list[Any] = []
    if text.strip():
        clauses.append("text LIKE ?")
        params.append(f"%{text.strip()}%")
    if document_id.strip():
        clauses.append("document_id LIKE ?")
        params.append(f"%{document_id.strip()}%")
    joins=" JOIN documents d ON d.corpus_version_id=c.corpus_version_id AND d.document_id=c.document_id"
    for column,value,operator in (("d.author",author, "contains"),("d.document_date",date_from,">="),("d.document_date",date_to,"<="),("c.chunk_set_id",chunk_set_id,"=")):
        if value.strip():
            clauses.append(f"{column} LIKE ?" if operator=="contains" else f"{column} {operator} ?")
            params.append(f"%{value.strip()}%" if operator=="contains" else value.strip())
    where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
    params.extend((max(1, min(int(limit), 500)),max(0,int(offset))))
    rows = connection.execute(f"SELECT c.chunk_id,c.chunk_set_id,c.corpus_version_id,c.document_id,c.text,c.metadata_json,c.source_sha256,c.created_at,d.text_source,d.source_url,d.author,d.document_date FROM document_chunks c{joins}{where} ORDER BY c.document_id,c.position_start,c.chunk_id LIMIT ? OFFSET ?", params)
    return [dict(row) for row in rows]

def chunk_context(connection,chunk_set_id:str,chunk_id:str,radius:int=1):
    row=connection.execute("SELECT document_id,position_start FROM document_chunks WHERE chunk_set_id=? AND chunk_id=?",(chunk_set_id,chunk_id)).fetchone()
    if not row:return []
    return [dict(r) for r in connection.execute("SELECT * FROM (SELECT c.chunk_id,c.document_id,c.text,c.position_start,d.source_url,d.text_source FROM document_chunks c JOIN documents d USING(corpus_version_id,document_id) WHERE c.chunk_set_id=? AND c.document_id=? ORDER BY ABS(COALESCE(c.position_start,0)-COALESCE(?,0)) LIMIT ?) ORDER BY position_start",(chunk_set_id,row['document_id'],row['position_start'],2*radius+1))]


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

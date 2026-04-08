#!/usr/bin/env python3
import argparse
import json
import math
import re
from pathlib import Path

import pandas as pd
from huggingface_hub import hf_hub_download, list_repo_files


def normalize_text(text: str) -> str:
    text = (text or "").replace("\u00a0", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def chunk_words(text: str, max_words: int, overlap_words: int) -> list[str]:
    words = text.split()
    if not words:
        return []
    if len(words) <= max_words:
        return [" ".join(words)]

    step = max_words - overlap_words
    if step <= 0:
        raise ValueError("max_words must be greater than overlap_words")

    chunks = []
    for start in range(0, len(words), step):
        end = start + max_words
        chunk = words[start:end]
        if not chunk:
            break
        chunks.append(" ".join(chunk))
        if end >= len(words):
            break
    return chunks


def choose_text(row: pd.Series) -> str:
    preferred_fields = ["TextoDiscursoIntegral", "Resumo", "Indexacao"]
    for field in preferred_fields:
        value = row.get(field, "")
        if isinstance(value, str) and value.strip():
            return value
    return ""


def escape_md(value: str) -> str:
    return (value or "").replace("\n", " ").strip()


def resolve_parquet_path(repo_id: str, parquet_rel_path: str | None) -> Path:
    if parquet_rel_path:
        return Path(
            hf_hub_download(
                repo_id=repo_id, repo_type="dataset", filename=parquet_rel_path
            )
        )

    files = list_repo_files(repo_id=repo_id, repo_type="dataset")
    parquet_files = [f for f in files if f.lower().endswith(".parquet")]
    if not parquet_files:
        raise RuntimeError(f"No parquet file found in dataset {repo_id}")
    parquet_files.sort()
    return Path(
        hf_hub_download(repo_id=repo_id, repo_type="dataset", filename=parquet_files[0])
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build OpenWebUI knowledge files from a Hugging Face parquet dataset."
    )
    parser.add_argument(
        "--repo-id",
        default="fabriciosantana/discursos-senado-legislatura-56",
        help="Hugging Face dataset repo id",
    )
    parser.add_argument(
        "--parquet-path",
        default="data/full/discursos_2019-02-01_2023-01-31.parquet",
        help="Relative parquet path inside the dataset repo. If empty, auto-discover.",
    )
    parser.add_argument(
        "--output-dir",
        default="knowledge_openwebui",
        help="Output directory for generated files",
    )
    parser.add_argument(
        "--max-words", type=int, default=850, help="Max words per chunk"
    )
    parser.add_argument(
        "--overlap-words", type=int, default=150, help="Overlap words between chunks"
    )
    parser.add_argument(
        "--chunks-per-file",
        type=int,
        default=200,
        help="How many chunks to place in each markdown file",
    )
    parser.add_argument(
        "--limit-rows",
        type=int,
        default=0,
        help="Optional limit for testing (0 = no limit)",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir).resolve()
    md_dir = output_dir / "md_batches"
    output_dir.mkdir(parents=True, exist_ok=True)
    md_dir.mkdir(parents=True, exist_ok=True)

    parquet_path = resolve_parquet_path(
        repo_id=args.repo_id, parquet_rel_path=args.parquet_path or None
    )
    df = pd.read_parquet(parquet_path)
    if args.limit_rows > 0:
        df = df.head(args.limit_rows)

    jsonl_path = output_dir / "discursos_chunks.jsonl"
    metadata_path = output_dir / "build_metadata.json"

    total_input_rows = len(df)
    written_rows = 0
    skipped_rows = 0
    total_chunks = 0

    batch_index = 1
    chunk_in_batch = 0
    md_file = (md_dir / f"batch_{batch_index:05d}.md").open("w", encoding="utf-8")
    md_file.write(
        "# Discursos Senado - Knowledge Batch 1\n\n"
        "Generated for OpenWebUI Knowledge ingestion.\n\n"
    )

    with jsonl_path.open("w", encoding="utf-8") as jf:
        for _, row in df.iterrows():
            base_text = normalize_text(choose_text(row))
            if not base_text:
                skipped_rows += 1
                continue

            chunks = chunk_words(
                text=base_text,
                max_words=args.max_words,
                overlap_words=args.overlap_words,
            )
            if not chunks:
                skipped_rows += 1
                continue

            row_id = str(row.get("id", "")).strip() or str(row.get("CodigoPronunciamento", ""))
            data = str(row.get("Data", "") or "")
            nome_autor = str(row.get("NomeAutor", "") or "")
            partido = str(row.get("Partido", "") or "")
            uf = str(row.get("UF", "") or "")
            casa = str(row.get("Casa", "") or "")
            tipo = str(row.get("TipoUsoPalavra.Descricao", "") or "")
            resumo = normalize_text(str(row.get("Resumo", "") or ""))
            indexacao = normalize_text(str(row.get("Indexacao", "") or ""))
            texto_url = str(row.get("TextoIntegral", "") or "")

            for i, chunk_text in enumerate(chunks, start=1):
                chunk_id = f"{row_id}-{i:03d}"
                record = {
                    "chunk_id": chunk_id,
                    "source_id": row_id,
                    "chunk_index": i,
                    "chunk_count": len(chunks),
                    "metadata": {
                        "data": data,
                        "nome_autor": nome_autor,
                        "partido": partido,
                        "uf": uf,
                        "casa": casa,
                        "tipo_uso_palavra": tipo,
                        "texto_integral_url": texto_url,
                        "resumo": resumo,
                        "indexacao": indexacao,
                    },
                    "text": chunk_text,
                }
                jf.write(json.dumps(record, ensure_ascii=False) + "\n")

                if chunk_in_batch >= args.chunks_per_file:
                    md_file.close()
                    batch_index += 1
                    chunk_in_batch = 0
                    md_file = (md_dir / f"batch_{batch_index:05d}.md").open(
                        "w", encoding="utf-8"
                    )
                    md_file.write(
                        f"# Discursos Senado - Knowledge Batch {batch_index}\n\n"
                        "Generated for OpenWebUI Knowledge ingestion.\n\n"
                    )

                md_file.write(f"## Chunk {chunk_id}\n")
                md_file.write(f"- Data: {escape_md(data)}\n")
                md_file.write(f"- Autor: {escape_md(nome_autor)}\n")
                md_file.write(f"- Partido: {escape_md(partido)}\n")
                md_file.write(f"- UF: {escape_md(uf)}\n")
                md_file.write(f"- Casa: {escape_md(casa)}\n")
                md_file.write(f"- Tipo: {escape_md(tipo)}\n")
                if texto_url:
                    md_file.write(f"- Fonte: {escape_md(texto_url)}\n")
                if resumo:
                    md_file.write(f"- Resumo: {escape_md(resumo)}\n")
                if indexacao:
                    md_file.write(f"- Indexacao: {escape_md(indexacao)}\n")
                md_file.write("\n")
                md_file.write(chunk_text)
                md_file.write("\n\n---\n\n")

                total_chunks += 1
                chunk_in_batch += 1

            written_rows += 1

    md_file.close()

    metadata = {
        "repo_id": args.repo_id,
        "parquet_local_path": str(parquet_path),
        "total_input_rows": total_input_rows,
        "written_rows": written_rows,
        "skipped_rows": skipped_rows,
        "total_chunks": total_chunks,
        "max_words": args.max_words,
        "overlap_words": args.overlap_words,
        "chunks_per_file": args.chunks_per_file,
        "markdown_batch_files": math.ceil(total_chunks / args.chunks_per_file)
        if total_chunks
        else 0,
        "jsonl_path": str(jsonl_path),
        "markdown_dir": str(md_dir),
    }
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(json.dumps(metadata, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

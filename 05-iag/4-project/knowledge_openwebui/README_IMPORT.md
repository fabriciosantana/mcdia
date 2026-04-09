# Importing In OpenWebUI

This folder was generated from:
- Dataset: `fabriciosantana/discursos-senado-legislatura-56`
- Source file: `data/full/discursos_2019-02-01_2023-01-31.parquet`

Generated artifacts:
- `discursos_chunks.jsonl`: structured chunks with metadata (for custom pipelines)
- `md_batches/`: markdown files ready for OpenWebUI Knowledge upload
- `build_metadata.json`: generation summary

## Quick Import Steps

1. Open OpenWebUI admin/user panel.
2. Go to `Knowledge`.
3. Create a new knowledge base (for example: `Discursos Senado 56`).
4. Add files from `md_batches/` (multiple upload is recommended).
5. Wait for indexing to finish.

## Notes

- Generated with `max_words=850` and `overlap_words=150`.
- Current output has `120` markdown files.
- If you want fewer/larger files, regenerate with a higher `--chunks-per-file` value.

# Importando a base no Open WebUI

Esta pasta é o destino dos artefatos gerados por:

- `scripts/build_openwebui_knowledge_from_hf.py`

Fonte de dados esperada:

- Dataset: `fabriciosantana/discursos-senado-legislatura-56`
- Arquivo parquet: `data/full/discursos_2019-02-01_2023-01-31.parquet`

Artefatos gerados quando a preparação é executada:

- `discursos_chunks.jsonl`: chunks estruturados com metadados
- `md_batches/`: arquivos Markdown prontos para ingestão no Open WebUI
- `build_metadata.json`: resumo quantitativo da geração

Observação: os lotes Markdown e o `jsonl` podem não estar versionados no repositório. Se esta pasta contiver apenas este README, regenere os artefatos pelo comando documentado no README principal do projeto.

## Fluxo recomendado

1. Gere os lotes com `build_openwebui_knowledge_from_hf.py`.
2. Crie a Knowledge Base no Open WebUI.
3. Descubra o `knowledge_id`.
4. Importe os batches via `scripts/import_batches_to_openwebui.py`.

## Upload manual

Se preferir usar a interface:

1. abra `Knowledge` no Open WebUI;
2. crie uma knowledge base;
3. faça upload múltiplo dos arquivos em `md_batches/`;
4. aguarde o término da indexação.

## Upload automatizado

```bash
python scripts/import_batches_to_openwebui.py \
  --knowledge-id <knowledge_id> \
  --pattern 'knowledge_openwebui/md_batches/batch_*.md'
```

## Parâmetros usados na geração validada no projeto

- `max_words=850`
- `overlap_words=150`
- `chunks_per_file=200`

Na execução completa descrita no artigo, isso resultou em `120` arquivos Markdown.

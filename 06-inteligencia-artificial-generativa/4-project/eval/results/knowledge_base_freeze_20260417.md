# Congelamento da knowledge base de avaliacao

Data: 2026-04-17

## Objetivo

Confirmar formalmente que as rodadas comparadas na fase atual do experimento usam a mesma knowledge base no Open WebUI e os mesmos artefatos de origem, sem evidencia de reindexacao entre elas.

## Rodadas verificadas

- [rag_eval_20260416T172816Z.run_config.json](/workspaces/mcdia/05-iag/4-project/eval/results/rag_eval_20260416T172816Z.run_config.json:1)
- [rag_eval_20260416T182240Z.run_config.json](/workspaces/mcdia/05-iag/4-project/eval/results/rag_eval_20260416T182240Z.run_config.json:1)
- [rag_eval_20260416T232921Z.run_config.json](/workspaces/mcdia/05-iag/4-project/eval/results/rag_eval_20260416T232921Z.run_config.json:1)
- [rag_eval_20260417T022327Z.run_config.json](/workspaces/mcdia/05-iag/4-project/eval/results/rag_eval_20260417T022327Z.run_config.json:1)
- [rag_eval_20260417T024620Z.run_config.json](/workspaces/mcdia/05-iag/4-project/eval/results/rag_eval_20260417T024620Z.run_config.json:1)

## Evidencia consolidada

- `knowledge_id`: `902f627d-ab07-43bb-a395-8d573117f4fc`
- `build_metadata.json`
  - SHA-256: `abfc1956a78e87f57266a53b7982abb8d364b42fd22d777fbe3053353c1c90be`
- `discursos_chunks.jsonl`
  - SHA-256: `70297ce414e3eb5da2615ca7a158fc8667cf6d50fa9a88dfa9aa2f445d89b66c`
- `knowledge_openwebui/md_batches/`
  - quantidade de arquivos: `120`
  - primeira amostra registrada: `batch_00001.md`
  - SHA-256 da amostra: `bc9599ab089e7b9beeaa2c6651249b1af28400cba2fae089e7b30bbeaa2bd2a7`

## Conclusao

As cinco rodadas verificadas compartilham o mesmo `knowledge_id` e os mesmos fingerprints dos artefatos associados a base indexada. Dentro desse conjunto de evidencias, nao ha sinal de reindexacao ou troca silenciosa da knowledge base entre as rodadas comparadas.

## Implicacao metodologica

As comparacoes entre essas rodadas podem ser tratadas como comparacoes sobre a mesma base de conhecimento. A partir deste ponto, qualquer nova rodada que pretenda entrar no mesmo conjunto comparativo deve manter:

- o mesmo `knowledge_id`; e
- os mesmos fingerprints de `build_metadata.json`, `discursos_chunks.jsonl` e `md_batches/`.

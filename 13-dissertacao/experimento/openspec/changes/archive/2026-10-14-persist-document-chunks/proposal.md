# Persistência e consulta de chunks

## Why

A preparação do corpus produzia um JSONL derivado, mas os chunks não eram persistidos em `document_chunks`. Isso impedia a curadoria das perguntas pelo aplicativo e exigia consultar arquivos externos para localizar `chunk_id` relevantes.

## What Changes

- persistir chunks preparados no SQLite com texto, documento, hash da fonte e parâmetros de segmentação;
- disponibilizar busca e visualização de chunks no dashboard;
- manter o JSONL como artefato de exportação e compatibilidade.

## Fora de escopo

- alterar o corpus bruto;
- substituir o armazenamento vetorial ChromaDB;
- fazer curadoria automática de relevância.

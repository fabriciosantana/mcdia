# Migração do índice vetorial para ChromaDB

## Why

O índice persistente inicial usava arquivos NumPy, enquanto o sistema precisa de uma camada vetorial que mantenha documentos, metadados e embeddings em uma coleção consultável.

## What Changes

- usar ChromaDB persistente em `data/embeddings/chroma`;
- manter coleções identificadas por modelo e hash do corpus;
- armazenar também embeddings de consultas em coleções persistentes;
- atualizar a documentação e a dependência de runtime.

## Fora de escopo

- serviço Chroma remoto ou implantação distribuída;
- remoção automática de índices antigos;
- alteração dos dados brutos do corpus.

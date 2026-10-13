# Design

## Context

O registro SQLite e o dashboard já existem. O notebook 02 contém um baseline exploratório, mas não persiste resultados no registro. O executor deve transformar esse baseline em um componente testável e independente de provedores de LLM.

## Goals / Non-Goals

**Goals:** executar BM25, TF–IDF e híbrido; persistir rankings e métricas; usar entradas em JSONL/CSV; produzir artefatos auditáveis.

**Non-Goals:** gerar respostas, chamar APIs externas, construir banco vetorial persistente ou substituir o notebook exploratório nesta etapa.

## Decisions

1. Usar `scikit-learn` para TF–IDF e similaridade; BM25 será implementado localmente para manter controle dos parâmetros.
2. Representar documentos como JSONL `{id,text}` e perguntas como CSV com `question_id,query,reference_doc_ids`.
3. Registrar hashes SHA-256 dos dois arquivos de entrada na configuração da execução.
4. Persistir métricas agregadas e detalhes por pergunta em tabelas e JSON.
5. Tratar `tfidf` como baseline vetorial lexical; embeddings neurais entrarão em adaptador posterior, sem chamar serviços externos.

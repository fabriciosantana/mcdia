# Design

## Context

O registro já possui execuções, perguntas e recuperações. Esta mudança acrescenta a camada posterior sem assumir um fornecedor de modelo.

## Goals / Non-Goals

**Goals:** persistir respostas, citações e avaliações; oferecer ingestão JSONL; manter rubrica explícita e auditável.

**Non-Goals:** chamada automática a APIs, treinamento, julgamento automático ou anonimização completa de avaliadores.

## Decisions

1. Usar JSONL para ingestão, permitindo adaptadores para qualquer modelo local ou serviço.
2. Persistir citações como linhas próprias, vinculadas à resposta e com documento, trecho e texto opcional.
3. Usar cinco colunas ordinais inteiras e observações livres para a avaliação humana.
4. Manter o dashboard como cliente da API de persistência.

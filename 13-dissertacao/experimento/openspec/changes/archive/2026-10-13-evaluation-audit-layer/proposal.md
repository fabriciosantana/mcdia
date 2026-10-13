# Proposta: camada de auditoria avaliativa

## Why

A dissertação exige análise de casos críticos, intervalos de confiança e rastreabilidade das citações. O pipeline principal ainda não persistia esses elementos.

## What Changes

- adicionar bootstrap determinístico;
- registrar erros por resposta e severidade;
- extrair somente citações explicitamente presentes na resposta.

## Impact

Os resultados passam a preservar análise de incerteza e casos negativos sem misturar julgamento humano e automatizado.


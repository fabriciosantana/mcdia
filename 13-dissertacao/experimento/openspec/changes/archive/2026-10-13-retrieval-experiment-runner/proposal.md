# Proposal

## Why

O gerenciador já registra execuções, mas ainda não executa o piloto de recuperação nem persiste seus resultados. Um executor controlado é necessário para comparar baselines sob as mesmas perguntas e evidências e eliminar a manipulação manual de arquivos.

## What Changes

- Adicionar tabelas para perguntas, resultados de recuperação e métricas.
- Implementar executor determinístico para BM25, TF–IDF e híbrido.
- Persistir ranking, documentos recuperados, métricas Recall@k e MRR e artefatos JSON.
- Integrar a execução ao CLI e exibir resultados no dashboard.
- Manter geração por modelo de linguagem como interface futura, sem chamadas externas nesta mudança.

## Capabilities

### New Capabilities

- `retrieval-runner`: executar, comparar e persistir experimentos de recuperação sobre perguntas e documentos fornecidos.

### Modified Capabilities

- `experiment-registry`: adicionar entidades persistentes para perguntas, resultados e métricas de recuperação.

## Impact

A mudança adiciona uma migração SQLite, módulos Python de recuperação, comando CLI, dependência de scikit-learn e visualização básica no dashboard. Dados brutos permanecem inalterados; entradas do runner são arquivos derivados ou conjuntos de teste explicitamente fornecidos.

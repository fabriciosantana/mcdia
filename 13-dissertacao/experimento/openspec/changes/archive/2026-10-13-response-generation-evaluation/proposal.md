# Proposal

## Why

A recuperação já produz evidências e métricas, mas o sistema ainda não registra respostas geradas, citações ou julgamentos humanos. Essa lacuna impede avaliar verificabilidade, insuficiência documental e concordância entre avaliadores.

## What Changes

- Criar tabelas para respostas, citações e avaliações humanas.
- Definir formato de ingestão independente do provedor de modelo.
- Associar resposta e citações a pergunta e execução de recuperação.
- Registrar notas 0–2 nas cinco dimensões e observações.
- Exibir respostas e avaliações no dashboard.

## Capabilities

### New Capabilities
- `response-evaluation`: registrar respostas, evidências citadas e avaliações humanas.

### Modified Capabilities
- `experiment-dashboard`: exibir respostas e avaliações persistidas.

## Impact

Adiciona migração SQLite, API de ingestão JSONL, comando CLI e campos de avaliação. Não executa chamadas externas automaticamente nem altera o corpus bruto.

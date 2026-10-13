# response-generation-evaluation

Persistência de respostas, citações e avaliações

## Verification

- `python -m unittest discover -s tests -v` — 11 testes aprovados.
- `python -m compileall -q experiment_registry dashboard scripts` — aprovado.
- Migração 003 aplicada em banco temporário.
- Resposta, citação e avaliação 0–2 testadas com corpus sintético.
- Dashboard exibe respostas e avaliações persistidas.
- `openspec validate --all` — aprovado antes do arquivamento.

## Limites

A ingestão é independente do provedor e não executa chamadas externas. Um adaptador de modelo deve produzir o JSONL documentado; avaliações automatizadas ainda não substituem a avaliação humana.

# establish-experiment-registry

Registro persistente de configurações e execuções experimentais

## Verification

- `python -m compileall -q experiment_registry scripts`
- `python -m unittest discover -s tests -v` — 5 testes aprovados.
- Os testes também passaram em ambiente virtual limpo com `requirements.txt`.
- `python -m experiment_registry.cli demo` criou banco e relatório JSON sintéticos.
- `openspec validate --changes establish-experiment-registry` passou sem erros.

## Limites da primeira versão

O registro ainda não executa recuperação, geração, embeddings ou banco vetorial. Ele fornece a persistência e a integridade necessárias para integrar esses componentes em mudanças posteriores.

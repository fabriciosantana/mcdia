# Verificação

A mudança foi implementada no dashboard e validada com:

```bash
python -m compileall -q experiment_registry dashboard
python -m unittest discover -s tests -v
```

A geração real via LLM depende de `OPENAI_API_KEY` e `OPENAI_MODEL` configurados no ambiente local. O teste automatizado usa um cliente falso para não fazer chamadas externas.


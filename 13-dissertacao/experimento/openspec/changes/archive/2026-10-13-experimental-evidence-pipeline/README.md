# Verificação

A mudança será validada com:

```bash
openspec validate --all --strict
python -m unittest discover -s tests -v
python -m compileall -q experiment_registry dashboard
```


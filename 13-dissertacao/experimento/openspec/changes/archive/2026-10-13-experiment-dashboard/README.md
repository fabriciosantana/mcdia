
## Verification

- `python -m unittest discover -s tests -v` — 8 testes aprovados, incluindo o registro e o parser do dashboard.
- `python -m compileall -q experiment_registry dashboard scripts` — aprovado.
- A instalação em ambiente virtual limpo com `requirements.txt` foi concluída.
- `streamlit run dashboard/app.py` iniciou o servidor local em smoke test.
- `openspec validate --changes experiment-dashboard` — aprovado.

## Limites da primeira versão

A interface é local, sem autenticação, sem execução de RAG e sem acesso remoto. Ela opera somente sobre o registro SQLite existente.

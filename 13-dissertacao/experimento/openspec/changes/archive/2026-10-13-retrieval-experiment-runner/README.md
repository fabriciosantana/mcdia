# retrieval-experiment-runner

Executor persistente de experimentos de recuperação

## Verification

- `python -m unittest discover -s tests -v` — 10 testes aprovados.
- `python -m compileall -q experiment_registry dashboard scripts` — aprovado.
- Instalação de `requirements.txt` e testes em ambiente virtual limpo — aprovados.
- CLI `run-retrieval` executado em corpus sintético com estratégia híbrida e artefato JSON produzido.
- `openspec validate --all` — aprovado antes do arquivamento.

## Limites

O TF–IDF é um baseline vetorial lexical, não um modelo de embeddings neural. O executor ainda não gera respostas nem chama modelos de linguagem; essas etapas serão adaptadores posteriores que consumirão os resultados persistidos.

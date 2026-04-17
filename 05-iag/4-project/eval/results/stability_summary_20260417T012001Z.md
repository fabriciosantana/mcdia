# Stability Summary

Gerado em: `2026-04-17 01:20:01Z`

## Rodadas comparadas

### rag_eval_20260416T172816Z

- CSV: `/workspaces/mcdia/05-iag/4-project/eval/results/rag_eval_20260416T172816Z.csv`
- Run config: `/workspaces/mcdia/05-iag/4-project/eval/results/rag_eval_20260416T172816Z.run_config.json`
- Perguntas: `20`
- Statuses: `ok`
- Total score: min `6` | media `9.15` | max `10`
- Gerador: `gpt-5-nano` | Juiz: `gpt-5-nano`
- Knowledge ID: `902f627d-ab07-43bb-a395-8d573117f4fc`

### rag_eval_20260416T182240Z

- CSV: `/workspaces/mcdia/05-iag/4-project/eval/results/rag_eval_20260416T182240Z.csv`
- Run config: `/workspaces/mcdia/05-iag/4-project/eval/results/rag_eval_20260416T182240Z.run_config.json`
- Perguntas: `20`
- Statuses: `ok`
- Total score: min `7` | media `9.55` | max `10`
- Gerador: `gpt-5-nano` | Juiz: `gpt-5-nano`
- Knowledge ID: `902f627d-ab07-43bb-a395-8d573117f4fc`

### rag_eval_20260416T232921Z

- CSV: `/workspaces/mcdia/05-iag/4-project/eval/results/rag_eval_20260416T232921Z.csv`
- Run config: `/workspaces/mcdia/05-iag/4-project/eval/results/rag_eval_20260416T232921Z.run_config.json`
- Perguntas: `20`
- Statuses: `ok`
- Total score: min `7` | media `9.35` | max `10`
- Gerador: `gpt-5-nano` | Juiz: `gpt-5-nano`
- Knowledge ID: `902f627d-ab07-43bb-a395-8d573117f4fc`

## Leitura inicial

- Rodadas analisadas: `3`
- Media das medias: `9.35`
- Melhor media observada: `9.55`
- Pior media observada: `9.15`
- Perguntas com variacao entre rodadas: `12`

## Variacao por pergunta

| Pergunta | Categoria | Scores | Amplitude |
|---|---|---|---|
| `q15` | `numbers_precision` | `6, 10, 10` | `4` |
| `q16` | `scope_control` | `7, 9, 10` | `3` |
| `q08` | `numbers` | `8, 10, 10` | `2` |
| `q09` | `author_focus` | `10, 10, 8` | `2` |
| `q18` | `cross_author` | `8, 7, 9` | `2` |
| `q19` | `retrieval_stress` | `10, 10, 8` | `2` |
| `q01` | `factual` | `10, 10, 9` | `1` |
| `q02` | `factual` | `10, 9, 9` | `1` |
| `q07` | `synthesis` | `9, 10, 9` | `1` |
| `q10` | `broad` | `10, 9, 9` | `1` |
| `q11` | `comparison` | `8, 9, 9` | `1` |
| `q14` | `multi_hop` | `7, 8, 7` | `1` |

## Conclusao inicial

- As rodadas comparadas sao operacionalmente estaveis: todas completaram com sucesso.
- Ainda ha variacao metodologica relevante em parte do benchmark, especialmente nas perguntas com maior amplitude de score.
- Perguntas mais instaveis nesta leitura inicial: `q15`.

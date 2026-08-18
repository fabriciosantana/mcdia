# Notebooks da dissertação

Este diretório reúne os notebooks de desenvolvimento e análise da pesquisa. Os notebooks devem ser executados a partir de um ambiente criado com as dependências de `requirements.txt`.

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r 13-dissertacao/notebooks/requirements.txt
```

## Catálogo

| Ordem | Notebook | Finalidade | Situação |
|---:|---|---|---|
| 01 | `01-analisar-base-discursos-rag.ipynb` | Auditoria completa, análise exploratória e avaliação da prontidão do corpus para uma solução RAG | Criado |

## Convenções

- Os arquivos originais ficam em `13-dissertacao/dados/` e não são modificados pelos notebooks.
- Um notebook pode baixar dados públicos quando o arquivo necessário não estiver disponível localmente.
- Tabelas ou figuras destinadas à dissertação devem ser exportadas apenas para diretórios próprios, sem sobrescrever os dados de origem.
- Novos notebooks devem receber prefixos numéricos sequenciais e ser registrados neste catálogo.


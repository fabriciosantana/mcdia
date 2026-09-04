# Trabalho final — Auditoria de Dados e Accountability com Python

Este diretório concentra os artefatos do short paper sobre uma solução RAG
auditável para consulta a discursos do Senado Federal.

## Estrutura

- `main.tex`: fonte principal do short paper;
- `referencias.bib`: referências bibliográficas;
- `analise_corpus_discursos.ipynb`: auditoria, caracterização, segmentação e
  baseline de recuperação lexical;
- `avaliacao/perguntas_referencia.json`: coleção inicial de perguntas e
  documentos conhecidos para avaliação da recuperação;
- `scripts/baixar_dados_hf.py`: download reproduzível do corpus no Hugging Face;
- `dados/`: dados baixados localmente (ignorados pelo Git);
- `resultados/`: tabelas produzidas pelo notebook;
- `figuras/`: figuras produzidas para o artigo;
- `Guia e Orientações do Trabalho Final.pdf`: enunciado da atividade.

## Dados

O corpus é obtido do repositório público
`fabriciosantana/discursos-senado-legislatura-56` no Hugging Face. Para baixar o
primeiro arquivo Parquet encontrado no dataset:

```bash
python -m pip install -r requirements.txt
python scripts/baixar_dados_hf.py
```

O script registra a URL de origem, o nome do arquivo remoto e o hash SHA-256 em
`dados/proveniencia.json`. É possível selecionar explicitamente um arquivo:

```bash
python scripts/baixar_dados_hf.py --arquivo caminho/no/repositorio.parquet
```

## Execução do notebook

Abra `analise_corpus_discursos.ipynb` no Jupyter ou VS Code e execute todas as
células. O notebook não requer chave de API. Além da auditoria do corpus, ele
gera uma prova de conceito TF–IDF sobre uma amostra de mil documentos e exporta
os resultados usados no artigo para `resultados/` e `figuras/`.

## Compilação do artigo

```bash
latexmk -pdf main.tex
```

O PDF será criado em `out/main.pdf`.

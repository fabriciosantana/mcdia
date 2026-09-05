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

## Avaliação com embeddings da OpenAI

Preencha `OPENAI_API_KEY` no arquivo `.env`. O `.env` e o cache de embeddings
são ignorados pelo Git. Valide primeiro o plano sem chamar a API:

```bash
python scripts/gerar_embeddings_openai.py --planejar
```

Depois gere os embeddings e execute a comparação:

```bash
python scripts/gerar_embeddings_openai.py
python scripts/avaliar_recuperacao.py
```

O gerador usa `text-embedding-3-large` com 512 dimensões, respeita o limite por
entrada, cria lotes por orçamento de tokens e mantém checkpoints retomáveis. O
avaliador compara TF–IDF, recuperação vetorial e fusão por Reciprocal Rank
Fusion (RRF). Não compartilhe o `.env` nem inclua a chave em células do
notebook.

O avaliador também produz um pool cego com a união dos dez primeiros resultados
de cada método em `resultados/pool_avaliacao.xlsx`. A correspondência entre os
itens e os rankings permanece separada em `pool_chave_metodos.csv`.

## Julgamento por LLM

Para produzir dois julgamentos cegos por item e adjudicar automaticamente
divergências, baixa confiança ou informação insuficiente:

```bash
python scripts/julgar_pool_llm.py
python scripts/calcular_metricas_julgadas.py
```

O processo usa um snapshot fixo do modelo, Structured Outputs e checkpoints. A
saída principal é `pool_julgado_llm.xlsx`. Cada par recebe dois julgamentos cegos
na escala 0--2; divergências, baixa confiança ou insuficiência de informação são
adjudicadas em uma terceira chamada com contexto ampliado. O cálculo seguinte
produz Precision@5, Precision@10, recall dentro do pool, MRR e nDCG@10.

Não há etapa de avaliação humana. Portanto, os rótulos devem ser descritos como
uma aproximação automática de relevância, e não como padrão-ouro. A concordância
entre as duas passagens mede consistência interna do procedimento, não sua
validade externa.

## Compilação do artigo

```bash
latexmk -pdf main.tex
```

O PDF será criado em `out/main.pdf`.

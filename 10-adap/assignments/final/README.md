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

O avaliador também produz `resultados/pool_julgamento.xlsx`. Preencha somente
as colunas `julgamento_relevancia` e `observacoes`, usando a escala indicada na
aba `Instruções`. Para reduzir viés, não consulte `pool_chave_metodos.csv` antes
de terminar os julgamentos.

Depois de preencher e salvar todos os 205 julgamentos com `0`, `1` ou `2`,
calcule Precision@5, Precision@10, recall dentro do pool, MRR e nDCG@10:

```bash
python scripts/calcular_metricas_julgadas.py
```

O valor `?` deve ser adjudicado antes do cálculo final.

## Julgamento assistido por LLM

Para produzir dois julgamentos cegos por item e adjudicar automaticamente
divergências, baixa confiança ou informação insuficiente:

```bash
python scripts/julgar_pool_llm.py
python scripts/calcular_metricas_julgadas.py --fonte llm
```

O processo usa um snapshot fixo do modelo, Structured Outputs e checkpoints. A
saída principal é `pool_julgado_llm.xlsx`. A planilha
`amostra_validacao_humana.xlsx` contém 40 itens estratificados; preencha
`julgamento_especialista` com `0`, `1` ou `2` antes da análise final de
concordância. Os rótulos automáticos não devem ser descritos como padrão-ouro
humano. Para evitar ancoragem, os rótulos do LLM ficam separados em
`amostra_validacao_humana_chave.csv`, que não deve ser consultado antes do
preenchimento.

## Compilação do artigo

```bash
latexmk -pdf main.tex
```

O PDF será criado em `out/main.pdf`.

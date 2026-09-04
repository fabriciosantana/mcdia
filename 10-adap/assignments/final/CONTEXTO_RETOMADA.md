# Contexto para retomada do trabalho final

Última atualização: 4 de setembro de 2026.

## Decisões tomadas

- O trabalho final da disciplina **Auditoria de Dados e Accountability com
  Python** será produzido como short paper em LaTeX.
- Todos os artefatos devem permanecer em `10-adap/assignments/final/`.
- Tema escolhido: proposta de uma solução RAG auditável para consulta e análise
  de discursos do Senado Federal.
- Título de trabalho: **Recuperação aumentada por geração para análise auditável
  de discursos do Senado Federal**.
- O corpus deve ser obtido diretamente do dataset público
  `fabriciosantana/discursos-senado-legislatura-56`, no Hugging Face.
- A solução deve ser apresentada como apoio à pesquisa, à transparência e à
  accountability. Não deve ser descrita como mecanismo autônomo para auditar
  parlamentares, verificar fatos ou inferir intenções.
- O notebook atual deve permanecer reproduzível sem serviços pagos ou chaves de
  API. O baseline é lexical, baseado em TF–IDF.
- Caso sejam incorporados embeddings ou geração em nuvem, criar `.env` ignorado
  pelo Git. Chaves prováveis: `OPENAI_API_KEY`; `HF_TOKEN` é opcional para o
  dataset público.

## Exigências do enunciado

- Entrega individual em PDF.
- Peso: 70% da nota final.
- O guia apresenta uma inconsistência: menciona 3--5 páginas na abertura e
  4--6 páginas nas diretrizes. Adotar 4--6 páginas como faixa segura.
- Formatação: Arial ou Times New Roman, 11 ou 12 pontos, espaçamento 1,15 ou
  1,5 e margens de 2,5 cm.
- Rubrica: problema (25%), adequação metodológica (35%), dados e governança
  (15%), impacto e limitações (15%) e estrutura/formatação (10%).

## Artefatos existentes

- `main.tex`: primeira versão completa do short paper.
- `referencias.bib`: bibliografia inicial.
- `analise_corpus_discursos.ipynb`: notebook executado com aquisição,
  auditoria, caracterização, chunking e baseline TF–IDF.
- `scripts/baixar_dados_hf.py`: download independente e registro de
  proveniência.
- `requirements.txt`: dependências Python.
- `latexmkrc`: compilação do artigo para `out/`.
- `resultados/`: CSVs e tabela LaTeX produzidos pelo notebook.
- `figuras/cobertura_temporal.{pdf,png}`: figura produzida pelo notebook.
- `dados/`: parquet e proveniência locais, ignorados pelo Git.
- `Guia e Orientações do Trabalho Final.pdf`: enunciado original.

## Resultados validados

- Dataset: 15.729 pronunciamentos e 30 colunas originais.
- Textos integrais disponíveis: 15.039 (95,61%).
- IDs duplicados: 0.
- Datas inválidas: 0.
- Partido ausente: 2.074 registros.
- UF ausente: 2.074 registros.
- Autores distintos: 1.794.
- Partidos distintos: 32.
- Período observado: 1º de fevereiro de 2019 a 10 de janeiro de 2023.
- Mediana do comprimento: 492 palavras; média: 761,2 palavras.
- Prova de conceito: mil documentos e 5.696 chunks, matriz TF–IDF limitada a
  50 mil termos.
- O notebook foi executado integralmente sem erro.
- O LaTeX foi compilado integralmente sem erro para `out/main.pdf`.
- O PDF atual tem três páginas e deverá chegar a 4--6 após incorporar resultados,
  tabela, figura e maior detalhamento metodológico.

## Pendências conhecidas

1. Preencher no artigo o e-mail e o órgão/área de atuação de Fabricio Santana.
2. Incorporar ao `main.tex` os resultados efetivos do notebook, evitando tratar
   resultados esperados como resultados já medidos.
3. Inserir a tabela de qualidade e a figura temporal no artigo.
4. Incluir um diagrama simples do pipeline proposto.
5. Definir um pequeno conjunto de perguntas e julgamentos de relevância para
   demonstrar como Recall@k e MRR seriam calculados; decidir se haverá avaliação
   empírica ou apenas protocolo proposto.
6. Revisar e ampliar as referências com fontes primárias e confirmar os dados
   bibliográficos antes da entrega.
7. Revisar criticamente LAI, LGPD, vieses, falsos positivos/negativos,
   abstenção e supervisão humana.
8. Ajustar o texto final para 4--6 páginas e realizar revisão visual do PDF.

## Comandos de retomada

```bash
cd /workspaces/mcdia/10-adap/assignments/final
python -m pip install -r requirements.txt
python scripts/baixar_dados_hf.py
jupyter nbconvert --to notebook --execute --inplace \
  analise_corpus_discursos.ipynb --ExecutePreprocessor.timeout=600
latexmk -pdf main.tex
```

Antes de alterar arquivos, verificar `git status` e preservar mudanças não
relacionadas existentes no repositório.

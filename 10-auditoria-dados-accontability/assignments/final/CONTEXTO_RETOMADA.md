# Contexto para retomada do trabalho final

Última atualização: 5 de setembro de 2026.

## Decisões tomadas

- O trabalho final da disciplina **Auditoria de Dados e Accountability com
  Python** será produzido como short paper em LaTeX.
- Todos os artefatos devem permanecer em `10-adap/assignments/final/`.
- Tema escolhido: proposta de uma solução RAG auditável para consulta e análise
  de discursos do Senado Federal.
- Título de trabalho: **Proposta de recuperação aumentada por geração para análise auditável
  de discursos do Senado Federal**.
- O corpus deve ser obtido diretamente do dataset público
  `fabriciosantana/discursos-senado-legislatura-56`, no Hugging Face.
- A solução deve ser apresentada como apoio à pesquisa, à transparência e à
  accountability. Não deve ser descrita como mecanismo autônomo para auditar
  parlamentares, verificar fatos ou inferir intenções.
- O notebook atual deve permanecer reproduzível sem serviços pagos ou chaves de
  API. O baseline é lexical, baseado em TF–IDF.
- Identificação informada: Fabricio Fernandes Santana, Coordenador de
  Informática Legislativa no Senado Federal, e-mail
  `fabricio.santana@gmail.com`.
- Caso sejam incorporados embeddings ou geração em nuvem, criar `.env` ignorado
  pelo Git. Chaves prováveis: `OPENAI_API_KEY`; `HF_TOKEN` é opcional para o
  dataset público.
- A integração de embeddings OpenAI foi preparada com
  `text-embedding-3-large`, 512 dimensões, checkpoints retomáveis e fusão RRF.
  O `.env` existe e está ignorado; a chave foi preenchida pelo usuário e a
  execução efetiva foi concluída.
- A avaliação de relevância será exclusivamente automática, por LLM como juiz.
  Não haverá etapa de avaliação humana; os rótulos não constituem padrão-ouro.

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
  auditoria, caracterização e demonstração de segmentação e TF–IDF sobre mil
  documentos; a comparação final dos três métodos ocorre no nível documental.
- `scripts/baixar_dados_hf.py`: download independente e registro de
  proveniência.
- `requirements.txt`: dependências Python.
- `latexmkrc`: compilação do artigo para `out/`.
- `scripts/verificar_consistencia_artigo.py`: validação dos principais números
  do texto contra os CSVs e o resumo do juiz.
- `CHECKLIST_ENTREGA.md`: conferência pela rubrica e instruções de submissão.
- `entrega/trabalho_final_fabricio_santana.pdf`: cópia limpa para submissão.
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
- Foi criada uma coleção inicial de dez consultas de localização de item
  conhecido em `avaliacao/perguntas_referencia.json`.
- Resultados do TF--IDF em dez consultas: Hit@1 = 0,20; Hit@5 = 0,40;
  Hit@10 = 0,40; MRR = 0,301; mediana do melhor rank = 17,5.
- Os resultados, a figura temporal e a tabela comparativa foram incorporados ao
  artigo, que passou a cinco páginas e permaneceu compilando sem erros.
- A bibliografia usa o estilo autor-data da ABNT, com citações em azul. Foram
  incorporadas referências da disciplina de Agostino et al. (2026; publicação
  antecipada on-line em 2025), para a
  relação entre ciência de dados e accountability pública, e Mökander (2023),
  para a definição de auditabilidade de sistemas de IA.

## Pendências conhecidas

1. Leitura final pelo autor antes da submissão.
2. A geração de respostas, a avaliação de fidelidade e a validação com usuários
   permanecem como próximos passos do projeto, não como partes executadas neste trabalho.

A revisão final distinguiu a segmentação demonstrativa (mil documentos e 5.696
trechos) da avaliação comparativa no nível documental (15.039 discursos),
explicitou o recorte do pool e dos excertos fornecidos ao LLM, delimitou o
R@10 do pool e registrou os riscos do envio de textos a uma API externa. O PDF
permanece com cinco páginas.

O planejamento da execução vetorial contabilizou 15.039 documentos, 10
perguntas, 19.926.075 tokens após truncamento explícito em 8.000 tokens por
documento, 104 documentos truncados e 101 lotes. Após informar a chave, executar
`python scripts/gerar_embeddings_openai.py` e, em seguida,
`python scripts/avaliar_recuperacao.py`.

A execução com `text-embedding-3-large` e 512 dimensões foi concluída. O cache
consolidado ocupa aproximadamente 18,1 MB. Resultados comparativos: TF--IDF
(Hit@1 0,20; Hit@5 0,40; Hit@10 0,40; MRR 0,301; mediana 17,5), OpenAI
(0,00; 0,30; 0,40; 0,112; 44,5) e híbrido RRF (0,10; 0,30; 0,50; 0,212;
11,5). O artigo e o notebook já incorporam a leitura crítica desses resultados.

Foi gerado um pool cego com a união dos dez primeiros resultados de TF--IDF,
OpenAI e híbrido para cada pergunta. Após deduplicação, há 205 pares em
`resultados/pool_avaliacao.xlsx`; a chave dos rankings está separada em
`pool_chave_metodos.csv`. O script `scripts/calcular_metricas_julgadas.py`
calcula Precision@5, Precision@10, recall dentro do pool, MRR e nDCG@10 com os
rótulos finais do LLM.

Foi executado julgamento cego com `gpt-5.4-mini-2026-03-17`: duas passagens por
item e adjudicação nos casos divergentes, de baixa confiança ou insuficientes.
Houve concordância exata de 62,9%, kappa ponderado quadrático de 0,690, 76
divergências e 136 adjudicações. Distribuição final: 43 itens com rótulo 0, 80
com rótulo 1 e 82 com rótulo 2. O consumo foi 455.893 tokens de entrada e
65.167 de saída. Com esses rótulos, o híbrido obteve Precision@5 0,92,
Precision@10 0,89, recall no pool 0,566 e nDCG@10 0,840. Por decisão
metodológica, não haverá validação humana. A concordância entre passagens mede
consistência interna, não validade externa, e o artigo registra essa limitação.

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

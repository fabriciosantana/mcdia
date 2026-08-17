# AGENTS.md

## Contexto do pre-projeto

- Este diretorio contem o pre-projeto de pesquisa da dissertacao de mestrado em Administracao Publica.
- O tema deriva do artigo em `../chatbot-rag/`, mas o texto deve ser tratado como proposta prospectiva de pesquisa, nao como repeticao do artigo da disciplina.
- O arquivo principal e `main.tex`.
- As secoes ficam em `sections/`.
- As referencias ficam em `references.bib`.
- O template institucional esta em `template/Template_pre_projeto.docx` e orienta capa, folha de rosto, estrutura, metodologia, cronograma e referencias.

## Enquadramento esperado

- Formular o trabalho como pre-projeto de dissertacao profissional.
- Preservar a relacao com administracao publica, transparencia, informacao legislativa, governanca de IA e avaliacao de sistemas RAG.
- Diferenciar claramente:
  - o que ja foi demonstrado no artigo `chatbot-rag`;
  - o que sera investigado de forma mais robusta na dissertacao;
  - o que depende de validacao humana, baseline, gold standard, ablação ou decisao institucional.
- Preferir proposicoes verificaveis e criterios de avaliacao a hipoteses causais fortes quando o desenho for construtivo e orientado a artefato.

## Regras de trabalho

- Seguir tambem o `AGENTS.md` da raiz do repositorio.
- Antes de editar, ler `main.tex`, as secoes afetadas e o contexto relevante de `../chatbot-rag/NOTAS_REVISAO.md`.
- Apos edicoes em LaTeX que afetem o PDF, compilar a partir deste diretorio com:

```bash
latexmk -pdf main.tex
```

- Verificar citacoes indefinidas, referencias quebradas, tabelas e avisos relevantes.
- Manter alteracoes incrementais e faceis de revisar.

## Retomada consolidada da redacao

Ultima contextualizacao registrada: junho de 2026, na branch `pre-projeto-dissertacao-rag`.

Arquivos e fontes ja lidos para contextualizacao:

- `main.tex`;
- `sections/01-introducao.tex`;
- `sections/02-referencial-teorico.tex`;
- `sections/03-hipoteses.tex`;
- `sections/04-metodologia.tex`;
- `sections/05-cronograma.tex`;
- `sections/06-referencias.tex`;
- `references.bib`;
- `../chatbot-rag/AGENTS.md`;
- `../chatbot-rag/NOTAS_REVISAO.md`;
- `../chatbot-rag/main.tex`;
- secoes centrais do artigo-base em `../chatbot-rag/sections/`, em especial resumo, introducao, experimentos e conclusao;
- slides de metodologia em `metodologia/IDP-MCDIA_PROJETO-CD-IA_AULA-1.pptx` e `metodologia/IDP-MCDIA_PROJETO-CD-IA_AULA-2.pptx`.

Diagnostico editorial atual:

- O pre-projeto ja esta estruturado como proposta prospectiva de dissertacao profissional, nao como mera repeticao do artigo da disciplina.
- A introducao ja apresenta tema, problema, pergunta de pesquisa, justificativa e objetivos.
- O referencial teorico esta organizado em torno de RAG, recuperacao de informacao, informacao legislativa, avaliacao e governanca publica de IA.
- A secao de hipoteses usa hipoteses de trabalho verificaveis, adequadas a uma pesquisa aplicada, multimetodos e orientada a artefato.
- A metodologia ja explicita natureza aplicada, carater exploratorio e descritivo, abordagem multimetodos, orientacao hipotetico-dedutiva com componente indutivo, pesquisa bibliografica, documental, estudo de caso aplicado, avaliacao controlada e dialogo com Design Science Research.
- A matriz metodologica ja esta alinhada ao modelo trabalhado na Aula 2, com objetivo especifico, abordagem, natureza, dados, publico-alvo, amostragem, tecnicas de coleta, tecnicas de analise e forma de apresentacao.
- A secao de recursos, viabilidade e transparencia no uso de IA ja cobre disponibilidade do corpus, infraestrutura computacional, avaliadores humanos, custos, registro de modelo, prompt, rubrica, configuracao e data de execucao.
- O cronograma ja cobre refinamento do problema, revisao, protocolo, corpus, bateria, qualificacao, execucao, avaliacao humana/LLM juiz, analise, redacao, deposito, defesa e artigo derivado.

Relacao com o artigo-base `../chatbot-rag/`:

- O artigo-base deve ser tratado como prova de conceito reprodutivel ja demonstrada, com bateria automatizada pequena, avaliacao por LLM como juiz, inspecao humana amostral e discussao de governanca.
- O pre-projeto deve transformar essa base em desenho mais robusto de dissertacao, incluindo bateria ampliada, gold standard, baseline de LLM sem recuperacao, baseline lexical, avaliacao formal da recuperacao, avaliacao humana independente, comparacao com LLM como juiz e discussao institucional das condicoes de uso.
- Evitar prometer como futuro o que o artigo-base ja demonstrou em escala preliminar; formular como ampliacao, aprofundamento, validacao ou robustecimento.
- Evitar apresentar os resultados do artigo-base como evidencias finais da dissertacao; eles funcionam como motivacao, prova de viabilidade e ponto de partida.

Pontos de alinhamento com as aulas de metodologia:

- A Aula 1 enfatiza conhecimento cientifico como sistematico, verificavel e falivel; teoria, hipoteses, variaveis, falseabilidade, estrutura ABNT do projeto, tema, problema, objetivos e tecnicas de analise de problemas.
- A Aula 2 enfatiza taxonomia metodologica, metodos de abordagem, natureza e forma de abordagem, metodos mistos, classificacao quanto aos objetivos, delineamentos, tecnicas de coleta, elaboracao e analise, matriz metodologica, ABNT e uso etico/transparente de IA.
- Para a banca, reforcar a coerencia interna `problema -> objetivos -> hipoteses -> metodologia`, pois esse ponto aparece explicitamente nas aulas.
- Como o desenho nao e um teste causal classico, manter a justificativa de que as hipoteses sao hipoteses de trabalho verificaveis e criterios de avaliacao do artefato.
- Preservar a secao de uso transparente de IA, pois a disciplina cobra explicitamente uso etico e transparente de ferramentas de IA na pesquisa academica.

Prioridades recomendadas para a proxima sessao:

1. Revisar a coerencia entre pergunta de pesquisa, objetivo geral, objetivos especificos, hipoteses e matriz metodologica.
2. Polir a metodologia para reduzir repeticoes e tornar mais visivel a ponte entre cada objetivo especifico e a evidencia empirica correspondente.
3. Verificar se a secao de hipoteses deve manter esse titulo ou receber uma formulacao explicativa mais forte, deixando claro que nao se trata de teste causal classico.
4. Conferir se o cronograma e realista para a entrega academica e para a futura dissertacao, especialmente quanto a avaliadores humanos, gold standard e baselines.
5. Fazer uma revisao final de aderencia ABNT/template: capa, folha de rosto, sumario, secoes textuais, matriz, fonte das tabelas, cronograma e referencias.
6. Apos edicoes substantivas, compilar com `latexmk -pdf main.tex` a partir de `chatbot-rag-pre/` e verificar o log.


# AGENTS.md

## Contexto do artigo

- Este diretorio contem um artigo academico em LaTeX sobre um chatbot RAG aplicado a discursos parlamentares do Senado Federal.
- O manuscrito deve ser tratado como uma prova de conceito reprodutivel, com potencial de evolucao para submissao a periodico.
- O backlog editorial operacional esta nas GitHub Issues do repositorio.
- O historico de revisao, o estado consolidado e o mapa estrategico herdado estao em `NOTAS_REVISAO.md`.

## Retomada de contexto

Antes de propor ou executar mudancas relevantes neste artigo, ler nesta ordem:

1. `NOTAS_REVISAO.md`
2. `main.tex`
3. As secoes diretamente afetadas em `sections/`
4. `chatbot-rag.bib`, quando houver citacoes ou referencias

Se o usuario pedir para continuar o plano sem indicar uma acao especifica, consultar primeiro as GitHub Issues abertas do artigo `chatbot-rag`. Se o acesso ao GitHub nao estiver disponivel, usar o mapa estrategico consolidado em `NOTAS_REVISAO.md`.

Se houver ambiguidade sobre o objetivo editorial, perguntar diretamente se a prioridade e fechar a versao de entrega academica ou preparar uma versao para submissao a periodico.

## Enquadramento e contribuicao

- Preservar o enquadramento atual como prova de conceito reprodutivel.
- Evitar transformar resultados preliminares em afirmacoes de validade ampla.
- Tratar o sistema RAG como solucao sociotecnica, nao apenas como integracao entre LLM e banco vetorial.
- Quando a revisao estiver orientada a periodico, considerar o enquadramento como *Design Science Research* e explicitar o artefato de design.
- Posicionar a contribuicao como protocolo reprodutivel para acervos legislativos em portugues, quando isso estiver sustentado pelo texto.
- Diferenciar o que e especifico do corpus de discursos do Senado Federal e o que pode ser transferido para outros acervos legislativos.
- Ao comparar com outros trabalhos, destacar corpus, idioma, jurisdicao, pipeline, avaliacao, abertura dos artefatos e diferenca em relacao ao protocolo deste artigo.

## Avaliacao e metodologia

- Distinguir avaliacao da recuperacao, avaliacao da geracao e avaliacao humana.
- Tratar LLM as a Judge como instrumento auxiliar sujeito a vieses, variacao de modelo e sensibilidade a rubrica.
- Registrar ameacas a validade, limites de generalizacao e dependencias da configuracao do Open WebUI.
- Ao fortalecer o artigo para periodico, priorizar baseline, ablation study, metricas de recuperacao, bateria ampliada de perguntas e protocolo de anotacao humana.
- Manter a conexao entre objetivos, criterios de sucesso, resultados e conclusao.
- Nao apresentar medias de avaliacao automatizada como prova isolada de qualidade; sempre relacionar os numeros a exemplos qualitativos, variacao entre rodadas, rubrica e validacao humana.
- Quando discutir erros ou divergencias entre juiz automatizado e avaliacao humana, tratar esses casos como achados metodologicos relevantes, nao apenas como falhas pontuais.

## Arquivos principais

- `main.tex` e o arquivo principal.
- As secoes ficam em `sections/`.
- As referencias ficam em `chatbot-rag.bib`.
- O PDF compilado fica em `out/main.pdf`.

## Plano e acompanhamento

- Usar GitHub Issues como backlog editorial operacional.
- Quando uma acao for iniciada, registrar progresso na issue correspondente.
- Quando uma acao for concluida, fechar a issue correspondente e registrar arquivos alterados, verificacao e pendencias.
- Atualizar `NOTAS_REVISAO.md` apenas quando a mudanca afetar o estado geral do manuscrito, o diagnostico consolidado ou o mapa estrategico.
- Nao marcar uma acao como concluida apenas por ter sido discutida.

## Compilacao

- Apos edicoes em LaTeX, recompilar a partir deste diretorio com `latexmk -pdf main.tex` quando a mudanca afetar o PDF.
- Verificar o log apos recompilacao, especialmente citacoes indefinidas, referencias quebradas, problemas de tabelas e avisos relevantes.

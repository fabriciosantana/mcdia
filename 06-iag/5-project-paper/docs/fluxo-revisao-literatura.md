# Fluxo auditavel de revisao de literatura

Este fluxo combina MCPs, skills e arquivos locais para tornar a revisao de literatura rastreavel.

## MCPs configurados

- `openalex`: busca e metadados de publicacoes academicas via OpenAlex.
- `github`: gestao do repositorio, issues, PRs e comentarios via GitHub MCP. Para o artigo `chatbot-rag`, as issues sao o backlog editorial operacional.

O MCP `github` usa a variavel de ambiente `GITHUB_PAT_TOKEN`. Nunca registrar tokens no repositorio.

## Skills relacionadas

- `.agents/skills/literature-review-workflow`: planejar busca, triagem, sintese e tabela comparativa.
- `.agents/skills/academic-latex-review`: revisar consistencia academica do texto.
- `.agents/skills/article-action-plan`: atualizar marcadores e notas de progresso.
- `.agents/skills/chatbot-rag-article`: aplicar regras especificas do artigo `chatbot-rag`.

## Artefatos locais recomendados por artigo

Dentro do diretorio de cada artigo, criar quando necessario:

- `literatura/PLANO_BUSCA.md`: escopo, perguntas, bases, criterios de inclusao/exclusao e strings de busca.
- `literatura/TRIAGEM.md`: trabalhos encontrados, decisao de inclusao, exclusao ou adiamento, e justificativa.
- `literatura/TABELA_COMPARATIVA.md`: comparacao dos trabalhos mais proximos.
- `literatura/NOTAS_LEITURA.md`: fichamentos curtos dos trabalhos incluidos.

## Campos minimos para triagem

Para cada trabalho avaliado, registrar:

- referencia curta;
- DOI, URL ou identificador OpenAlex/Semantic Scholar quando disponivel;
- fonte da busca;
- string ou criterio que levou ao trabalho;
- decisao: incluido, excluido ou adiado;
- justificativa curta;
- relacao com o artigo atual.

## Campos para tabela comparativa

Usar, no minimo:

- trabalho;
- corpus ou dados;
- idioma e jurisdicao;
- metodo ou pipeline;
- tipo de avaliacao;
- principais resultados;
- limitacoes;
- disponibilidade de artefatos;
- diferenca em relacao ao artigo atual.

## Sequencia de trabalho

1. Definir escopo em `literatura/PLANO_BUSCA.md`.
2. Buscar fontes com `openalex` e, se necessario, busca web complementar.
3. Registrar candidatos em `literatura/TRIAGEM.md`.
4. Atualizar o `.bib` apenas depois de verificar duplicatas.
5. Construir ou atualizar `literatura/TABELA_COMPARATIVA.md`.
6. Revisar a secao de literatura no LaTeX, conectando literatura, lacuna e contribuicao.
7. Atualizar o plano de acao e notas de revisao do artigo quando o estado geral mudar.
8. Usar GitHub Issues como backlog operacional e PRs para agrupar alteracoes revisaveis.

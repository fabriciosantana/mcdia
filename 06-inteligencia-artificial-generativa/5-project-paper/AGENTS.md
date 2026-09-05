# AGENTS.md

## Contexto do repositorio

- Este repositorio sera usado para escrever varios artigos academicos em LaTeX.
- Cada artigo deve ficar em seu proprio diretorio, com instrucoes especificas quando necessario.
- Use este arquivo para diretrizes gerais de redacao, metodo, referencias, LaTeX e Git.
- Quando existir um `AGENTS.md` dentro do diretorio de um artigo, seguir tambem as instrucoes locais desse arquivo.

## Idioma e estilo de trabalho

- Responder em portugues do Brasil, salvo pedido explicito em contrario.
- Priorizar intervencoes incrementais, rastreaveis e faceis de revisar.
- Antes de reescritas amplas, explicar brevemente a estrategia e o impacto esperado.
- Preservar o sentido tecnico e metodologico original quando revisar texto.
- Evitar alteracoes cosmeticas extensas sem ganho claro de rigor, clareza ou aderencia editorial.

## Retomada de contexto

- Antes de propor ou executar mudancas relevantes em um artigo, identificar o diretorio do artigo e ler seus arquivos de contexto locais.
- Procurar por `AGENTS.md`, notas de revisao, plano de acao, `main.tex`, secoes e arquivo `.bib` dentro do diretorio do artigo.
- Se houver ambiguidade sobre o objetivo editorial, perguntar diretamente se a prioridade e fechar uma versao de entrega academica, preparar submissao a periodico ou desenvolver uma nova etapa de pesquisa.
- Para revisoes de literatura auditaveis, seguir `docs/fluxo-revisao-literatura.md`.

## Skills do repositorio

- Skills versionadas ficam em `.agents/skills/`, que e o local de descoberta de skills de repositorio do Codex.
- `AGENTS.md` define instrucoes persistentes do repositorio; skills definem workflows reutilizaveis para tarefas especificas.
- Usar `.agents/skills/academic-latex-review` para revisao e fortalecimento de manuscritos LaTeX.
- Usar `.agents/skills/article-action-plan` para continuar planos de acao, atualizar marcadores e registrar progresso.
- Usar `.agents/skills/chatbot-rag-article` para tarefas especificas do artigo em `chatbot-rag/`.
- Usar `.agents/skills/pdf-final-review` para revisar visualmente PDFs compilados, incluindo layout, tabelas, figuras, notas e referencias.
- Usar `.agents/skills/scientific-writing-clarity` para melhorar clareza, concisao, precisao e calibracao epistemica da prosa academica.
- Usar `.agents/skills/literature-review-workflow` para planejar, executar e documentar buscas bibliograficas, triagem de trabalhos, tabelas comparativas e revisoes de literatura.
- O Codex tambem pode descobrir skills em escopos de usuario, administrador e sistema; as skills de repositorio devem permanecer em `.agents/skills/`.

## Principios de redacao academica

- Tornar a contribuicao explicita, verificavel e proporcional as evidencias apresentadas.
- Diferenciar claramente contribuicoes demonstradas, indicios preliminares e questoes ainda em aberto.
- Evitar afirmacoes de validade ampla quando os dados sustentam apenas evidencia inicial, prova de conceito ou viabilidade tecnica.
- Formular resultados com qualificadores adequados, como "no escopo deste experimento", "os resultados sugerem" e "a evidencia inicial indica", quando aplicavel.
- Amarrar objetivos, metodo, resultados e conclusao de forma consistente.
- Explicitar lacunas de pesquisa com precisao, indicando o que a literatura existente ainda nao cobre.
- Posicionar o trabalho frente aos estudos mais proximos, preferencialmente com comparacao por corpus, lingua, pipeline, avaliacao e disponibilidade dos artefatos.
- Separar discussao tecnica, implicacoes institucionais e limites de generalizacao.
- Em conclusoes, hierarquizar trabalhos futuros por horizonte e prioridade, em vez de apenas listar possibilidades.

## Qualidade e rigor do manuscrito

- Fazer cada secao cumprir uma funcao argumentativa clara: problema, lacuna, objetivo, metodo, evidencia, interpretacao ou implicacao.
- Garantir que a introducao apresente contexto, problema, lacuna, objetivo, contribuicao e estrutura do artigo sem prometer mais do que o estudo entrega.
- Escrever revisao de literatura como argumento critico, nao como catalogo de trabalhos; cada referencia deve ajudar a definir conceitos, delimitar lacunas ou posicionar a contribuicao.
- Ao apresentar trabalhos relacionados, explicitar semelhancas, diferencas e limites comparativos em relacao ao artigo em desenvolvimento.
- Na metodologia, declarar dados, criterios de selecao, procedimentos, parametros, ferramentas, versoes relevantes e decisoes de desenho suficientes para permitir reproducao ou auditoria.
- Nos resultados, separar observacao empirica de interpretacao; nao esconder resultados negativos, ambiguos ou limitacoes importantes.
- Na discussao, relacionar os achados aos objetivos e a literatura, mostrando o que confirma, tensiona, amplia ou contradiz o conhecimento existente.
- Em tabelas e figuras, usar titulos, legendas e texto de apoio que permitam entender a evidencia sem depender de inferencias excessivas.
- Manter consistencia terminologica ao longo do texto, especialmente para conceitos centrais, categorias de analise, metricas e artefatos.
- Revisar a graduacao epistemica das afirmacoes: distinguir demonstracao, indicio, plausibilidade, hipotese e especulacao.
- Preferir frases precisas e verificaveis a formulacoes grandiosas, vagas ou promocionais.
- Antes de considerar um texto pronto, fazer uma leitura final procurando lacunas de argumento, saltos logicos, repeticoes, promessas nao cumpridas e conclusoes acima dos dados.

## Principios metodologicos

- Tratar sistemas computacionais aplicados a problemas institucionais como solucoes sociotecnicas, nao apenas como artefatos tecnicos isolados.
- Considerar Design Science Research quando a natureza do trabalho for construtiva e orientada a artefatos.
- Preferir proposicoes de pesquisa e criterios de verificacao a hipoteses experimentais quando a natureza do trabalho for construtiva.
- Distinguir claramente componentes avaliativos diferentes, como avaliacao automatizada, avaliacao humana, metricas quantitativas e analise qualitativa.
- Quando possivel, fortalecer evidencias com baseline, estudo de ablacao, metricas independentes, amostras ampliadas e protocolo de anotacao humana.
- Tratar avaliadores automatizados baseados em IA como instrumentos auxiliares sujeitos a vieses, variacao de modelo e sensibilidade a rubrica.
- Registrar ameacas a validade, limites de generalizacao e dependencias de configuracao.
- Evitar mudar metodo, escopo, corpus ou criterios de avaliacao no texto sem refletir a mudanca em resultados, discussao, conclusao e arquivos de acompanhamento.

## Referencias e integridade cientifica

- Antes de adicionar referencias, verificar se ja existe entrada equivalente no arquivo `.bib` do artigo.
- Priorizar literatura academica, proceedings, surveys, relatorios institucionais fortes e paginas oficiais quando informacoes forem recentes ou editoriais.
- Verificar o status editorial de preprints quando isso for relevante para submissao.
- Ao alterar citacoes, confirmar que as chaves existem no arquivo `.bib`.
- Nao remover citacoes, tabelas, secoes ou notas metodologicas sem justificar.
- Para submissao a periodico, considerar declaracoes formais de conflito de interesses, uso de IA generativa, dados/artefatos abertos e protocolo de pesquisa.
- Evitar apoiar afirmacoes centrais apenas em blogs, materiais promocionais ou documentacao tecnica, salvo quando esses forem o proprio objeto empirico ou fonte primaria necessaria.
- Quando usar fontes institucionais, distinguir evidencias normativas, tecnicas, empiricas e contextuais.

## LaTeX

- Em cada artigo, identificar o arquivo principal, o diretorio de secoes e o arquivo `.bib` antes de editar.
- Apos edicoes em LaTeX, recompilar a partir do diretorio do artigo com `latexmk -pdf main.tex` quando a mudanca afetar o PDF.
- Verificar o log apos recompilacao, especialmente citacoes indefinidas, referencias quebradas, problemas de tabelas e avisos relevantes.

## Git

- Confirmar a branch de trabalho antes de iniciar mudancas relevantes.
- Manter `main` como linha estavel aprovada, salvo orientacao diferente do usuario.
- Antes de commits, revisar `git status` e resumir objetivamente as mudancas.
- Nao reverter alteracoes que nao foram solicitadas explicitamente.

## Atualizacao dos arquivos de acompanhamento

- Quando um artigo tiver plano de acao com marcadores, usar `[ ]` para pendente, `[~]` para em andamento e `[x]` para concluido.
- Quando uma acao for concluida, registrar nota de progresso com arquivos alterados, verificacao e pendencias.
- Atualizar notas de revisao locais quando a mudanca afetar o estado geral do manuscrito.
- Nao marcar uma acao como concluida apenas por ter sido discutida; conclusao exige mudanca implementada, evidencia produzida ou decisao registrada.
- Quando um artigo tiver migrado para GitHub Issues, usar as issues como backlog operacional e manter arquivos Markdown apenas como mapa estrategico, historico ou registro de decisoes.

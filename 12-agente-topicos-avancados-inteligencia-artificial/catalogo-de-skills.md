# Catálogo de skills do repositório

Este catálogo lista as 39 skills encontradas em `/workspaces/mcdia/.agents/skills`.

## Como a instalação funciona

Neste workspace, elas já estão instaladas porque o Codex procura skills em:

```text
/workspaces/mcdia/.agents/skills/<nome>/SKILL.md
```

Para instalar uma skill individualmente em outra instalação do Codex, copie a pasta correspondente para o diretório pessoal de skills, normalmente `~/.codex/skills/`:

```bash
mkdir -p ~/.codex/skills/<nome>
cp -R /workspaces/mcdia/.agents/skills/<nome>/* ~/.codex/skills/<nome>/
```

Depois, reinicie ou recarregue o Codex. A invocação normalmente usa `/nome`; skills marcadas como `disable-model-invocation` precisam ser chamadas explicitamente pelo usuário.

As linhas abaixo mostram o comando individual de cada skill. Substitua `~/.codex/skills` pelo diretório de skills da sua instalação, se necessário.

## Fluxo principal: ideia → entrega

| Skill | O que faz | Instalação individual |
|---|---|---|
| `grill-with-docs` | Entrevista rigorosa para amadurecer uma ideia, registrando glossário e ADRs. | `cp -R /workspaces/mcdia/.agents/skills/grill-with-docs ~/.codex/skills/` |
| `prototype` | Cria um protótipo descartável para responder uma dúvida de design, estado ou UI. | `cp -R /workspaces/mcdia/.agents/skills/prototype ~/.codex/skills/` |
| `handoff` | Salva um resumo portátil para continuar o trabalho em outra sessão ou diretório. | `cp -R /workspaces/mcdia/.agents/skills/handoff ~/.codex/skills/` |
| `to-spec` | Converte a conversa atual em uma especificação publicada no issue tracker. | `cp -R /workspaces/mcdia/.agents/skills/to-spec ~/.codex/skills/` |
| `to-tickets` | Divide uma especificação em tickets tracer-bullet com bloqueios explícitos. | `cp -R /workspaces/mcdia/.agents/skills/to-tickets ~/.codex/skills/` |
| `implement` | Implementa uma especificação ou conjunto de tickets. | `cp -R /workspaces/mcdia/.agents/skills/implement ~/.codex/skills/` |
| `implement-spec` | Implementa uma especificação já fornecida, normalmente com tickets associados. | `cp -R /workspaces/mcdia/.agents/skills/implement-spec ~/.codex/skills/` |
| `tdd` | Conduz desenvolvimento test-first no ciclo red → green → refactor. | `cp -R /workspaces/mcdia/.agents/skills/tdd ~/.codex/skills/` |
| `code-review` | Revisa uma mudança desde um ponto fixo nos eixos Standards e Spec. | `cp -R /workspaces/mcdia/.agents/skills/code-review ~/.codex/skills/` |

Fluxo recomendado:

```text
/grill-with-docs → /to-spec → /to-tickets → /implement → /code-review
```

Use `/prototype` e `/handoff` quando uma questão precisar de um experimento separado. O `implement` usa TDD internamente e termina com revisão de código.

## On-ramps: entradas para problemas diferentes

| Skill | O que faz | Instalação individual |
|---|---|---|
| `triage` | Classifica issues e PRs recebidos, verifica contexto e produz briefs prontos para agentes. | `cp -R /workspaces/mcdia/.agents/skills/triage ~/.codex/skills/` |
| `diagnosing-bugs` | Diagnostica bugs difíceis e regressões com um loop reproduzível e teste de regressão. | `cp -R /workspaces/mcdia/.agents/skills/diagnosing-bugs ~/.codex/skills/` |
| `wayfinder` | Mapeia grandes esforços em tickets de decisão até o caminho de implementação ficar claro. | `cp -R /workspaces/mcdia/.agents/skills/wayfinder ~/.codex/skills/` |
| `improve-codebase-architecture` | Encontra oportunidades de aprofundamento arquitetural e produz relatório visual para escolher uma. | `cp -R /workspaces/mcdia/.agents/skills/improve-codebase-architecture ~/.codex/skills/` |

Use `triage` para demandas que chegaram de fora. Use `diagnosing-bugs` para algo quebrado; não o use apenas para construir uma feature nova.

## Vocabulário e design

| Skill | O que faz | Instalação individual |
|---|---|---|
| `domain-modeling` | Define termos do domínio, resolve ambiguidades e registra decisões em `CONTEXT.md` ou ADRs. | `cp -R /workspaces/mcdia/.agents/skills/domain-modeling ~/.codex/skills/` |
| `codebase-design` | Usa o vocabulário de módulos profundos, interfaces, seams, adapters e testabilidade. | `cp -R /workspaces/mcdia/.agents/skills/codebase-design ~/.codex/skills/` |
| `grilling` | Faz uma entrevista em rodadas para expor decisões, premissas e dependências. | `cp -R /workspaces/mcdia/.agents/skills/grilling ~/.codex/skills/` |

`grill-with-docs` combina `grilling` e `domain-modeling`; `codebase-design` apoia TDD e melhoria arquitetural.

## Skills standalone

| Skill | O que faz | Instalação individual |
|---|---|---|
| `ask-matt` | Escolhe a skill ou o fluxo adequado para a situação. | `cp -R /workspaces/mcdia/.agents/skills/ask-matt ~/.codex/skills/` |
| `grill-me` | Faz a entrevista de planejamento sem criar documentação persistente. | `cp -R /workspaces/mcdia/.agents/skills/grill-me ~/.codex/skills/` |
| `research` | Investiga uma pergunta em fontes primárias e registra achados citados em Markdown. | `cp -R /workspaces/mcdia/.agents/skills/research ~/.codex/skills/` |
| `resolving-merge-conflicts` | Resolve conflitos de merge/rebase por intenção e fonte primária, sem usar abort automático. | `cp -R /workspaces/mcdia/.agents/skills/resolving-merge-conflicts ~/.codex/skills/` |
| `to-questionnaire` | Cria questionários para obter decisões ou informações que outra pessoa possui. | `cp -R /workspaces/mcdia/.agents/skills/to-questionnaire ~/.codex/skills/` |
| `wizard` | Gera um assistente Bash para passos que somente um humano pode executar. | `cp -R /workspaces/mcdia/.agents/skills/wizard ~/.codex/skills/` |
| `teach` | Ensina um conceito ou skill em múltiplas sessões com estado no workspace. | `cp -R /workspaces/mcdia/.agents/skills/teach ~/.codex/skills/` |
| `wait-what` | Reexplica a última resposta em linguagem simples quando ela não foi compreendida. | `cp -R /workspaces/mcdia/.agents/skills/wait-what ~/.codex/skills/` |
| `claude-handoff` | Entrega a conversa a um agente em background para continuar o trabalho. | `cp -R /workspaces/mcdia/.agents/skills/claude-handoff ~/.codex/skills/` |
| `loop-me` | Faz uma entrevista persistente focada em especificar workflows do workspace. | `cp -R /workspaces/mcdia/.agents/skills/loop-me ~/.codex/skills/` |
| `lavish` | Converte planos, tabelas, diagramas e relatórios em HTML revisável. | `cp -R /workspaces/mcdia/.agents/skills/lavish ~/.codex/skills/` |
| `retro` | Faz retrospectiva de uma sessão e sugere melhorias no ambiente do agente. | `cp -R /workspaces/mcdia/.agents/skills/retro ~/.codex/skills/` |
| `writing-for-agents` | Orienta a escrita de skills, `AGENTS.md`, `CLAUDE.md` e documentos consumidos por agentes. | `cp -R /workspaces/mcdia/.agents/skills/writing-for-agents ~/.codex/skills/` |
| `writing-fragments` | Explora material bruto de escrita sem impor estrutura prematura. | `cp -R /workspaces/mcdia/.agents/skills/writing-fragments ~/.codex/skills/` |
| `writing-beats` | Organiza material de escrita em uma sequência de beats com termos fundamentados. | `cp -R /workspaces/mcdia/.agents/skills/writing-beats ~/.codex/skills/` |
| `writing-shape` | Dá forma ao material bruto em artigo, parágrafo a parágrafo. | `cp -R /workspaces/mcdia/.agents/skills/writing-shape ~/.codex/skills/` |

## Skills de setup, migração e infraestrutura

| Skill | O que faz | Instalação individual |
|---|---|---|
| `setup-matt-pocock-skills` | Configura tracker, labels de triagem e layout de documentação exigidos pelas outras skills. | `cp -R /workspaces/mcdia/.agents/skills/setup-matt-pocock-skills ~/.codex/skills/` |
| `setup-pre-commit` | Configura Husky, lint-staged, Prettier, typecheck e testes no pre-commit. | `cp -R /workspaces/mcdia/.agents/skills/setup-pre-commit ~/.codex/skills/` |
| `setup-ts-deep-modules` | Configura dependency-cruiser para reforçar módulos profundos em TypeScript. | `cp -R /workspaces/mcdia/.agents/skills/setup-ts-deep-modules ~/.codex/skills/` |
| `scaffold-exercises` | Cria estruturas de exercícios, problemas, soluções e explicadores com lint. | `cp -R /workspaces/mcdia/.agents/skills/scaffold-exercises ~/.codex/skills/` |
| `migrate-to-shoehorn` | Substitui asserções `as` em testes por `@total-typescript/shoehorn`. | `cp -R /workspaces/mcdia/.agents/skills/migrate-to-shoehorn ~/.codex/skills/` |
| `git-guardrails-claude-code` | Configura hooks para bloquear comandos Git perigosos, como push e reset destrutivo. | `cp -R /workspaces/mcdia/.agents/skills/git-guardrails-claude-code ~/.codex/skills/` |

## Invocação rápida

```text
/ask-matt
/setup-matt-pocock-skills
/grill-with-docs
/research teste de software com IA
/diagnosing-bugs descreva o bug
/tdd implemente comportamento X
/code-review revise desde main
/teach quero aprender testes
```

## Ordem recomendada para um projeto novo

1. `/setup-matt-pocock-skills`
2. `/grill-with-docs`
3. `/to-spec`
4. `/to-tickets`
5. `/implement`
6. `/code-review`

Para uma ideia muito grande, comece com `/wayfinder`. Para um bug difícil, comece com `/diagnosing-bugs`. Para pesquisa, use `/research`; para aprendizagem, `/teach`.

## Observação sobre instalação externa

As skills do repositório são pastas locais. Skills de outros repositórios ou do catálogo do Codex devem ser instaladas com a skill `skill-installer` ou pelo mecanismo de plugins correspondente; copiar uma pasta local não instala automaticamente dependências externas, hooks ou plugins.

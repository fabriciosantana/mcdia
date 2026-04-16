# Plano de Melhorias

Este arquivo consolida a lista priorizada de melhorias do projeto para acompanhamento de execucao.

## Como usar

- Atualize o campo `Status` de cada item conforme o andamento.
- Quando uma tarefa for concluida, registre a data e um resumo curto da decisao tomada.
- Se surgir uma dependencia nova, adicione em `Bloqueios/Dependencias`.
- Sempre que possivel, vincule o item a um commit, branch ou execucao de avaliacao.

## Legenda de status

- `todo`: ainda nao iniciado
- `doing`: em andamento
- `done`: concluido
- `blocked`: aguardando dependencia ou decisao

## Prioridade 1 - Reprodutibilidade do pipeline

**Objetivo**

Garantir que qualquer pessoa consiga reconstruir a base, importar os artefatos e repetir as avaliacoes a partir deste repositorio, sem depender de caminhos antigos ou estado implicito do ambiente.

**Impacto esperado**

- Reduz risco de inconsistencias entre ambientes.
- Facilita demonstracao, manutencao e entrega do projeto.
- Cria base confiavel para as proximas melhorias.

**Status geral**

- Status: `todo`
- Responsavel: a definir
- Bloqueios/Dependencias: nenhum

### Tarefa 1.1 - Corrigir metadados de geracao para refletirem o workspace atual

- Prioridade: alta
- Status: `todo`
- Arquivos principais:
  - [scripts/build_openwebui_knowledge_from_hf.py](/workspaces/mcdia/05-iag/4-project/scripts/build_openwebui_knowledge_from_hf.py:72)
  - [knowledge_openwebui/build_metadata.json](/workspaces/mcdia/05-iag/4-project/knowledge_openwebui/build_metadata.json:1)
- Problema atual:
  - O arquivo versionado aponta `jsonl_path` e `markdown_dir` para outro workspace (`/workspaces/mcdia/05-iag/2-rag/...`), o que prejudica a confianca na reproducao.
- Implementacao:
  - Revisar a geracao do objeto `metadata`.
  - Gravar caminhos absolutos corretos do ambiente atual.
  - Adicionar tambem caminhos relativos ao diretorio do projeto, para facilitar portabilidade.
  - Regenerar os artefatos apos o ajuste.
- Criterios de aceite:
  - `build_metadata.json` aponta apenas para caminhos do repositorio atual.
  - O arquivo inclui caminhos relativos ou outra forma portavel de referencia.
  - A regeneracao nao altera contagens esperadas sem justificativa.
- Evidencias a registrar:
  - comando executado
  - diff do arquivo
  - contagens finais de linhas, chunks e batches

### Tarefa 1.2 - Congelar dependencias dos scripts auxiliares

- Prioridade: alta
- Status: `todo`
- Arquivos principais:
  - [README.md](/workspaces/mcdia/05-iag/4-project/README.md:168)
  - novo arquivo sugerido: `requirements.txt` ou `pyproject.toml`
- Problema atual:
  - O projeto documenta instalacao por `pip install ...`, mas nao fixa versoes.
- Implementacao:
  - Escolher entre `requirements.txt` enxuto ou `pyproject.toml`.
  - Fixar pelo menos as bibliotecas usadas diretamente:
    - `pandas`
    - `pyarrow`
    - `huggingface_hub`
    - `requests`
    - `chromadb`
    - `pytest` se a suite de testes for adicionada
  - Atualizar README com o fluxo de instalacao oficial.
- Criterios de aceite:
  - Existe um arquivo de dependencias versionado.
  - O README referencia apenas o fluxo oficial novo.
  - Um ambiente limpo consegue instalar tudo sem ambiguidade.
- Evidencias a registrar:
  - arquivo criado
  - comando de instalacao validado

### Tarefa 1.3 - Padronizar o fluxo operacional no README

- Prioridade: alta
- Status: `todo`
- Arquivos principais:
  - [README.md](/workspaces/mcdia/05-iag/4-project/README.md:1)
  - [knowledge_openwebui/README_IMPORT.md](/workspaces/mcdia/05-iag/4-project/knowledge_openwebui/README_IMPORT.md:1)
- Implementacao:
  - Consolidar uma trilha unica:
    - preparar ambiente
    - gerar knowledge
    - importar knowledge
    - executar avaliacao
  - Explicitar precondicoes e saidas esperadas.
  - Remover duplicacao ou divergencia entre README principal e README de importacao.
- Criterios de aceite:
  - Existe uma sequencia unica e clara de comandos.
  - O leitor consegue executar o projeto sem deduzir passos faltantes.

### Tarefa 1.4 - Automatizar comandos recorrentes

- Prioridade: media
- Status: `todo`
- Arquivos principais:
  - novo arquivo sugerido: `Makefile`
- Implementacao:
  - Criar alvos como:
    - `make setup`
    - `make build-knowledge`
    - `make import-knowledge`
    - `make eval`
    - `make test`
  - Manter os comandos simples e documentados no README.
- Criterios de aceite:
  - Os alvos executam os fluxos principais com poucos argumentos.
  - O README mostra exemplos de uso.

## Prioridade 2 - Testes automatizados dos scripts

**Objetivo**

Proteger o nucleo do projeto contra regressao em parsing, chunking, importacao e avaliacao.

**Impacto esperado**

- Mais seguranca para refatorar.
- Menor risco de quebrar o pipeline com mudancas pequenas.
- Base melhor para evolucao continua.

**Status geral**

- Status: `todo`
- Responsavel: a definir
- Bloqueios/Dependencias:
  - definicao do framework de testes

### Tarefa 2.1 - Criar suite de testes para o builder

- Prioridade: alta
- Status: `todo`
- Arquivos principais:
  - [scripts/build_openwebui_knowledge_from_hf.py](/workspaces/mcdia/05-iag/4-project/scripts/build_openwebui_knowledge_from_hf.py:12)
  - novo diretorio sugerido: `tests/`
- Cobertura minima:
  - `normalize_text`
  - `chunk_words`
  - `choose_text`
  - validacao de `max_words > overlap_words`
- Casos de teste sugeridos:
  - texto vazio
  - texto curto
  - texto longo com overlap
  - fallback de `TextoDiscursoIntegral` para `Resumo`
  - ausencia total de texto
- Criterios de aceite:
  - Os principais helpers do builder estao cobertos.
  - Casos de borda mais provaveis passam em ambiente limpo.

### Tarefa 2.2 - Criar suite de testes para o avaliador

- Prioridade: alta
- Status: `todo`
- Arquivos principais:
  - [scripts/run_rag_eval.py](/workspaces/mcdia/05-iag/4-project/scripts/run_rag_eval.py:69)
- Cobertura minima:
  - `extract_answer`
  - `parse_json_object`
  - `coerce_score`
  - `build_prompt_from_template`
- Casos de teste sugeridos:
  - payload estilo OpenAI com `choices`
  - payload com `message`
  - resposta JSON com lixo antes/depois
  - score invalido
  - score fora da faixa `0-2`
- Criterios de aceite:
  - O parser de avaliacao se comporta de forma previsivel em respostas imperfeitas do juiz.

### Tarefa 2.3 - Criar testes para o importador

- Prioridade: alta
- Status: `todo`
- Arquivos principais:
  - [scripts/import_batches_to_openwebui.py](/workspaces/mcdia/05-iag/4-project/scripts/import_batches_to_openwebui.py:30)
- Cobertura minima:
  - `load_dotenv`
  - filtro `--start-from`
  - `is_openai_rate_limit_error`
  - retry com backoff
- Implementacao:
  - Usar mocks para chamadas HTTP.
  - Evitar dependencia de instancias reais do Open WebUI nos testes.
- Criterios de aceite:
  - O fluxo de retry e os filtros de arquivos podem ser validados localmente.

### Tarefa 2.4 - Integrar execucao dos testes ao fluxo normal

- Prioridade: media
- Status: `todo`
- Arquivos principais:
  - `Makefile` ou README
- Implementacao:
  - Adicionar comando padrao `pytest`.
  - Opcionalmente criar alvo `make test`.
- Criterios de aceite:
  - Existe um comando unico para rodar a suite.

## Prioridade 3 - Observabilidade e rastreabilidade da execucao

**Objetivo**

Melhorar visibilidade sobre tempos, falhas, volume processado e resultados por etapa.

**Status geral**

- Status: `todo`
- Responsavel: a definir
- Bloqueios/Dependencias: nenhum

### Tarefa 3.1 - Substituir `print` por logging estruturado nos scripts

- Prioridade: alta
- Status: `todo`
- Arquivos principais:
  - [scripts/import_batches_to_openwebui.py](/workspaces/mcdia/05-iag/4-project/scripts/import_batches_to_openwebui.py:160)
  - [scripts/run_rag_eval.py](/workspaces/mcdia/05-iag/4-project/scripts/run_rag_eval.py:281)
- Implementacao:
  - Adotar modulo `logging`.
  - Padronizar niveis:
    - `INFO` para progresso
    - `WARNING` para retries
    - `ERROR` para falhas
  - Incluir identificadores de item processado no log.
- Criterios de aceite:
  - Logs ficam legiveis e consistentes.
  - Falhas podem ser localizadas sem inspecionar o codigo.

### Tarefa 3.2 - Registrar duracao por etapa e resumo final

- Prioridade: alta
- Status: `todo`
- Implementacao:
  - Medir inicio e fim da execucao total.
  - Medir tempo por arquivo importado.
  - Medir tempo por pergunta avaliada.
  - Salvar um `run_summary.json` com estatisticas da execucao.
- Criterios de aceite:
  - Cada execucao gera um resumo reutilizavel.
  - O tempo total e os gargalos ficam visiveis.

### Tarefa 3.3 - Padronizar saidas de artefatos operacionais

- Prioridade: media
- Status: `todo`
- Implementacao:
  - Definir pasta e nome padrao para logs e resumos.
  - Evitar espalhar evidencias em varios lugares sem convencao.
- Criterios de aceite:
  - Um operador sabe exatamente onde procurar logs, resumo e resultados.

## Prioridade 4 - Classificacao da origem do conteudo indexado

**Objetivo**

Separar claramente chunks oriundos de texto integral, resumo ou indexacao para melhorar diagnostico de qualidade do retrieval.

**Status geral**

- Status: `todo`
- Responsavel: a definir
- Bloqueios/Dependencias:
  - ajuste no builder

### Tarefa 4.1 - Alterar selecao de texto para retornar conteudo e origem

- Prioridade: alta
- Status: `todo`
- Arquivos principais:
  - [scripts/build_openwebui_knowledge_from_hf.py](/workspaces/mcdia/05-iag/4-project/scripts/build_openwebui_knowledge_from_hf.py:41)
- Implementacao:
  - Transformar `choose_text` para retornar tambem a origem:
    - `texto_integral`
    - `resumo`
    - `indexacao`
  - Ajustar o loop principal para persistir essa informacao.
- Criterios de aceite:
  - Todo chunk passa a carregar o campo `text_source`.

### Tarefa 4.2 - Persistir origem nos artefatos gerados

- Prioridade: alta
- Status: `todo`
- Implementacao:
  - Incluir `text_source` no JSONL.
  - Incluir `Origem do texto` nos batches Markdown.
  - Atualizar documentacao dos artefatos.
- Criterios de aceite:
  - Um revisor consegue identificar facilmente a natureza do texto indexado.

### Tarefa 4.3 - Usar a origem nas analises de qualidade

- Prioridade: media
- Status: `todo`
- Implementacao:
  - Relacionar respostas ruins com a origem dos chunks recuperados.
  - Identificar se respostas problemáticas dependem mais de `Resumo` ou `Indexacao`.
- Criterios de aceite:
  - Pelo menos um relatorio passa a cruzar desempenho com `text_source`.

## Prioridade 5 - Separar avaliacao de retrieval e geracao

**Objetivo**

Diagnosticar se os erros estao na recuperacao do contexto, na qualidade da resposta ou em ambos.

**Status geral**

- Status: `todo`
- Responsavel: a definir
- Bloqueios/Dependencias:
  - entendimento do payload retornado pelo Open WebUI em cada modo

### Tarefa 5.1 - Extrair e salvar sinais de retrieval por pergunta

- Prioridade: alta
- Status: `todo`
- Arquivos principais:
  - [scripts/run_rag_eval.py](/workspaces/mcdia/05-iag/4-project/scripts/run_rag_eval.py:357)
- Implementacao:
  - Ler `sources` e outros campos do payload salvo no JSONL.
  - Persistir indicadores como:
    - quantidade de fontes
    - autores presentes
    - links presentes
    - possivel foco em um unico autor ou mistura indevida
- Criterios de aceite:
  - O JSONL ou CSV contem campos adicionais de retrieval.

### Tarefa 5.2 - Criar metricas simples de retrieval

- Prioridade: alta
- Status: `todo`
- Implementacao:
  - Definir heuristicas iniciais, por exemplo:
    - `retrieval_has_expected_author`
    - `retrieval_source_count`
    - `retrieval_author_mix_risk`
  - Nao precisa ser perfeito; precisa ser util para diagnostico.
- Criterios de aceite:
  - O time consegue diferenciar resposta ruim por falta de contexto de resposta ruim por sintese ruim.

### Tarefa 5.3 - Incorporar os novos sinais ao relatorio final

- Prioridade: media
- Status: `todo`
- Implementacao:
  - Expandir CSV e Markdown de resultados.
  - Manter a rubrica existente sem substituir o que ja funciona.
- Criterios de aceite:
  - O relatorio final passa a mostrar qualidade de retrieval e de answer quality lado a lado.

## Prioridade 6 - Refinamento de chunking

**Objetivo**

Melhorar foco semantico dos chunks e reduzir mistura de argumentos ou autores em perguntas mais sensiveis.

**Status geral**

- Status: `todo`
- Responsavel: a definir
- Bloqueios/Dependencias:
  - baseline reprodutivel

### Tarefa 6.1 - Executar experimento comparativo de tamanhos de chunk

- Prioridade: alta
- Status: `todo`
- Parametros sugeridos:
  - atual: `850 / 150`
  - experimento A: `650 / 120`
  - experimento B: `500 / 100`
- Implementacao:
  - Gerar knowledge separada por configuracao.
  - Reexecutar o conjunto de perguntas de avaliacao.
  - Comparar media, minimo e perguntas mais afetadas.
- Criterios de aceite:
  - Existe uma comparacao objetiva entre configuracoes.

### Tarefa 6.2 - Avaliar chunking mais estrutural

- Prioridade: media
- Status: `todo`
- Implementacao:
  - Investigar divisao por blocos de discurso, cabecalho, apartes ou marcadores textuais.
  - Preservar simplicidade; nao introduzir heuristica fragil sem ganho mensuravel.
- Criterios de aceite:
  - Ha pelo menos uma proposta clara de chunking semantico para teste futuro.

## Prioridade 7 - Robustez da importacao

**Objetivo**

Tornar a ingestao retomavel, menos manual e menos vulneravel a falhas intermitentes.

**Status geral**

- Status: `todo`
- Responsavel: a definir
- Bloqueios/Dependencias: nenhum

### Tarefa 7.1 - Adicionar checkpoint de importacao

- Prioridade: alta
- Status: `todo`
- Arquivos principais:
  - [scripts/import_batches_to_openwebui.py](/workspaces/mcdia/05-iag/4-project/scripts/import_batches_to_openwebui.py:217)
- Implementacao:
  - Criar `import_state.json`.
  - Registrar sucesso, falha, numero de tentativas e `file_id`.
  - Permitir retomada automatica.
- Criterios de aceite:
  - Uma importacao interrompida pode continuar do ponto correto.

### Tarefa 7.2 - Criar modo `resume`

- Prioridade: alta
- Status: `todo`
- Implementacao:
  - Adicionar flag de linha de comando para retomar importacao anterior.
  - Pular arquivos ja marcados como concluidos.
- Criterios de aceite:
  - Nao e necessario controlar retomada manualmente por nome de arquivo.

### Tarefa 7.3 - Melhorar rastreio de falhas por arquivo

- Prioridade: media
- Status: `todo`
- Implementacao:
  - Persistir mensagem de erro por arquivo.
  - Destacar falhas recuperaveis vs. permanentes.
- Criterios de aceite:
  - O operador sabe exatamente quais arquivos falharam e por que.

## Prioridade 8 - Endurecimento da configuracao e da infraestrutura

**Objetivo**

Reduzir divergencias entre ambiente local, hibrido e cloud.

**Status geral**

- Status: `todo`
- Responsavel: a definir
- Bloqueios/Dependencias:
  - decisao sobre perfil padrao de execucao

### Tarefa 8.1 - Alinhar `.env.example` com `docker-compose.yaml`

- Prioridade: alta
- Status: `todo`
- Arquivos principais:
  - [.env.example](/workspaces/mcdia/05-iag/4-project/.env.example:1)
  - [docker-compose.yaml](/workspaces/mcdia/05-iag/4-project/docker-compose.yaml:1)
- Implementacao:
  - Revisar se todas as variaveis relevantes do compose estao documentadas.
  - Revisar defaults de modelos entre compose e `.env.example`.
- Criterios de aceite:
  - Nao ha variavel operacional importante ausente da documentacao.

### Tarefa 8.2 - Reduzir dependencia de `network_mode: host`

- Prioridade: media
- Status: `todo`
- Implementacao:
  - Testar exposicao explicita de portas.
  - Manter modo host apenas como alternativa documentada, se necessario.
- Criterios de aceite:
  - Existe ao menos um perfil de execucao mais portavel do que o atual.

### Tarefa 8.3 - Validar configuracao antes de rodar pipelines

- Prioridade: media
- Status: `todo`
- Implementacao:
  - Criar validacao inicial das variaveis obrigatorias.
  - Falhar cedo com mensagens claras.
- Criterios de aceite:
  - Erros de configuracao aparecem antes de chamadas longas ou custosas.

## Prioridade 9 - Governanca dos resultados de avaliacao

**Objetivo**

Transformar execucoes isoladas em historico comparavel de qualidade.

**Status geral**

- Status: `todo`
- Responsavel: a definir
- Bloqueios/Dependencias:
  - padronizacao minima dos resultados

### Tarefa 9.1 - Consolidar comparacao entre rodadas de avaliacao

- Prioridade: alta
- Status: `todo`
- Arquivos principais:
  - `eval/results/`
  - [eval-openwebui/RESULTS.md](/workspaces/mcdia/05-iag/4-project/eval-openwebui/RESULTS.md:1)
- Implementacao:
  - Criar script para ler todos os CSVs.
  - Comparar media, minimo, maximo e perguntas mais problemáticas.
- Criterios de aceite:
  - Existe um resumo unico da evolucao do sistema ao longo do tempo.

### Tarefa 9.2 - Identificar categorias mais frageis

- Prioridade: media
- Status: `todo`
- Implementacao:
  - Agrupar resultados por `category`.
  - Destacar recorrencia de falhas em:
    - `comparison`
    - `author_focus`
    - `hallucination_check`
    - outras categorias com pior comportamento
- Criterios de aceite:
  - O time sabe onde concentrar refinamentos de prompt e retrieval.

### Tarefa 9.3 - Automatizar atualizacao do relatorio de resultados

- Prioridade: media
- Status: `todo`
- Implementacao:
  - Criar script como `scripts/summarize_eval_results.py`.
  - Atualizar `eval-openwebui/RESULTS.md` automaticamente.
- Criterios de aceite:
  - O relatorio deixa de depender de manutencao manual.

## Prioridade 10 - Preparacao para operacao continua

**Objetivo**

Deixar o projeto mais proximo de um fluxo recorrente de uso, nao apenas de um experimento pontual.

**Status geral**

- Status: `todo`
- Responsavel: a definir
- Bloqueios/Dependencias:
  - melhorias anteriores de reproducao e observabilidade

### Tarefa 10.1 - Criar preflight check unificado

- Prioridade: alta
- Status: `todo`
- Arquivos candidatos:
  - [scripts/test_chroma_connection.py](/workspaces/mcdia/05-iag/4-project/scripts/test_chroma_connection.py:1)
  - [scripts/test_chroma_cloud_client.py](/workspaces/mcdia/05-iag/4-project/scripts/test_chroma_cloud_client.py:1)
  - novo script sugerido: `scripts/preflight_check.py`
- Implementacao:
  - Validar:
    - variaveis obrigatorias
    - conectividade com Chroma
    - disponibilidade do Open WebUI
    - existencia da knowledge base esperada
- Criterios de aceite:
  - O operador consegue validar o ambiente antes de rodar importacao ou avaliacao.

### Tarefa 10.2 - Definir rotina de atualizacao da base

- Prioridade: media
- Status: `todo`
- Implementacao:
  - Decidir se a base e:
    - reconstruida integralmente
    - atualizada incrementalmente
  - Documentar quando reindexar e como comparar versoes.
- Criterios de aceite:
  - Existe uma politica minima de manutencao da knowledge base.

### Tarefa 10.3 - Registrar criterios de "pronto para uso"

- Prioridade: media
- Status: `todo`
- Implementacao:
  - Definir thresholds minimos de qualidade, por exemplo:
    - media minima de score
    - minimo aceitavel por pergunta
    - ausencia de falhas em categorias criticas
- Criterios de aceite:
  - O time tem um criterio objetivo para aceitar ou recusar uma nova configuracao.

## Proposta de sequenciamento por sprint

## Sprint 1

- Prioridade 1 - Reprodutibilidade do pipeline
- Prioridade 2 - Testes automatizados
- Prioridade 3 - Observabilidade basica

## Sprint 2

- Prioridade 4 - Origem do conteudo indexado
- Prioridade 7 - Robustez da importacao
- Prioridade 9 - Governanca dos resultados

## Sprint 3

- Prioridade 5 - Separar retrieval e geracao
- Prioridade 6 - Refinamento de chunking
- Prioridade 8 - Endurecimento de configuracao e infraestrutura
- Prioridade 10 - Preparacao para operacao continua

## Registro de decisoes

Use esta secao para anotar escolhas importantes feitas ao longo da execucao do plano.

| Data | Item | Decisao | Observacoes |
|---|---|---|---|
| a preencher | a preencher | a preencher | a preencher |

## Registro de execucao

Use esta secao para resumir entregas realizadas.

| Data | Item concluido | Evidencia | Observacoes |
|---|---|---|---|
| a preencher | a preencher | a preencher | a preencher |

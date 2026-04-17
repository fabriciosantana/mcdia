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

## Diretriz metodologica vigente

- Protocolo escolhido: `Opcao A`
- Definicao:
  - A bateria automatizada deve reproduzir o mais fielmente possivel o comportamento do fluxo interativo do Open WebUI.
  - Isso inclui alinhar a estrutura de prompt, a knowledge utilizada, os parametros de execucao e o formato da rodada experimental.
- Implicacao pratica:
  - Nao basta trocar o arquivo de prompt padrao no script.
  - O protocolo de avaliacao deve refletir a mesma logica efetiva do fluxo RAG usado manualmente no Open WebUI, com diferencas residuais explicitamente documentadas.

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
- Status: `doing`
- Arquivos principais:
  - [README.md](/workspaces/mcdia/05-iag/4-project/README.md:1)
  - [knowledge_openwebui/README_IMPORT.md](/workspaces/mcdia/05-iag/4-project/knowledge_openwebui/README_IMPORT.md:1)
- Implementacao:
  - Consolidar uma trilha unica:
    - preparar ambiente
    - gerar knowledge
    - importar knowledge
    - executar avaliacao
    - registrar configuracao da rodada
  - Explicitar precondicoes e saidas esperadas.
  - Remover duplicacao ou divergencia entre README principal e README de importacao.
- Criterios de aceite:
  - Existe uma sequencia unica e clara de comandos.
  - O leitor consegue executar o projeto sem deduzir passos faltantes.

### Tarefa 1.5 - Versionar explicitamente a configuracao de cada rodada experimental

- Prioridade: alta
- Status: `done`
- Arquivos principais:
  - [scripts/run_rag_eval.py](/workspaces/mcdia/05-iag/4-project/scripts/run_rag_eval.py:281)
  - `eval/results/`
- Problema atual:
  - Parte da configuracao final de uma rodada esta espalhada entre `.env`, Open WebUI, prompts e argumentos de CLI.
- Implementacao:
  - Salvar um arquivo `run_config_<timestamp>.json` ou equivalente em `eval/results/`.
  - Registrar no minimo:
    - modelo gerador
    - modelo juiz
    - prompt de geracao efetivamente usado
    - prompt do juiz
    - rubrica usada
    - `knowledge_name`
    - `knowledge_id`
    - data/hora de execucao
    - conjunto de perguntas utilizado
    - parametros de geracao relevantes, incluindo `temperature`, `top_p`, `max_tokens` e `seed`, se disponiveis
  - Registrar fingerprints ou hashes dos artefatos da knowledge base usados na rodada.
- Criterios de aceite:
  - Cada rodada gera um arquivo de configuracao proprio.
  - Um terceiro consegue reconstruir a configuracao experimental sem depender de memoria operacional.

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
  - Incluir identificadores da rodada e ponteiros para o `run_config`.
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
    - numero de chunks ou segmentos retornados por resposta, quando disponivel
    - numero de arquivos-fonte unicos por resposta
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
- Status: `doing`
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
  - Comparar tambem variacao entre rodadas teoricamente identicas.
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
  - Incluir referencias cruzadas para `run_config` e `run_summary`.
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

## Prioridade 11 - Fortalecimento metodologico da avaliacao

**Objetivo**

Transformar a avaliacao do projeto em um protocolo de pesquisa reproduzivel, comparavel e defensavel metodologicamente.

**Impacto esperado**

- Aumenta a comparabilidade entre uso interativo e bateria automatizada.
- Fortalece a defesa do experimento no manuscrito.
- Reduz ambiguidade sobre o que exatamente foi avaliado em cada rodada.

**Status geral**

- Status: `todo`
- Responsavel: a definir
- Bloqueios/Dependencias:
  - Prioridade 1 minimamente avancada
  - Prioridade 9 minimamente avancada

### Tarefa 11.1 - Implementar o protocolo A de alinhamento com o Open WebUI

- Prioridade: alta
- Status: `done`
- Arquivos principais:
  - [scripts/run_rag_eval.py](/workspaces/mcdia/05-iag/4-project/scripts/run_rag_eval.py:77)
  - [eval/prompts/rag_prompt.md](/workspaces/mcdia/05-iag/4-project/eval/prompts/rag_prompt.md:1)
  - [eval/prompts/rag_answer_system.md](/workspaces/mcdia/05-iag/4-project/eval/prompts/rag_answer_system.md:1)
- Problema atual:
  - O fluxo automatizado usa um `system_prompt` simples e a pergunta como `user`, enquanto o uso interativo do Open WebUI pode operar com uma formulacao RAG mais rica e com estrutura diferente.
- Implementacao:
  - Definir qual e a estrutura real do prompt no Open WebUI para o modelo RAG avaliado.
  - Adaptar o `run_rag_eval.py` para espelhar essa estrutura o mais fielmente possivel.
  - Se necessario, separar:
    - template de sistema
    - template de usuario
    - configuracao de anexacao da collection
  - Nao apenas trocar o default para `rag_prompt.md` sem adaptacao estrutural.
  - Documentar qualquer diferenca residual que nao possa ser eliminada.
- Criterios de aceite:
  - O protocolo automatizado e descritivamente equivalente ao fluxo interativo do Open WebUI.
  - A diferenca entre uso manual e bateria automatizada fica minimizada e explicitamente registrada.

### Tarefa 11.2 - Rerodar a bateria com o protocolo alinhado

- Prioridade: alta
- Status: `done`
- Implementacao:
  - Executar nova rodada completa apos o alinhamento do protocolo A.
  - Salvar resultados em novo conjunto de artefatos.
  - Comparar com a melhor rodada anterior.
- Criterios de aceite:
  - Existe ao menos uma rodada completa produzida ja sob o protocolo A.

### Tarefa 11.3 - Executar rodadas identicas e medir estabilidade

- Prioridade: alta
- Status: `done`
- Implementacao:
  - Executar pelo menos 3 rodadas identicas com:
    - mesma knowledge base
    - mesmo prompt
    - mesmos modelos
    - mesmos parametros de geracao
    - mesmo conjunto de perguntas
  - Medir:
    - media total por rodada
    - minimo por rodada
    - variacao por pergunta
    - variacao das `review_notes`
  - Registrar se houve mudanca relevante nas respostas ou no julgamento.
- Criterios de aceite:
  - Existe um relatorio de estabilidade da avaliacao.
  - A variacao entre rodadas identicas esta quantificada.

### Tarefa 11.4 - Separar gerador e juiz em pelo menos uma rodada controlada

- Prioridade: alta
- Status: `todo`
- Implementacao:
  - Executar ao menos dois cenarios:
    - gerador e juiz com o mesmo modelo
    - gerador e juiz com modelos diferentes
  - Comparar notas agregadas e por pergunta.
  - Avaliar se a mudanca de juiz altera materialmente o resultado.
- Criterios de aceite:
  - Ha evidencia objetiva para discutir a robustez do `LLM as a Judge`.

### Tarefa 11.5 - Congelar a knowledge base usada na avaliacao

- Prioridade: alta
- Status: `todo`
- Arquivos principais:
  - [knowledge_openwebui/build_metadata.json](/workspaces/mcdia/05-iag/4-project/knowledge_openwebui/build_metadata.json:1)
  - [knowledge_openwebui/discursos_chunks.jsonl](/workspaces/mcdia/05-iag/4-project/knowledge_openwebui/discursos_chunks.jsonl:1)
  - `knowledge_openwebui/md_batches/`
- Implementacao:
  - Registrar `knowledge_id` em toda rodada.
  - Confirmar que a collection nao foi reindexada entre rodadas comparadas.
  - Manter snapshot dos artefatos usados.
  - Se possivel, registrar hash ou fingerprint dos artefatos.
- Criterios de aceite:
  - Rodadas comparadas usam comprovadamente a mesma knowledge base.

### Tarefa 11.6 - Enriquecer a saida sintetica por pergunta

- Prioridade: media
- Status: `todo`
- Implementacao:
  - Criar uma etapa de pos-processamento para gerar, por pergunta:
    - qualidade da recuperacao
    - fidelidade ao contexto
    - presenca correta de referencias
    - principal limite observado
  - Aproveitar `review_notes` e sinais de retrieval ja extraidos.
  - Produzir uma matriz curta para uso no manuscrito.
- Criterios de aceite:
  - Cada pergunta possui uma leitura analitica sintetica alem da nota numerica.

### Tarefa 11.7 - Expandir a bateria com melhor balanceamento por categoria

- Prioridade: media
- Status: `todo`
- Arquivos principais:
  - [eval/discursos_questions.json](/workspaces/mcdia/05-iag/4-project/eval/discursos_questions.json:1)
- Implementacao:
  - Aumentar o numero de perguntas por familia.
  - Garantir pelo menos 2 ou 3 perguntas por categoria critica, especialmente:
    - autoria cruzada
    - ampla
    - comparacao
    - checagem de alucinacao
    - multietapas
  - Versionar explicitamente o conjunto de perguntas.
- Criterios de aceite:
  - O benchmark deixa de ter categorias criticas subrepresentadas.

### Tarefa 11.8 - Incluir validacao manual amostral

- Prioridade: media
- Status: `todo`
- Implementacao:
  - Selecionar 5 a 7 respostas da rodada final.
  - Fazer revisao humana parcial.
  - Comparar julgamento humano versus LLM Judge.
  - Registrar convergencias e divergencias.
- Criterios de aceite:
  - O experimento final inclui triangulacao entre avaliacao automatica e avaliacao humana amostral.

### Tarefa 11.9 - Transformar a avaliacao em protocolo reproduzivel formal

- Prioridade: alta
- Status: `todo`
- Implementacao:
  - Definir um roteiro fixo da rodada:
    - regenerar ou confirmar base
    - validar ingestao
    - confirmar prompt
    - executar bateria
    - executar julgamento
    - gerar CSV/MD/JSONL
    - gerar resumo analitico
  - Registrar este roteiro no README e nos artefatos de configuracao da rodada.
- Criterios de aceite:
  - Existe um protocolo operacional e metodologico claro para repetir a avaliacao.

## Proposta de sequenciamento por sprint

## Sprint 1

- Prioridade 1 - Reprodutibilidade do pipeline
- Prioridade 2 - Testes automatizados
- Prioridade 3 - Observabilidade basica
- Prioridade 11 - Fortalecimento metodologico da avaliacao, etapa de desenho do protocolo A

## Sprint 2

- Prioridade 4 - Origem do conteudo indexado
- Prioridade 7 - Robustez da importacao
- Prioridade 9 - Governanca dos resultados
- Prioridade 11 - Execucao das primeiras rodadas controladas

## Sprint 3

- Prioridade 5 - Separar retrieval e geracao
- Prioridade 6 - Refinamento de chunking
- Prioridade 8 - Endurecimento de configuracao e infraestrutura
- Prioridade 10 - Preparacao para operacao continua
- Prioridade 11 - Validacao manual, balanceamento do benchmark e protocolo final

## Registro de decisoes

Use esta secao para anotar escolhas importantes feitas ao longo da execucao do plano.

| Data | Item | Decisao | Observacoes |
|---|---|---|---|
| 2026-04-16 | Diretriz metodologica | Adotada a Opcao A para a avaliacao | A bateria automatizada deve espelhar o mais fielmente possivel o fluxo interativo do Open WebUI. |
| a preencher | a preencher | a preencher | a preencher |

## Registro de execucao

Use esta secao para resumir entregas realizadas.

| Data | Item concluido | Evidencia | Observacoes |
|---|---|---|---|
| 2026-04-16 | Base inicial do protocolo A e versionamento de rodada | [scripts/run_rag_eval.py](/workspaces/mcdia/05-iag/4-project/scripts/run_rag_eval.py:368) | Prompt padrao alterado para `eval/prompts/rag_prompt.md`; suporte a `temperature`, `top_p`, `max_tokens` e `seed`; novo `run_config` com knowledge_id, prompts e fingerprints. |
| 2026-04-16 | Estrutura de mensagens mais fiel ao Open WebUI | [scripts/run_rag_eval.py](/workspaces/mcdia/05-iag/4-project/scripts/run_rag_eval.py:78) | No protocolo A, o default passou a ser `--answer-prompt-role=none`, enviando apenas a pergunta do usuario e deixando o Open WebUI aplicar o `RAG_TEMPLATE` configurado no servidor. |
| 2026-04-16 | Rodada oficial completa sob o protocolo A | [rag_eval_20260416T172816Z.csv](/workspaces/mcdia/05-iag/4-project/eval/results/rag_eval_20260416T172816Z.csv:1) | Execucao completa com 20/20 perguntas `ok`, media 9.15, minimo 6, maximo 10, com configuracao versionada em `rag_eval_20260416T172816Z.run_config.json`. |
| 2026-04-16 | Diagnostico e correcao do erro 400 no juiz automatico | [scripts/run_rag_eval.py](/workspaces/mcdia/05-iag/4-project/scripts/run_rag_eval.py:109) | O script passou a incluir o corpo de erro do `/api/chat/completions` nas excecoes HTTP e a chamada do juiz deixou de enviar `seed` e parametros extras que estavam gerando `400 Bad Request`. |
| 2026-04-16 | Parametros experimentais padronizados como `RAG_EVAL_*` | [scripts/run_rag_eval.py](/workspaces/mcdia/05-iag/4-project/scripts/run_rag_eval.py:463) | `RAG_EVAL_TEMPERATURE`, `RAG_EVAL_TOP_P`, `RAG_EVAL_MAX_TOKENS` e `RAG_EVAL_SEED` foram adicionados ao `.env`, `.env.example` e README como defaults da bateria, sem confundir configuracao experimental com configuracao global do Open WebUI. |
| 2026-04-17 | Tres rodadas completas para analise inicial de estabilidade | [rag_eval_20260416T172816Z.csv](/workspaces/mcdia/05-iag/4-project/eval/results/rag_eval_20260416T172816Z.csv:1) | Rodadas completas: `172816Z` media 9.15, `182240Z` media 9.55 e `232921Z` media 9.35; todas com 20/20 perguntas `ok` e mesma configuracao experimental versionada. |
| 2026-04-17 | Variacao entre rodadas identicas quantificada | [rag_eval_20260416T232921Z.csv](/workspaces/mcdia/05-iag/4-project/eval/results/rag_eval_20260416T232921Z.csv:1) | Variacao observada em perguntas como `q15`, `q16`, `q18` e `q19`, indicando estabilidade operacional alta, mas sensibilidade metodologica relevante em parte do benchmark. |
| a preencher | a preencher | a preencher | a preencher |

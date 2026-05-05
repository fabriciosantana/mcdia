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

- Status: `doing`
- Responsavel: a definir
- Bloqueios/Dependencias: nenhum

### Tarefa 1.1 - Corrigir metadados de geracao para refletirem o workspace atual

- Prioridade: alta
- Status: `done`
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
- Resultado observado:
  - O builder passou a registrar `project_root`, caminhos absolutos do workspace atual e caminhos relativos portaveis para o JSONL e o diretorio de batches Markdown.
  - O `build_metadata.json` foi regenerado e deixou de apontar para `/workspaces/mcdia/05-iag/2-rag/...`.
  - A regeneracao manteve as contagens esperadas: `15729` linhas de entrada, `15726` linhas escritas, `3` linhas puladas, `23806` chunks e `120` batches Markdown.
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
- Status: `done`
- Arquivos principais:
  - [README.md](/workspaces/mcdia/05-iag/4-project/README.md:168)
  - [requirements.txt](/workspaces/mcdia/05-iag/4-project/requirements.txt:1)
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
- Resultado observado:
  - Foi adotado um `requirements.txt` enxuto com as dependencias diretas usadas pelos scripts.
  - O `README.md` passou a referenciar `pip install -r requirements.txt` como fluxo oficial de instalacao.
  - O arquivo foi validado com `python -m pip install --dry-run -r requirements.txt`.
- Criterios de aceite:
  - Existe um arquivo de dependencias versionado.
  - O README referencia apenas o fluxo oficial novo.
  - Um ambiente limpo consegue instalar tudo sem ambiguidade.
- Evidencias a registrar:
  - arquivo criado
  - comando de instalacao validado

### Tarefa 1.3 - Padronizar o fluxo operacional no README

- Prioridade: alta
- Status: `done`
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
- Resultado observado:
  - O `README.md` passou a conter uma trilha unica e resumida de execucao de ponta a ponta.
  - O `README` principal tornou-se a unica fonte operacional de verdade; o `knowledge_openwebui/README_IMPORT.md` foi removido para evitar duplicacao e drift documental.
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

- Status: `done`
- Responsavel: Codex
- Bloqueios/Dependencias: nenhum

### Tarefa 2.1 - Criar suite de testes para o builder

- Prioridade: alta
- Status: `done`
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
- Resultado observado:
  - Foi criada uma suite `pytest` para os helpers do builder em `tests/test_build_openwebui_knowledge_from_hf.py`.
  - A cobertura inicial valida normalizacao de texto, chunking com overlap, rejeicao de overlap invalido, selecao preferencial de texto e fallback para `Resumo`/`Indexacao`.
- Criterios de aceite:
  - Os principais helpers do builder estao cobertos.
  - Casos de borda mais provaveis passam em ambiente limpo.

### Tarefa 2.2 - Criar suite de testes para o avaliador

- Prioridade: alta
- Status: `done`
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
- Resultado observado:
  - Foi criada uma suite `pytest` para os helpers do avaliador em `tests/test_run_rag_eval.py`.
  - A cobertura inicial valida extracao de respostas, parsing de JSON com texto antes/depois, coercao da escala `0-2`, preenchimento de templates e montagem de mensagens por modo de prompt.
- Criterios de aceite:
  - O parser de avaliacao se comporta de forma previsivel em respostas imperfeitas do juiz.

### Tarefa 2.3 - Criar testes para o importador

- Prioridade: alta
- Status: `done`
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
- Resultado observado:
  - Foi criada uma suite `pytest` para helpers do importador em `tests/test_import_batches_to_openwebui.py`.
  - A cobertura inicial valida carregamento de `.env`, preservacao de variaveis ja definidas, filtro semantico de `--start-from`, deteccao de rate limit da OpenAI e retry com mocks, sem depender de instancia real do Open WebUI.
- Criterios de aceite:
  - O fluxo de retry e os filtros de arquivos podem ser validados localmente.

### Tarefa 2.4 - Integrar execucao dos testes ao fluxo normal

- Prioridade: media
- Status: `done`
- Arquivos principais:
  - `Makefile` ou README
- Implementacao:
  - Adicionar comando padrao `pytest`.
  - Opcionalmente criar alvo `make test`.
- Resultado observado:
  - Foi adicionado `pytest==9.0.2` ao `requirements.txt`.
  - Foi criado `pytest.ini` para padronizar descoberta da suite.
  - O README passou a documentar `pytest` como comando padrao de validacao local.
  - A suite inicial executou com `25 passed`.
- Criterios de aceite:
  - Existe um comando unico para rodar a suite.

## Prioridade 3 - Observabilidade e rastreabilidade da execucao

**Objetivo**

Melhorar visibilidade sobre tempos, falhas, volume processado e resultados por etapa.

**Status geral**

- Status: `done`
- Responsavel: a definir
- Bloqueios/Dependencias: nenhum

### Tarefa 3.1 - Substituir `print` por logging estruturado nos scripts

- Prioridade: alta
- Status: `done`
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
- Resultado:
  - O `scripts/run_rag_eval.py` passou a usar `logging` para progresso, retries e falhas.
  - O `scripts/import_batches_to_openwebui.py` tambem passou a usar `logging` para progresso, retries de rate limit, falhas e resumo final.

### Tarefa 3.2 - Registrar duracao por etapa e resumo final

- Prioridade: alta
- Status: `done`
- Implementacao:
  - Medir inicio e fim da execucao total.
  - Medir tempo por arquivo importado.
  - Medir tempo por pergunta avaliada.
  - Salvar um `run_summary.json` com estatisticas da execucao.
  - Incluir identificadores da rodada e ponteiros para o `run_config`.
- Criterios de aceite:
  - Cada execucao gera um resumo reutilizavel.
  - O tempo total e os gargalos ficam visiveis.
- Resultado:
  - O avaliador passou a registrar `duration_seconds` por pergunta no JSONL/CSV.
  - Cada rodada do avaliador passa a gerar `eval/results/*.run_summary.json` com contagens, estatisticas de nota, tempos e ponteiros para os artefatos da rodada.
  - O importador passou a registrar duracao por batch e gerar `knowledge_openwebui/import_summary_<timestamp>.json` com contagens, filtros aplicados, falhas e tempos por arquivo.

### Tarefa 3.3 - Padronizar saidas de artefatos operacionais

- Prioridade: media
- Status: `done`
- Implementacao:
  - Definir pasta e nome padrao para logs e resumos.
  - Evitar espalhar evidencias em varios lugares sem convencao.
- Criterios de aceite:
  - Um operador sabe exatamente onde procurar logs, resumo e resultados.
- Resultado:
  - Resumos de avaliacao ficam em `eval/results/*.run_summary.json`.
  - Resumos de importacao ficam em `knowledge_openwebui/import_summary_<timestamp>.json`.
  - Logs operacionais sao emitidos no console com niveis `INFO`, `WARNING` e `ERROR`, e podem ser detalhados com `--verbose`.

## Prioridade 4 - Classificacao da origem do conteudo indexado

**Objetivo**

Separar claramente chunks oriundos de texto integral, resumo ou indexacao para melhorar diagnostico de qualidade do retrieval.

**Status geral**

- Status: `done_com_4_3_deferida`
- Responsavel: a definir
- Bloqueios/Dependencias:
  - nenhum para o escopo de metadado de controle

**Decisao metodologica**

O campo `text_source` deve ser tratado como metadado de controle e auditoria, nao como eixo analitico central neste momento. A regeneracao da base mostrou distribuicao fortemente desbalanceada: `23119` chunks de `texto_integral`, `687` de `resumo` e `0` de `indexacao`. Isso confirma que a base e majoritariamente composta por texto integral e que uma analise extensa por origem tende a agregar pouco valor experimental agora. O valor principal da mudanca e documentar os fallbacks e evitar ambiguidade metodologica futura.

### Tarefa 4.1 - Alterar selecao de texto para retornar conteudo e origem

- Prioridade: alta
- Status: `done`
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
- Resultado:
  - `choose_text` passou a retornar o texto escolhido e a origem (`texto_integral`, `resumo` ou `indexacao`).
  - O loop principal usa essa origem para cada chunk gerado.

### Tarefa 4.2 - Persistir origem nos artefatos gerados

- Prioridade: alta
- Status: `done`
- Implementacao:
  - Incluir `text_source` no JSONL.
  - Incluir `Origem do texto` nos batches Markdown.
  - Atualizar documentacao dos artefatos.
- Criterios de aceite:
  - Um revisor consegue identificar facilmente a natureza do texto indexado.
- Resultado:
  - O JSONL passou a incluir `text_source` no registro do chunk e nos metadados.
  - Os batches Markdown passaram a exibir `Origem do texto`.
  - O `build_metadata.json` passou a consolidar `text_source_counts`.

### Tarefa 4.3 - Usar a origem nas analises de qualidade

- Prioridade: baixa
- Status: `deferred`
- Implementacao:
  - Relacionar respostas ruins com a origem dos chunks recuperados.
  - Identificar se respostas problemáticas dependem mais de `Resumo` ou `Indexacao`.
- Criterios de aceite:
  - Pelo menos um relatorio passa a cruzar desempenho com `text_source`.
- Decisao:
  - Nao priorizar agora, pois a distribuicao de origem e muito desbalanceada e quase toda a base vem de `texto_integral`.
  - Retomar apenas se uma rodada futura mostrar falhas concentradas nos `687` chunks de `resumo` ou se a composicao da knowledge base mudar.

**Proximo foco recomendado**

Avancar para uma frente com maior impacto experimental:

- Prioridade 11 - Preparar uma rodada experimental ampliada com bateria mais diversa.
- Prioridade 9 - Consolidar governanca dos resultados quando houver novas rodadas.
- Prioridade 6 - Refinar chunking apenas depois de evidencia clara da bateria ampliada.

## Prioridade 5 - Separar avaliacao de retrieval e geracao

**Objetivo**

Diagnosticar se os erros estao na recuperacao do contexto, na qualidade da resposta ou em ambos.

**Status geral**

- Status: `done`
- Responsavel: a definir
- Bloqueios/Dependencias:
  - nenhum para a primeira versao heuristica baseada em `sources`

### Tarefa 5.1 - Extrair e salvar sinais de retrieval por pergunta

- Prioridade: alta
- Status: `done`
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
- Resultado:
  - O avaliador passou a extrair sinais do payload `sources` retornado pelo Open WebUI.
  - Cada linha da rodada passa a incluir contagens de entries, chunks, arquivos unicos, scores, links e autores detectados.

### Tarefa 5.2 - Criar metricas simples de retrieval

- Prioridade: alta
- Status: `done`
- Implementacao:
  - Definir heuristicas iniciais, por exemplo:
    - `retrieval_has_expected_author`
    - `retrieval_source_count`
    - `retrieval_author_mix_risk`
  - Nao precisa ser perfeito; precisa ser util para diagnostico.
- Criterios de aceite:
  - O time consegue diferenciar resposta ruim por falta de contexto de resposta ruim por sintese ruim.
- Resultado:
  - Foram adicionadas heuristicas iniciais:
    - `retrieval_has_expected_author`
    - `retrieval_author_mix_risk`
    - `retrieval_source_entries`
    - `retrieval_chunk_count`
    - `retrieval_unique_file_count`
  - Campos incertos sao marcados como `unknown`, evitando falsa precisao quando a pergunta ou o payload nao sustentam inferencia.

### Tarefa 5.3 - Incorporar os novos sinais ao relatorio final

- Prioridade: media
- Status: `done`
- Implementacao:
  - Expandir CSV e Markdown de resultados.
  - Manter a rubrica existente sem substituir o que ja funciona.
- Criterios de aceite:
  - O relatorio final passa a mostrar qualidade de retrieval e de answer quality lado a lado.
- Resultado:
  - CSV, Markdown e `run_summary.json` passaram a expor sinais de retrieval ao lado das notas da rubrica.
  - A rubrica existente foi mantida sem alteracao; os novos campos funcionam como diagnostico complementar.

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

- Status: `done`
- Responsavel: a definir
- Bloqueios/Dependencias: nenhum

### Tarefa 7.1 - Adicionar checkpoint de importacao

- Prioridade: alta
- Status: `done`
- Arquivos principais:
  - [scripts/import_batches_to_openwebui.py](/workspaces/mcdia/05-iag/4-project/scripts/import_batches_to_openwebui.py:217)
- Implementacao:
  - Criar `import_state.json`.
  - Registrar sucesso, falha, numero de tentativas e `file_id`.
  - Permitir retomada automatica.
- Criterios de aceite:
  - Uma importacao interrompida pode continuar do ponto correto.
- Resultado:
  - O importador passou a manter `knowledge_openwebui/import_state.json`.
  - O estado registra `status`, `attempts`, `file_id`, hash SHA-256, tamanho, erro e `knowledge_id` por batch.
  - O checkpoint e atualizado apos `uploaded`, `processed`, `added` e `failed`.

### Tarefa 7.2 - Criar modo `resume`

- Prioridade: alta
- Status: `done`
- Implementacao:
  - Adicionar flag de linha de comando para retomar importacao anterior.
  - Pular arquivos ja marcados como concluidos.
- Criterios de aceite:
  - Nao e necessario controlar retomada manualmente por nome de arquivo.
- Resultado:
  - Foi adicionada a flag `--resume`.
  - Batches ja marcados como `added` sao pulados automaticamente quando `knowledge_id` e SHA-256 coincidem.
  - A retomada continua compativel com `--start-from` e `--limit`.

### Tarefa 7.3 - Melhorar rastreio de falhas por arquivo

- Prioridade: media
- Status: `done`
- Implementacao:
  - Persistir mensagem de erro por arquivo.
  - Destacar falhas recuperaveis vs. permanentes.
- Criterios de aceite:
  - O operador sabe exatamente quais arquivos falharam e por que.
- Resultado:
  - Falhas passam a ser persistidas no estado com mensagem de erro e numero de tentativas.
  - `import_summary_<timestamp>.json` passa a apontar para o `import_state.json` e contabilizar importados, falhos, pulados por resume e dry-run.
  - Foi adicionado `--dry-run` para revisar o plano de importacao sem chamar a API.
  - Foram adicionados `--sleep-between-files` e retries com backoff para arquivos cujo processamento assíncrono termina com `status=failed`, mitigando `429` do endpoint de embeddings observado nos logs do Open WebUI.
  - A reimportacao da knowledge `Discursos do plenário do Senado 2019-2023 (v2)` foi concluida com `120/120` batches marcados como `added` e `0` falhas no estado local.

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
- Status: `done`
- Arquivos principais:
  - [.env.example](/workspaces/mcdia/05-iag/4-project/.env.example:1)
  - [docker-compose.yaml](/workspaces/mcdia/05-iag/4-project/docker-compose.yaml:1)
- Implementacao:
  - Revisar se todas as variaveis relevantes do compose estao documentadas.
  - Revisar defaults de modelos entre compose e `.env.example`.
- Resultado observado:
  - Todas as variaveis interpoladas no `docker-compose.yaml` passaram a existir explicitamente no `.env.example`.
  - Foram adicionadas e documentadas as variaveis `DOCLING_MAX_WORKERS`, `CHROMA_HTTP_HEADERS` e `WEBUI_TIMEOUT`.
  - O default de `OPENAI_MODEL` no `docker-compose.yaml` foi alinhado para `gpt-5.4-nano`, em coerencia com `.env.example` e `README.md`.
  - A configuracao final foi validada com `docker compose config`.
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
- Status: `done`
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
- Status: `doing`
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
- Status: `done`
- Implementacao:
  - Executar ao menos dois cenarios:
    - gerador e juiz com o mesmo modelo
    - gerador e juiz com modelos diferentes
  - Comparar notas agregadas e por pergunta.
  - Avaliar se a mudanca de juiz altera materialmente o resultado.
- Resultado observado:
  - `gemma3:12b` como juiz foi operacionalmente instavel e retornou respostas nulas em parte da bateria, inviabilizando seu uso como juiz confiavel no protocolo atual.
  - `gemma4:31b` foi operacionalmente estavel como gerador e como juiz, mas produziu `10/10` em toda a bateria tanto no cenario `gemma4 -> gemma4` quanto no cenario `gpt-5.4-nano -> gemma4`, sugerindo um perfil de julgamento excessivamente leniente.
- Criterios de aceite:
  - Ha evidencia objetiva para discutir a robustez do `LLM as a Judge`.

### Tarefa 11.5 - Congelar a knowledge base usada na avaliacao

- Prioridade: alta
- Status: `done`
- Arquivos principais:
  - [knowledge_openwebui/build_metadata.json](/workspaces/mcdia/05-iag/4-project/knowledge_openwebui/build_metadata.json:1)
  - [knowledge_openwebui/discursos_chunks.jsonl](/workspaces/mcdia/05-iag/4-project/knowledge_openwebui/discursos_chunks.jsonl:1)
  - `knowledge_openwebui/md_batches/`
- Implementacao:
  - Registrar `knowledge_id` em toda rodada.
  - Confirmar que a collection nao foi reindexada entre rodadas comparadas.
  - Manter snapshot dos artefatos usados.
  - Se possivel, registrar hash ou fingerprint dos artefatos.
- Resultado observado:
  - Todas as rodadas com `run_config` comparadas ate aqui registram o mesmo `knowledge_id`: `902f627d-ab07-43bb-a395-8d573117f4fc`.
  - Os fingerprints de `build_metadata.json`, `discursos_chunks.jsonl` e da amostra de `md_batches/` permaneceram identicos entre as rodadas comparadas.
  - A evidência consolidada foi registrada em um resumo dedicado de congelamento da knowledge base.
- Criterios de aceite:
  - Rodadas comparadas usam comprovadamente a mesma knowledge base.

### Tarefa 11.6 - Enriquecer a saida sintetica por pergunta

- Prioridade: media
- Status: `done`
- Implementacao:
  - Criar uma etapa de pos-processamento para gerar, por pergunta:
    - qualidade da recuperacao
    - fidelidade ao contexto
    - presenca correta de referencias
    - principal limite observado
  - Aproveitar `review_notes` e sinais de retrieval ja extraidos.
  - Produzir uma matriz curta para uso no manuscrito.
- Resultado observado:
  - Foi criado um pos-processador dedicado para gerar leitura analitica por pergunta a partir do JSONL da rodada.
  - A primeira matriz foi gerada sobre a rodada oficial base, com classificacoes sinteticas de recuperacao, fidelidade ao contexto, uso de referencias e limite principal por item.
- Criterios de aceite:
  - Cada pergunta possui uma leitura analitica sintetica alem da nota numerica.

### Tarefa 11.7 - Expandir a bateria com melhor balanceamento por categoria

- Prioridade: media
- Status: `done`
- Arquivos principais:
  - [eval/discursos_questions.json](/workspaces/mcdia/05-iag/4-project/eval/discursos_questions.json:1)
  - [eval/discursos_questions_v2_balanced.json](/workspaces/mcdia/05-iag/4-project/eval/discursos_questions_v2_balanced.json:1)
  - [eval/discursos_questions_v3_100.json](/workspaces/mcdia/05-iag/4-project/eval/discursos_questions_v3_100.json:1)
  - [eval/discursos_questions_v3_100.csv](/workspaces/mcdia/05-iag/4-project/eval/discursos_questions_v3_100.csv:1)
  - [eval/discursos_questions_v4_200.json](/workspaces/mcdia/05-iag/4-project/eval/discursos_questions_v4_200.json:1)
  - [eval/discursos_questions_v4_200.csv](/workspaces/mcdia/05-iag/4-project/eval/discursos_questions_v4_200.csv:1)
- Implementacao:
  - Aumentar o numero de perguntas por familia.
  - Garantir pelo menos 2 ou 3 perguntas por categoria critica, especialmente:
    - autoria cruzada
    - ampla
    - comparacao
    - checagem de alucinacao
    - multietapas
  - Versionar explicitamente o conjunto de perguntas.
- Resultado observado:
  - Foi criada uma nova versao explicitamente versionada do benchmark: [`eval/discursos_questions_v2_balanced.json`](/workspaces/mcdia/05-iag/4-project/eval/discursos_questions_v2_balanced.json:1).
  - O benchmark expandido passou de 20 para 25 perguntas.
  - As categorias criticas ficaram balanceadas em pelo menos 2 perguntas cada, com `comparison=3`, `broad=2`, `multi_hop=2`, `cross_author=2` e `hallucination_check=2`.
  - Foi criada a bateria ampliada [`eval/discursos_questions_v3_100.json`](/workspaces/mcdia/05-iag/4-project/eval/discursos_questions_v3_100.json:1), alinhada ao plano experimental do artigo em `/workspaces/latex/chatbot-rag/experimentos/PLANO_MELHORIA_EXPERIMENTOS.md`.
  - Foi criado tambem o espelho tabular [`eval/discursos_questions_v3_100.csv`](/workspaces/mcdia/05-iag/4-project/eval/discursos_questions_v3_100.csv:1) para revisao humana, anotacao e construcao posterior do gold standard de recuperacao.
  - A bateria v3 contem `100` perguntas e campos extras para desenho experimental: `secondary_categories`, `difficulty`, `answerable`, `expected_authors`, `relevant_sources_hint`, `expected_answer_criteria` e `evaluation_risks`.
  - A distribuicao cobre `16` categorias: `8` perguntas em `factual_simple`, `numeric`, `author_focus`, `comparison`, `negative_evidence`, `hallucination_trap`, `context_limits`, `multi_hop` e `cross_author_confusion`; e `4` perguntas em `synthesis`, `broad_multifocal`, `author_disambiguation`, `temporal_comparison`, `scope_control`, `retrieval_stress` e `citation_source_verification`.
  - Foi criada a bateria consolidada [`eval/discursos_questions_v4_200.json`](/workspaces/mcdia/05-iag/4-project/eval/discursos_questions_v4_200.json:1), com os `100` itens da v3 e mais `100` perguntas geradas a partir da leitura do dataset de discursos.
  - A v4 amplia a cobertura de temas para IA/PL 872, pandemia, auxilio emergencial, vacinas, Amazonia, desmatamento, garimpo, povos indigenas, feminicidio, universidades, ciencia, reforma tributaria, orcamento secreto, fake news, Judiciario, saude e SUS.
  - A distribuicao final da v4 fica equilibrada em `16` categorias, com `12` ou `13` perguntas por categoria.
- Criterios de aceite:
  - O benchmark deixa de ter categorias criticas subrepresentadas.

### Tarefa 11.8 - Incluir validacao manual amostral

- Prioridade: media
- Status: `done`
- Implementacao:
  - Selecionar 5 a 7 respostas da rodada final.
  - Fazer revisao humana parcial.
  - Comparar julgamento humano versus LLM Judge.
  - Registrar convergencias e divergencias.
- Resultado parcial:
  - A amostra recomendada foi definida com 7 perguntas da rodada oficial base: `q03`, `q11`, `q14`, `q15`, `q16`, `q18` e `q20`.
  - Foi gerado um pacote Markdown com a resposta completa, notas automaticas e campos prontos para preenchimento humano.
- Resultado observado:
  - A amostra foi efetivamente preenchida com uma revisao manual proposta, incluindo classificacao humana, fidelidade ao contexto, uso de referencias, principal problema observado e leitura de convergencia/divergencia com o juiz automatico.
  - A maior divergencia apareceu em `q20`, em que a revisao manual considerou a resposta inadequada por erro de escopo, apesar do `10/10` atribuido automaticamente.
- Criterios de aceite:
  - O experimento final inclui triangulacao entre avaliacao automatica e avaliacao humana amostral.

### Tarefa 11.9 - Transformar a avaliacao em protocolo reproduzivel formal

- Prioridade: alta
- Status: `done`
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
- Resultado observado:
  - O `README.md` passou a concentrar o protocolo oficial reproduzivel da avaliacao.
  - A documentacao agora explicita pre-condicoes, entradas obrigatorias, sequencia oficial de execucao, artefatos minimos, criterios de comparabilidade e criterios minimos de validade metodologica.
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
| 2026-04-17 | Uso de modelos locais como juiz | `gemma3:12b` descartado como juiz principal; `gemma4:31b` nao adotado como juiz principal | `gemma3:12b` apresentou respostas nulas em parte da bateria; `gemma4:31b` foi estavel, mas aparentou leniencia excessiva ao atribuir `10/10` em toda a bateria, inclusive quando julgou respostas de outro gerador. |
| 2026-04-17 | Congelamento da knowledge base | Rodadas com `run_config` passam a ser comparadas apenas quando mantem o mesmo `knowledge_id` e os mesmos fingerprints dos artefatos | O baseline atual fica associado ao `knowledge_id` `902f627d-ab07-43bb-a395-8d573117f4fc`, com verificacao formal registrada em resumo dedicado. |
| 2026-05-04 | Uso de `text_source` | Tratado como metadado de controle, nao como eixo analitico prioritario | A base regenerada tem `23119` chunks de `texto_integral`, `687` de `resumo` e `0` de `indexacao`; a Tarefa 4.3 foi deferida e o foco recomendado passou para separacao retrieval/geracao e desenho experimental ampliado. |
| 2026-05-04 | Separacao retrieval/geracao | Adotada primeira versao heuristica baseada no payload `sources` do Open WebUI | O avaliador passa a salvar sinais de recuperacao junto das notas de resposta; campos incertos sao marcados como `unknown` para evitar falsa precisao. |
| 2026-05-04 | Retomada da importacao | Importador passa a usar checkpoint persistente antes da reimportacao da base | `--resume` pula apenas batches com mesmo `knowledge_id` e mesmo SHA-256 ja marcados como `added`; `--dry-run` permite revisar a operacao sem chamadas de API. |
| 2026-05-05 | Mitigacao de rate limit em embeddings | Adicionado backoff para processamento `failed` e pausa entre batches | Logs do Open WebUI mostraram `429 Too Many Requests` em `/v1/embeddings`; o importador passou a oferecer `--process-failed-retries`, `--process-failed-initial-backoff`, `--process-failed-max-backoff` e `--sleep-between-files`. |
| 2026-05-05 | Rodada pos-reimportacao v2 | Tratar como baseline operacional, nao como evidencia de melhoria de qualidade | A knowledge v2 difere muito pouco da original, essencialmente por metadado de controle; a rodada valida que a base reimportada funciona, mas nao deve ser interpretada como ganho experimental relevante. |
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
| 2026-04-17 | Dependencias dos scripts auxiliares congeladas | [requirements.txt](/workspaces/mcdia/05-iag/4-project/requirements.txt:1) | Dependencias diretas fixadas em `requirements.txt` e fluxo oficial de instalacao do README atualizado para `pip install -r requirements.txt`, com validacao via `pip --dry-run`. |
| 2026-04-17 | Fluxo operacional do projeto padronizado no README | [README.md](/workspaces/mcdia/05-iag/4-project/README.md:217) | O README passou a trazer uma trilha unica de execucao de ponta a ponta, com precondicoes e saidas esperadas; o `README_IMPORT` foi removido para manter o README principal como unica fonte operacional. |
| 2026-04-17 | `.env.example` alinhado ao `docker-compose.yaml` | [.env.example](/workspaces/mcdia/05-iag/4-project/.env.example:1) | Variaveis interpoladas do compose foram revisadas e alinhadas com `.env.example`; defaults de `OPENAI_MODEL`, `DOCLING_MAX_WORKERS` e `WEBUI_TIMEOUT` foram consolidados e a configuracao foi validada com `docker compose config`. |
| 2026-04-17 | Tres rodadas completas para analise inicial de estabilidade | [rag_eval_20260416T172816Z.csv](/workspaces/mcdia/05-iag/4-project/eval/results/rag_eval_20260416T172816Z.csv:1) | Rodadas completas: `172816Z` media 9.15, `182240Z` media 9.55 e `232921Z` media 9.35; todas com 20/20 perguntas `ok` e mesma configuracao experimental versionada. |
| 2026-04-17 | Variacao entre rodadas identicas quantificada | [rag_eval_20260416T232921Z.csv](/workspaces/mcdia/05-iag/4-project/eval/results/rag_eval_20260416T232921Z.csv:1) | Variacao observada em perguntas como `q15`, `q16`, `q18` e `q19`, indicando estabilidade operacional alta, mas sensibilidade metodologica relevante em parte do benchmark. |
| 2026-04-17 | Consolidado automatico das 3 rodadas gerado | [scripts/summarize_eval_results.py](/workspaces/mcdia/05-iag/4-project/scripts/summarize_eval_results.py:1) | Script reutilizavel criado para comparar rodadas de avaliacao a partir dos CSVs e respectivos `run_config`. |
| 2026-04-17 | Estabilidade inicial formalmente registrada | [stability_summary_20260417T012001Z.md](/workspaces/mcdia/05-iag/4-project/eval/results/stability_summary_20260417T012001Z.md:1) | Resumo formal com medias por rodada, variacao por pergunta e conclusao inicial de estabilidade operacional com variacao metodologica em parte do benchmark. |
| 2026-04-17 | Rodadas controladas com juiz alternativo concluidas | [rag_eval_20260417T014653Z.csv](/workspaces/mcdia/05-iag/4-project/eval/results/rag_eval_20260417T014653Z.csv:1) | `gpt-5-nano -> gemma3:12b` confirmou que a troca de juiz altera o comportamento do experimento, mas revelou instabilidade operacional do `gemma3:12b`, com falhas por resposta nula em `q12`, `q14` e `q15`. |
| 2026-04-17 | Testes com `gemma4:31b` como gerador e juiz concluidos | [rag_eval_20260417T022327Z.csv](/workspaces/mcdia/05-iag/4-project/eval/results/rag_eval_20260417T022327Z.csv:1) | Rodada completa com 20/20 perguntas `ok` e `10/10` em todos os itens, sugerindo boa estabilidade operacional, mas tambem possivel leniencia excessiva do juiz quando o mesmo modelo gera e julga. |
| 2026-05-04 | Metadados de geracao corrigidos para o workspace atual | [knowledge_openwebui/build_metadata.json](/workspaces/mcdia/05-iag/4-project/knowledge_openwebui/build_metadata.json:1) | Builder atualizado para gravar caminhos absolutos atuais e caminhos relativos portaveis; artefatos regenerados com `23806` chunks e `120` batches Markdown. |
| 2026-05-04 | Suite inicial de testes automatizados criada | [pytest.ini](/workspaces/mcdia/05-iag/4-project/pytest.ini:1) | Criados testes para builder, avaliador e importador em `tests/`; `pytest==9.0.2` adicionado ao `requirements.txt`; validacao executada com `25 passed` e `pip install --dry-run -r requirements.txt`. |
| 2026-05-04 | Observabilidade inicial do avaliador automatizada | [scripts/run_rag_eval.py](/workspaces/mcdia/05-iag/4-project/scripts/run_rag_eval.py:1) | Avaliador passou a usar `logging`, medir duracao por pergunta, salvar `duration_seconds` no JSONL/CSV e gerar `*.run_summary.json` com estatisticas da rodada e ponteiros para os artefatos. |
| 2026-05-04 | Observabilidade basica do fluxo operacional concluida | [scripts/import_batches_to_openwebui.py](/workspaces/mcdia/05-iag/4-project/scripts/import_batches_to_openwebui.py:1) | Importador passou a usar `logging`, medir duracao por batch e gerar `knowledge_openwebui/import_summary_<timestamp>.json`; Prioridade 3 concluida com resumos padronizados para importacao e avaliacao. |
| 2026-05-04 | Origem do conteudo indexado persistida nos artefatos | [scripts/build_openwebui_knowledge_from_hf.py](/workspaces/mcdia/05-iag/4-project/scripts/build_openwebui_knowledge_from_hf.py:1) | Builder passou a registrar `text_source` por chunk, exibir `Origem do texto` nos batches Markdown e consolidar `text_source_counts` no `build_metadata.json`; tarefas 4.1 e 4.2 concluidas. |
| 2026-05-04 | Escopo analitico de `text_source` reavaliado | [PLANO_DE_MELHORIAS.md](/workspaces/mcdia/05-iag/4-project/PLANO_DE_MELHORIAS.md:341) | `text_source` mantido como metadado de controle; analise por origem deferida porque a base e fortemente dominada por `texto_integral`, com foco seguinte recomendado em retrieval/geracao e experimento ampliado. |
| 2026-05-04 | Primeira separacao entre retrieval e qualidade da resposta implementada | [scripts/run_rag_eval.py](/workspaces/mcdia/05-iag/4-project/scripts/run_rag_eval.py:1) | Avaliador passou a extrair `retrieval_*` do payload `sources`, salvar no JSONL/CSV/Markdown e consolidar sinais no `run_summary.json`; Prioridade 5 concluida em versao heuristica inicial. |
| 2026-05-04 | Importacao retomavel implementada | [scripts/import_batches_to_openwebui.py](/workspaces/mcdia/05-iag/4-project/scripts/import_batches_to_openwebui.py:1) | Prioridade 7 concluida com `import_state.json`, `--resume`, `--dry-run`, rastreio de falhas por batch e resumo operacional apontando para o estado persistente. |
| 2026-05-05 | Retry de processamento para falhas por embeddings | [scripts/import_batches_to_openwebui.py](/workspaces/mcdia/05-iag/4-project/scripts/import_batches_to_openwebui.py:1) | Importador atualizado para reenviar batches quando o processamento falha antes do `file/add`, com backoff configuravel e pausa entre arquivos para reduzir `429` em embeddings. |
| 2026-05-05 | Reimportacao da knowledge v2 concluida | estado local de importacao | A importacao finalizou com `120/120` batches adicionados e `0` falhas no `import_state.json`; os resumos de importacao permanecem artefatos operacionais locais e nao foram versionados. |
| 2026-05-05 | Rodada operacional contra knowledge v2 concluida | [rag_eval_20260505T142659Z.run_summary.json](/workspaces/mcdia/05-iag/4-project/eval/results/rag_eval_20260505T142659Z.run_summary.json:1) | Rodada com `20/20` perguntas `ok`, media `9.35`, minimo `7`, maximo `10`; usada como baseline pos-reimportacao, nao como prova de melhoria, pois o conteudo da base mudou muito pouco. |
| 2026-05-05 | Matriz analitica da rodada v2 gerada | [rag_eval_20260505T142659Z.question_analysis.md](/workspaces/mcdia/05-iag/4-project/eval/results/rag_eval_20260505T142659Z.question_analysis.md:1) | Pos-processamento registrou recuperacao `alta=19`, `media=1`, `baixa=0`; fidelidade `alta=11`, `media=8`, `baixa=1`, com fragilidade principal em autoria cruzada (`q18`). |
| 2026-04-17 | Teste cruzado `gpt-5.4-nano -> gemma4:31b` concluido | [rag_eval_20260417T024620Z.csv](/workspaces/mcdia/05-iag/4-project/eval/results/rag_eval_20260417T024620Z.csv:1) | Rodada completa com 20/20 perguntas `ok` e `10/10` em todos os itens novamente, reforcando a interpretacao de que `gemma4:31b` e estavel, mas permissivo demais para servir como juiz principal sem validacao manual adicional. |
| 2026-04-17 | Congelamento da knowledge base formalmente registrado | [knowledge_base_freeze_20260417.md](/workspaces/mcdia/05-iag/4-project/eval/results/knowledge_base_freeze_20260417.md:1) | Resumo formal confirmou que as rodadas comparadas com `run_config` compartilham o mesmo `knowledge_id` e os mesmos fingerprints de `build_metadata.json`, `discursos_chunks.jsonl` e `md_batches/`, sem evidencia de reindexacao entre elas. |
| 2026-04-17 | Pos-processamento analitico por pergunta implementado | [scripts/build_question_analysis.py](/workspaces/mcdia/05-iag/4-project/scripts/build_question_analysis.py:1) | Script criado para transformar o JSONL da rodada em matriz analitica por pergunta, combinando sinais de retrieval, notas do juiz e `review_notes`. |
| 2026-04-17 | Primeira matriz analitica da rodada oficial base gerada | [rag_eval_20260416T172816Z.question_analysis.md](/workspaces/mcdia/05-iag/4-project/eval/results/rag_eval_20260416T172816Z.question_analysis.md:1) | A rodada oficial base passou a ter leitura curta por pergunta com `retrieval_quality`, `context_faithfulness`, `reference_use` e `main_limitation`, pronta para reaproveito no manuscrito. |
| 2026-04-17 | Pacote de validacao manual amostral preparado | [rag_eval_20260416T172816Z.manual_validation_sample.md](/workspaces/mcdia/05-iag/4-project/eval/results/rag_eval_20260416T172816Z.manual_validation_sample.md:1) | Amostra recomendada definida com 7 perguntas cobrindo controle positivo, comparacao, multi-hop, precision de numeros, extrapolacao, autoria cruzada e controle de alucinacao; pacote inclui resposta completa, notas automaticas e campos para parecer humano. |
| 2026-04-17 | Validacao manual amostral preenchida | [rag_eval_20260416T172816Z.manual_validation_sample.md](/workspaces/mcdia/05-iag/4-project/eval/results/rag_eval_20260416T172816Z.manual_validation_sample.md:1) | Revisao manual proposta concluida para 7 perguntas; houve boa convergencia com o juiz automatico na maior parte da amostra, mas `q20` revelou divergencia importante e possivel superavaliacao automatica por erro de escopo. |
| 2026-04-17 | Protocolo reproduzivel formal consolidado no README | [README.md](/workspaces/mcdia/05-iag/4-project/README.md:467) | A secao de avaliacao passou a documentar o protocolo oficial da Opcao A, incluindo pre-condicoes, sequencia de execucao, artefatos obrigatorios, comparabilidade entre rodadas e criterios minimos de validade. |
| 2026-04-17 | Benchmark expandido e versionado | [discursos_questions_v2_balanced.json](/workspaces/mcdia/05-iag/4-project/eval/discursos_questions_v2_balanced.json:1) | Nova versao do questionario criada com 25 perguntas e melhor balanceamento das categorias criticas; o README passou a distinguir o benchmark historico de 20 perguntas da versao v2 recomendada para novas rodadas. |
| 2026-05-05 | Bateria experimental ampliada para o artigo | [discursos_questions_v3_100.json](/workspaces/mcdia/05-iag/4-project/eval/discursos_questions_v3_100.json:1) | Criada bateria com `100` perguntas e espelho CSV, alinhada ao plano experimental do artigo, incluindo categorias criticas, respondibilidade, dificuldade, autores esperados, pistas de fontes, criterios de resposta e riscos de avaliacao. |
| 2026-05-05 | Bateria experimental consolidada em 200 perguntas | [discursos_questions_v4_200.json](/workspaces/mcdia/05-iag/4-project/eval/discursos_questions_v4_200.json:1) | Criada versao consolidada com `200` perguntas e categorias equilibradas (`12` ou `13` itens por categoria), incorporando mais temas extraidos do dataset de discursos. |
| a preencher | a preencher | a preencher | a preencher |

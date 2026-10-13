# Construção do experimento

Este diretório será usado para desenvolver a infraestrutura de apoio e execução dos experimentos da dissertação.

O escopo será separado em dois componentes:

- gerenciador de experimentos, responsável por configurações, execuções, dados persistentes, métricas e relatórios;
- sistema RAG de referência, responsável por indexação, recuperação, geração e registro das evidências.

As primeiras decisões de arquitetura e especificações serão registradas aqui antes da implementação.

## OpenSpec

A estrutura de especificações está em `openspec/`, com o schema `spec-driven` e regras específicas deste subprojeto em `openspec/config.yaml`.

Comandos úteis, executados a partir deste diretório:

```bash
openspec list
openspec validate --all
openspec validate --changes
openspec validate --specs
```

Cada mudança relevante deve ser proposta e especificada antes da implementação. As especificações permanentes ficam em `openspec/specs/`; propostas em andamento ficam em `openspec/changes/` e só devem ser arquivadas depois de implementadas e verificadas.

## Registro experimental inicial

A primeira implementação usa apenas a biblioteca padrão do Python e SQLite. As dependências de teste estão em `requirements.txt`.

Inicialize o banco local:

```bash
python -m experiment_registry.cli init
```

Crie uma execução sintética e um relatório JSON:

```bash
python -m experiment_registry.cli demo
```

O banco será criado em `data/experiment_registry.sqlite3` e o relatório em `data/outputs/demo-run.json`. Para listar execuções:

```bash
python -m experiment_registry.cli list
```

Os testes podem ser executados sem dependências externas:

```bash
python -m unittest discover -s tests -v
```

A primeira versão ainda não implementa recuperação, geração, embeddings ou banco vetorial; ela apenas registra e valida execuções e artefatos.

## Dashboard local

Instale as dependências do subprojeto e execute a interface:

```bash
python -m pip install -r requirements.txt
streamlit run dashboard/app.py
```

O dashboard permite criar execuções com configuração JSON, listar e consultar execuções e validar a integridade dos artefatos. Ele é local e não possui autenticação ou acesso remoto configurado.

## Executor de recuperação

Entradas do executor:

- documentos em JSONL, uma linha por documento: `{"id": "doc-1", "text": "..."}`;
- perguntas em CSV com as colunas `question_id,query,reference_doc_ids`; múltiplas referências são separadas por `;`.

Execute um baseline:

```bash
python -m experiment_registry.cli run-retrieval \
  --documents /caminho/documentos.jsonl \
  --questions /caminho/perguntas.csv \
  --method bm25 \
  --name piloto-bm25
```

As estratégias disponíveis são `bm25`, `tfidf` e `hybrid`. Resultados, métricas e hashes das entradas são gravados no registro e em `data/outputs/`.

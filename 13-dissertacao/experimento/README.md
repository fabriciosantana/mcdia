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

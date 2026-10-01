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

# Design

## Context

A dissertação já possui dados derivados e notebooks, mas ainda não possui um registro operacional de execuções. O primeiro componente deve funcionar localmente, sem depender de serviços externos, e precisa preservar a distinção entre o gerenciador e o RAG avaliado.

## Goals / Non-Goals

**Goals:**

- Oferecer uma API Python pequena para criar e consultar execuções.
- Usar persistência relacional local, com migrações simples e inspeção direta.
- Armazenar configurações e metadados no banco e arquivos completos em diretórios derivados.
- Calcular hashes SHA-256 para configurações e artefatos.
- Permitir testes determinísticos sem modelo de linguagem ou índice vetorial.

**Non-Goals:**

- Implementar nesta mudança o recuperador, o gerador, embeddings ou banco vetorial.
- Criar interface web, autenticação, execução distribuída ou serviço de produção.
- Alterar os dados brutos do corpus.

## Decisions

1. **SQLite como primeiro armazenamento relacional.** Ele reduz a infraestrutura do piloto, é transacional e pode ser versionado como artefato local. PostgreSQL permanece uma alternativa futura se houver necessidade de concorrência ou serviço compartilhado.
2. **Arquivos derivados fora do banco.** Respostas completas, listas extensas de trechos e logs ficam em arquivos JSON/JSONL; o banco guarda caminho, tipo e hash. Isso evita blobs difíceis de inspecionar e preserva a portabilidade.
3. **Identidade por UUID e configuração por hash.** O UUID distingue execuções mesmo quando a configuração se repete; o hash permite verificar se a configuração ou o artefato mudou.
4. **API independente do RAG.** O registro recebe artefatos por uma interface estável. Recuperadores e geradores futuros serão adaptadores, evitando que o banco conheça detalhes de um fornecedor ou modelo.
5. **Migrations explícitas.** O esquema será criado por script versionado, com uma tabela de versão, para que um banco novo e um banco existente possam ser atualizados de maneira reproduzível.

## Risks / Trade-offs

- [Complexidade prematura] → limitar a primeira mudança ao registro e aos testes, sem UI ou banco vetorial.
- [Inconsistência entre banco e arquivos] → exigir hash e validação antes de aceitar associações.
- [Perda de contexto experimental] → registrar configuração completa, versão do código e manifestos como campos obrigatórios.
- [Migração futura para PostgreSQL] → evitar SQL específico de um fornecedor na API inicial.

## Migration Plan

1. Criar o esquema SQLite e os módulos de acesso.
2. Executar testes em banco temporário.
3. Registrar uma execução sintética e validar seus artefatos.
4. Integrar o notebook piloto somente depois da validação do registro.

Não há migração de dados existentes nesta mudança; os CSVs e JSONs atuais permanecem como fontes históricas.

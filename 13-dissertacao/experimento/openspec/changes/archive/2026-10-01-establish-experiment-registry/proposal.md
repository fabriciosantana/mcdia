# Proposal

## Why

Os experimentos hoje dependem de CSVs, JSONs e arquivos Markdown dispersos, o que aumenta o risco de perder a relação entre configuração, execução, recuperação, resposta e avaliação. Precisamos de um registro persistente mínimo antes de ampliar o RAG, para que cada resultado seja identificável e reproduzível.

## What Changes

- Criar um registro persistente de experimentos com identificador estável para cada execução.
- Registrar configurações, versões, parâmetros e hashes usados em uma execução.
- Associar perguntas, documentos, trechos recuperados, respostas e métricas à execução correspondente.
- Expor consultas básicas para listar execuções, recuperar uma execução e comparar resultados.
- Manter os arquivos completos em armazenamento derivado, usando o banco para metadados e relações.
- Definir comandos reproduzíveis para criar o banco, registrar uma execução e validar a integridade do registro.

## Capabilities

### New Capabilities

- `experiment-registry`: registro persistente e consultável de configurações, execuções e artefatos experimentais.

### Modified Capabilities

Nenhuma.

## Impact

A mudança criará o primeiro módulo executável em `experimento/`, um banco local e testes de integração. O gerenciador será independente do modelo de linguagem, do índice vetorial e do sistema RAG, que serão integrados em mudanças posteriores.

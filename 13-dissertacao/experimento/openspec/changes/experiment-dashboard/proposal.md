# Proposal

## Why

O registro SQLite já preserva as execuções, mas a interação ainda depende da linha de comando e de inspeção manual de JSON. Um dashboard local reduzirá a manipulação de arquivos e tornará a consulta das execuções mais adequada ao uso cotidiano durante o piloto.

## What Changes

- Adicionar dashboard Streamlit executável localmente.
- Permitir criar uma execução a partir de uma configuração JSON.
- Listar execuções e exibir detalhes de uma execução selecionada.
- Exibir artefatos associados e o resultado da validação de integridade.
- Manter o dashboard como cliente do registro existente, sem duplicar regras de persistência.

## Capabilities

### New Capabilities

- `experiment-dashboard`: interface local para consultar e operar o registro experimental.

### Modified Capabilities

Nenhuma.

## Impact

Será adicionada a dependência Streamlit, um aplicativo em `experimento/dashboard/` e testes para parsing e integração básica com o registro. O dashboard usará o banco SQLite local e os caminhos definidos pelo registro existente.

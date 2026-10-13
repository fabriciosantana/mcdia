# Spec Delta

## Purpose

O dashboard fornece uma interface local para operar o registro experimental, consultar execuções e verificar a integridade dos artefatos sem editar CSVs ou JSONs manualmente.

## ADDED Requirements

### Requirement: Criar execução pela interface
O dashboard SHALL aceitar um nome e uma configuração JSON válida e criar uma execução no registro persistente.

#### Scenario: Configuração válida
- **WHEN** o usuário informa nome e JSON válido e envia o formulário
- **THEN** o dashboard cria a execução e informa seu identificador

#### Scenario: JSON inválido
- **WHEN** o usuário envia uma configuração que não é JSON válido ou não é um objeto
- **THEN** o dashboard informa o erro e não altera o registro

### Requirement: Consultar execuções
O dashboard SHALL listar as execuções persistidas e permitir selecionar uma execução para consultar seus detalhes.

#### Scenario: Lista de execuções
- **WHEN** o dashboard é aberto
- **THEN** exibe identificador, nome, estado, data e hash da configuração das execuções

#### Scenario: Detalhes selecionados
- **WHEN** o usuário seleciona uma execução
- **THEN** o dashboard exibe a configuração, os artefatos e os metadados da execução

### Requirement: Validar integridade
O dashboard SHALL permitir executar a validação de uma execução e exibir o estado da configuração e de cada artefato.

#### Scenario: Execução íntegra
- **WHEN** os arquivos associados permanecem iguais aos hashes registrados
- **THEN** o dashboard informa validação bem-sucedida

#### Scenario: Artefato alterado
- **WHEN** um arquivo associado foi alterado ou removido
- **THEN** o dashboard identifica o artefato inválido sem modificar os dados registrados

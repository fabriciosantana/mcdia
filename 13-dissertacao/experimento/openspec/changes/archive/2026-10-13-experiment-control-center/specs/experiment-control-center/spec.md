# Centro de controle experimental

## ADDED Requirements

### Requirement: Gerenciar perfis de configuração

A interface SHALL allow saving, updating and viewing named JSON configuration profiles in the persistent registry.

#### Scenario: Salvar perfil válido

- **WHEN** the user submits a non-empty name and JSON object in the Configurações tab
- **THEN** the profile is persisted with canonical JSON and a hash
- **AND** the profile appears in the list of saved profiles

### Requirement: Executar e acompanhar recuperação

A interface SHALL allow selecting input paths and a retrieval method, executing a run, and viewing its metrics and artifacts.

#### Scenario: Executar recuperação

- **WHEN** the user submits valid documents and questions paths
- **THEN** a run is created and retrieval metrics and artifacts are shown
- **AND** the run is available in the run selectors

### Requirement: Gerar e visualizar respostas

A interface SHALL allow generating LLM responses for a selected run and viewing each question, answer, citation and model metadata.

#### Scenario: Visualizar respostas

- **WHEN** a selected run has persisted responses
- **THEN** the Questions and answers tab shows the questions and one selected answer
- **AND** citations and response metadata are available for inspection

### Requirement: Registrar avaliação humana

A interface SHALL provide the five 0–2 evaluation dimensions and persist evaluator notes for a selected response.

#### Scenario: Registrar avaliação

- **WHEN** the user submits an evaluator and scores for all five dimensions
- **THEN** the evaluation is persisted against the selected response
- **AND** it appears in the response's recorded evaluations


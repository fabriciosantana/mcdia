# Question catalog administration Specification

## ADDED Requirements

### Requirement: Administrar catálogo no SQLite
The system SHALL persist question definitions and curation state in the SQLite question catalog.

#### Scenario: Editar pergunta
- **WHEN** an operator saves a question in the dashboard
- **THEN** its text, category, references and curation state are persisted in SQLite

### Requirement: Selecionar somente perguntas validadas
The system SHALL allow a retrieval run to select questions from the catalog and SHALL reject an empty or non-validated selection.

#### Scenario: Criar execução a partir do catálogo
- **WHEN** the operator selects validated questions
- **THEN** the run snapshots those questions into the run-scoped `questions` table
- **AND** draft questions are not included

### Requirement: Preservar o banco inicial
The system SHALL provide a one-time import of the initial question bank without requiring ongoing CSV/JSON editing.

#### Scenario: Abrir catálogo vazio
- **WHEN** the catalog is empty and the initial source is available
- **THEN** the dashboard offers the initial import
- **AND** subsequent administration uses SQLite

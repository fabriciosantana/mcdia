# evaluation-audit-layer Specification

## Purpose
Adicionar incerteza estatística, análise de casos críticos e atribuição de citações explicitamente verificável ao pipeline experimental.

## Requirements

### Requirement: Quantificar incerteza

The system SHALL calculate deterministic bootstrap summaries for metric samples with explicit seed and sample size.

#### Scenario: Gerar intervalo

- **WHEN** the user supplies metric observations
- **THEN** the system returns sample size, mean, interval and seed

### Requirement: Registrar casos críticos

The system SHALL store error type, severity and notes linked to a response.

#### Scenario: Classificar resposta

- **WHEN** the user identifies an error in a response
- **THEN** the case is persisted and shown with the response

### Requirement: Preservar citações explícitas

The system SHALL register only source identifiers explicitly cited in generated text.

#### Scenario: Resposta sem citação

- **WHEN** generated text does not contain a known source identifier
- **THEN** no citation is falsely attributed to the response

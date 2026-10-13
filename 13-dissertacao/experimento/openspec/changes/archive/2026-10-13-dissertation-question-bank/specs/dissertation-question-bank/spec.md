# Banco de perguntas da dissertação

## ADDED Requirements

### Requirement: Preservar a proveniência das perguntas

The system SHALL preserve the source file, source question identifier, candidate source identifiers, answer criteria and evaluation risks for every imported question.

#### Scenario: Importar pergunta candidata

- **WHEN** a question is imported from the v4 source bank
- **THEN** its source metadata and candidate references remain inspectable
- **AND** its curation status is draft

### Requirement: Normalizar categorias

The system SHALL map source categories to the twelve primary dissertation categories and retain secondary categories.

#### Scenario: Gerar bateria-piloto

- **WHEN** the pilot selection is generated
- **THEN** it contains two questions for each primary category
- **AND** no question is automatically marked validated


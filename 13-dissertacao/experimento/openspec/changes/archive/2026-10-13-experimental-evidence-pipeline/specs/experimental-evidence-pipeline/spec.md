# Pipeline experimental orientado a evidências

## ADDED Requirements

### Requirement: Preparar documentos com proveniência

The system SHALL ingest JSONL and supported Parquet corpus records, create deterministic chunks, preserve source metadata, and register input hashes.

#### Scenario: Preparar corpus

- **WHEN** the user submits a valid corpus and chunking configuration
- **THEN** the system writes chunks with document and chunk identifiers
- **AND** preserves source metadata and registers the resulting artifact

### Requirement: Curar perguntas e evidências

The system SHALL store question category, answerability, validation status, reference documents, relevant chunks, relevance grades, and curation notes.

#### Scenario: Validar pergunta

- **WHEN** a question has a query, category, answerability and curation status
- **THEN** it can be included in a controlled retrieval run only when status is validated
- **AND** its evidence references remain inspectable

### Requirement: Avaliar recuperação ampliada

The system SHALL persist chunk rankings and calculate Recall@k, Precision@k, Hit@k, MRR and nDCG when the reference judgments support each metric.

#### Scenario: Comparar métodos

- **WHEN** the same validated questions and corpus are executed with multiple retrieval methods
- **THEN** each run stores comparable rankings and metrics
- **AND** metrics identify the run and method

### Requirement: Comparar julgamentos

The system SHALL persist automated judgments separately from human evaluations and calculate agreement only for matching response dimensions.

#### Scenario: Auditar juiz automatizado

- **WHEN** a response has human and automated scores for a shared rubric
- **THEN** the system reports exact agreement and weighted ordinal agreement by dimension
- **AND** preserves the underlying disagreements

### Requirement: Exportar resultados

The system SHALL export deterministic CSV and LaTeX summaries for a selected run, including provenance identifiers.

#### Scenario: Gerar artefatos de redação

- **WHEN** the user requests an export for a completed run
- **THEN** the system writes result tables to the outputs directory
- **AND** includes the run identifier and generation timestamp in the manifest


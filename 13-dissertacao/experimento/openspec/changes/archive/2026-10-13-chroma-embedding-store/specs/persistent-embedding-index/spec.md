# Persistent embedding index Specification

## MODIFIED Requirements

### Requirement: Reutilizar embeddings compatíveis
The system SHALL reuse persisted document and query embeddings from ChromaDB when model and input hashes match.

#### Scenario: Repetir recuperação densa
- **WHEN** the same corpus, query and embedding model are used again
- **THEN** the system loads the vectors from persistent ChromaDB collections
- **AND** it does not call the embedding provider again

### Requirement: Registrar proveniência do índice
The system SHALL persist a JSON manifest containing the ChromaDB collection, model, input hash, dimensions and document identifiers.

#### Scenario: Auditar execução densa
- **WHEN** a dense retrieval run completes
- **THEN** its registry contains the generated ChromaDB manifest artifact

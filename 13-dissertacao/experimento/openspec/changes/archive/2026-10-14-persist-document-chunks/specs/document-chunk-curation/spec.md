# Document chunk curation Specification

## ADDED Requirements

### Requirement: Persistir chunks preparados
The system SHALL persist every prepared chunk in the SQLite `document_chunks` table with source hash and segmentation metadata.

#### Scenario: Preparar corpus
- **WHEN** a corpus is prepared with a window and overlap
- **THEN** its chunks are stored in SQLite
- **AND** the generated JSONL remains available as an export artifact

### Requirement: Consultar chunks para curadoria
The system SHALL provide a dashboard view that searches persisted chunks by document identifier or text and displays each chunk identifier and content.

#### Scenario: Localizar evidência
- **WHEN** an operator searches the chunk catalog
- **THEN** matching chunks and their IDs are shown for manual curation

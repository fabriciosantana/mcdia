CREATE TABLE IF NOT EXISTS question_metadata (
    run_id TEXT NOT NULL,
    question_id TEXT NOT NULL,
    category TEXT,
    validation_status TEXT NOT NULL DEFAULT 'validated',
    curation_notes TEXT,
    reference_chunks_json TEXT NOT NULL DEFAULT '[]',
    relevance_judgments_json TEXT NOT NULL DEFAULT '{}',
    PRIMARY KEY (run_id, question_id),
    FOREIGN KEY (run_id, question_id) REFERENCES questions(run_id, question_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS document_chunks (
    chunk_id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    text TEXT NOT NULL,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    source_sha256 TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_chunks_document ON document_chunks(document_id);

CREATE TABLE IF NOT EXISTS automated_evaluations (
    evaluation_id TEXT PRIMARY KEY,
    response_id TEXT NOT NULL,
    evaluator_model TEXT NOT NULL,
    prompt_hash TEXT,
    factual_correctness INTEGER CHECK (factual_correctness BETWEEN 0 AND 2),
    context_adherence INTEGER CHECK (context_adherence BETWEEN 0 AND 2),
    citation_support INTEGER CHECK (citation_support BETWEEN 0 AND 2),
    proportional_completeness INTEGER CHECK (proportional_completeness BETWEEN 0 AND 2),
    insufficiency_recognition INTEGER CHECK (insufficiency_recognition BETWEEN 0 AND 2),
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (response_id) REFERENCES responses(response_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_auto_evaluations_response ON automated_evaluations(response_id);

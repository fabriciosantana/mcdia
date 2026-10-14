CREATE TABLE IF NOT EXISTS question_catalog (
    question_id TEXT PRIMARY KEY,
    source_question_id TEXT,
    query TEXT NOT NULL,
    category TEXT NOT NULL,
    source_category TEXT,
    secondary_categories_json TEXT NOT NULL DEFAULT '[]',
    difficulty TEXT,
    answerability TEXT,
    respondible INTEGER NOT NULL DEFAULT 1,
    expected_authors_json TEXT NOT NULL DEFAULT '[]',
    reference_doc_ids_json TEXT NOT NULL DEFAULT '[]',
    reference_chunk_ids_json TEXT NOT NULL DEFAULT '[]',
    relevance_judgments_json TEXT NOT NULL DEFAULT '{}',
    expected_answer_criteria TEXT,
    evaluation_risks TEXT,
    status TEXT NOT NULL DEFAULT 'rascunho' CHECK (status IN ('rascunho','revisar','validada','arquivada')),
    curation_notes TEXT,
    source_file TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_question_catalog_status ON question_catalog(status);
CREATE INDEX IF NOT EXISTS idx_question_catalog_category ON question_catalog(category);

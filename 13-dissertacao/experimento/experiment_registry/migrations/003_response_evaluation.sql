CREATE TABLE IF NOT EXISTS responses (
    response_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    question_id TEXT NOT NULL,
    answer TEXT NOT NULL,
    model TEXT,
    prompt_hash TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id, question_id) REFERENCES questions(run_id, question_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS citations (
    citation_id TEXT PRIMARY KEY,
    response_id TEXT NOT NULL,
    document_id TEXT NOT NULL,
    chunk_id TEXT,
    cited_text TEXT,
    FOREIGN KEY (response_id) REFERENCES responses(response_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS human_evaluations (
    evaluation_id TEXT PRIMARY KEY,
    response_id TEXT NOT NULL,
    evaluator TEXT NOT NULL,
    factual_correctness INTEGER NOT NULL CHECK (factual_correctness BETWEEN 0 AND 2),
    context_adherence INTEGER NOT NULL CHECK (context_adherence BETWEEN 0 AND 2),
    citation_support INTEGER NOT NULL CHECK (citation_support BETWEEN 0 AND 2),
    proportional_completeness INTEGER NOT NULL CHECK (proportional_completeness BETWEEN 0 AND 2),
    insufficiency_recognition INTEGER NOT NULL CHECK (insufficiency_recognition BETWEEN 0 AND 2),
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (response_id) REFERENCES responses(response_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_responses_run ON responses(run_id);
CREATE INDEX IF NOT EXISTS idx_evaluations_response ON human_evaluations(response_id);

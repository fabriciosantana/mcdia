CREATE TABLE IF NOT EXISTS vector_indexes (
    index_id TEXT PRIMARY KEY,
    chunk_set_id TEXT NOT NULL,
    collection_name TEXT NOT NULL UNIQUE,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    dimensions INTEGER,
    distance_metric TEXT NOT NULL DEFAULT 'cosine',
    parameters_json TEXT NOT NULL DEFAULT '{}',
    state TEXT NOT NULL DEFAULT 'queued' CHECK(state IN ('queued','building','completed','failed','archived')),
    total_items INTEGER NOT NULL DEFAULT 0,
    completed_items INTEGER NOT NULL DEFAULT 0,
    error TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(chunk_set_id) REFERENCES chunk_sets(chunk_set_id)
);
CREATE TABLE IF NOT EXISTS experiment_plans (
    plan_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    battery_id TEXT NOT NULL,
    chunk_set_id TEXT NOT NULL,
    index_id TEXT,
    configuration_json TEXT NOT NULL,
    prompt_version TEXT,
    state TEXT NOT NULL DEFAULT 'draft' CHECK(state IN ('draft','frozen','archived')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    frozen_at TEXT,
    FOREIGN KEY(battery_id) REFERENCES question_batteries(battery_id),
    FOREIGN KEY(chunk_set_id) REFERENCES chunk_sets(chunk_set_id),
    FOREIGN KEY(index_id) REFERENCES vector_indexes(index_id)
);
ALTER TABLE experiment_runs ADD COLUMN plan_id TEXT REFERENCES experiment_plans(plan_id);
ALTER TABLE experiment_runs ADD COLUMN attempt INTEGER NOT NULL DEFAULT 1;
ALTER TABLE experiment_runs ADD COLUMN heartbeat_at TEXT;
ALTER TABLE experiment_runs ADD COLUMN error TEXT;
CREATE TABLE IF NOT EXISTS experiment_jobs (
    job_id TEXT PRIMARY KEY,
    run_id TEXT,
    index_id TEXT,
    kind TEXT NOT NULL,
    state TEXT NOT NULL DEFAULT 'queued' CHECK(state IN ('queued','running','completed','failed','cancelled')),
    progress_total INTEGER NOT NULL DEFAULT 0,
    progress_done INTEGER NOT NULL DEFAULT 0,
    checkpoint TEXT,
    heartbeat_at TEXT,
    attempts INTEGER NOT NULL DEFAULT 0,
    error TEXT,
    requested_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finished_at TEXT,
    FOREIGN KEY(run_id) REFERENCES experiment_runs(run_id),
    FOREIGN KEY(index_id) REFERENCES vector_indexes(index_id)
);
CREATE TABLE IF NOT EXISTS run_question_snapshots (
    run_id TEXT NOT NULL,
    question_id TEXT NOT NULL,
    question_revision INTEGER NOT NULL,
    battery_id TEXT NOT NULL,
    chunk_set_id TEXT NOT NULL,
    query TEXT NOT NULL,
    expected_answer_criteria TEXT,
    answerability TEXT,
    category TEXT,
    source_category TEXT,
    secondary_categories_json TEXT NOT NULL DEFAULT '[]',
    reference_chunks_json TEXT NOT NULL,
    sufficient_chunks_json TEXT NOT NULL DEFAULT '[]',
    judgments_json TEXT NOT NULL,
    PRIMARY KEY(run_id,question_id),
    FOREIGN KEY(run_id,question_id) REFERENCES questions(run_id,question_id),
    FOREIGN KEY(battery_id) REFERENCES question_batteries(battery_id),
    FOREIGN KEY(chunk_set_id) REFERENCES chunk_sets(chunk_set_id)
);
ALTER TABLE retrieval_results ADD COLUMN ranked_chunks_json TEXT NOT NULL DEFAULT '[]';
ALTER TABLE retrieval_results ADD COLUMN scores_by_chunk_json TEXT NOT NULL DEFAULT '[]';
CREATE TABLE IF NOT EXISTS run_contexts (
    run_id TEXT NOT NULL,
    question_id TEXT NOT NULL,
    rank INTEGER NOT NULL,
    chunk_set_id TEXT NOT NULL,
    chunk_id TEXT NOT NULL,
    document_id TEXT NOT NULL,
    text TEXT NOT NULL,
    source_url TEXT,
    score REAL,
    PRIMARY KEY(run_id,question_id,rank),
    FOREIGN KEY(run_id,question_id) REFERENCES questions(run_id,question_id),
    FOREIGN KEY(chunk_set_id,chunk_id) REFERENCES document_chunks(chunk_set_id,chunk_id)
);
ALTER TABLE responses ADD COLUMN prompt_text TEXT;
ALTER TABLE responses ADD COLUMN context_hash TEXT;
ALTER TABLE responses ADD COLUMN provider TEXT;
ALTER TABLE responses ADD COLUMN parameters_json TEXT NOT NULL DEFAULT '{}';
ALTER TABLE responses ADD COLUMN duration_ms INTEGER;
ALTER TABLE responses ADD COLUMN usage_json TEXT;
ALTER TABLE responses ADD COLUMN cost_estimate REAL;
ALTER TABLE citations ADD COLUMN source_url TEXT;
ALTER TABLE citations ADD COLUMN validity TEXT NOT NULL DEFAULT 'unverified';
CREATE TRIGGER IF NOT EXISTS deny_delete_referenced_index BEFORE DELETE ON vector_indexes
WHEN EXISTS(SELECT 1 FROM experiment_plans WHERE index_id=OLD.index_id)
BEGIN SELECT RAISE(ABORT,'index is referenced by an experiment plan'); END;

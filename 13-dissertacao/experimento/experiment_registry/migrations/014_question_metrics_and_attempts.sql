CREATE TABLE retrieval_question_metrics (
    run_id TEXT NOT NULL,
    question_id TEXT NOT NULL,
    metric_version TEXT NOT NULL,
    coverage_state TEXT NOT NULL CHECK(coverage_state IN ('eligible','not_applicable')),
    metrics_json TEXT NOT NULL,
    not_applicable_reason TEXT,
    PRIMARY KEY(run_id,question_id),
    FOREIGN KEY(run_id,question_id) REFERENCES questions(run_id,question_id) ON DELETE CASCADE
);
ALTER TABLE responses ADD COLUMN generation_attempt INTEGER NOT NULL DEFAULT 1;
ALTER TABLE evaluator_registry ADD COLUMN access_salt TEXT;
ALTER TABLE evaluator_registry ADD COLUMN access_hash TEXT;
ALTER TABLE claim_evidence ADD COLUMN round_id TEXT REFERENCES evaluation_rounds(round_id);
CREATE INDEX idx_responses_run_question_attempt ON responses(run_id,question_id,generation_attempt);
CREATE UNIQUE INDEX idx_one_active_run_job ON experiment_jobs(run_id,kind) WHERE run_id IS NOT NULL AND state='running';
CREATE UNIQUE INDEX idx_one_active_index_job ON experiment_jobs(index_id,kind) WHERE index_id IS NOT NULL AND state='running';
CREATE UNIQUE INDEX idx_one_active_execution_kind ON experiment_jobs(kind) WHERE state='running' AND kind IN ('retrieval','generation','index-build','lexical-build');
CREATE TABLE evaluation_adjudication_links (
    adjudicated_evaluation_id TEXT NOT NULL,
    source_evaluation_id TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(adjudicated_evaluation_id,source_evaluation_id),
    FOREIGN KEY(adjudicated_evaluation_id) REFERENCES human_evaluations(evaluation_id),
    FOREIGN KEY(source_evaluation_id) REFERENCES human_evaluations(evaluation_id)
);

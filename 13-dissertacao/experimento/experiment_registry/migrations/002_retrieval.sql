CREATE TABLE IF NOT EXISTS questions (
    run_id TEXT NOT NULL,
    question_id TEXT NOT NULL,
    query TEXT NOT NULL,
    reference_doc_ids_json TEXT NOT NULL,
    respondible INTEGER NOT NULL,
    PRIMARY KEY (run_id, question_id),
    FOREIGN KEY (run_id) REFERENCES experiment_runs(run_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS retrieval_results (
    run_id TEXT NOT NULL,
    question_id TEXT NOT NULL,
    ranked_doc_ids_json TEXT NOT NULL,
    scores_json TEXT NOT NULL,
    PRIMARY KEY (run_id, question_id),
    FOREIGN KEY (run_id, question_id) REFERENCES questions(run_id, question_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS retrieval_metrics (
    run_id TEXT PRIMARY KEY,
    method TEXT NOT NULL,
    recall_at_1 REAL,
    recall_at_5 REAL,
    recall_at_10 REAL,
    mrr REAL,
    respondible_questions INTEGER NOT NULL,
    FOREIGN KEY (run_id) REFERENCES experiment_runs(run_id) ON DELETE CASCADE
);

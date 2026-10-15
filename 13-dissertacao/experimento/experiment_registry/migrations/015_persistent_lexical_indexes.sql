CREATE TABLE lexical_indexes (
    chunk_set_id TEXT PRIMARY KEY,
    algorithm TEXT NOT NULL,
    index_version TEXT NOT NULL,
    corpus_digest TEXT NOT NULL,
    document_count INTEGER NOT NULL,
    token_count INTEGER NOT NULL,
    index_sha256 TEXT NOT NULL,
    index_gzip BLOB NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(chunk_set_id) REFERENCES chunk_sets(chunk_set_id)
);
CREATE TABLE generation_items (
    job_id TEXT NOT NULL,
    run_id TEXT NOT NULL,
    question_id TEXT NOT NULL,
    generation_attempt INTEGER NOT NULL,
    state TEXT NOT NULL CHECK(state IN ('queued','running','completed','uncertain','failed')),
    request_hash TEXT NOT NULL,
    response_id TEXT,
    error TEXT,
    started_at TEXT,
    finished_at TEXT,
    PRIMARY KEY(job_id,question_id),
    FOREIGN KEY(job_id) REFERENCES experiment_jobs(job_id),
    FOREIGN KEY(run_id,question_id) REFERENCES questions(run_id,question_id),
    FOREIGN KEY(response_id) REFERENCES responses(response_id)
);

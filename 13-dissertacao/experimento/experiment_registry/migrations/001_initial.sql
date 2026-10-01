CREATE TABLE IF NOT EXISTS configurations (
    configuration_hash TEXT PRIMARY KEY,
    configuration_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS experiment_runs (
    run_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    state TEXT NOT NULL DEFAULT 'created'
        CHECK (state IN ('created', 'running', 'completed', 'failed', 'cancelled')),
    configuration_hash TEXT NOT NULL,
    started_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finished_at TEXT,
    FOREIGN KEY (configuration_hash) REFERENCES configurations(configuration_hash)
);

CREATE TABLE IF NOT EXISTS artifacts (
    artifact_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    artifact_type TEXT NOT NULL,
    path TEXT NOT NULL,
    sha256 TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES experiment_runs(run_id) ON DELETE CASCADE,
    UNIQUE (run_id, artifact_type, path)
);

CREATE INDEX IF NOT EXISTS idx_experiment_runs_state ON experiment_runs(state);
CREATE INDEX IF NOT EXISTS idx_experiment_runs_configuration ON experiment_runs(configuration_hash);
CREATE INDEX IF NOT EXISTS idx_artifacts_run ON artifacts(run_id);

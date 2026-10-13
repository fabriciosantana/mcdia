CREATE TABLE IF NOT EXISTS error_cases (
    error_id TEXT PRIMARY KEY,
    response_id TEXT NOT NULL,
    error_type TEXT NOT NULL,
    severity TEXT NOT NULL DEFAULT 'moderate',
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (response_id) REFERENCES responses(response_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_error_cases_response ON error_cases(response_id);

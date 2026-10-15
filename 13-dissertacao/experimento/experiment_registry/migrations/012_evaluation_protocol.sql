CREATE TABLE IF NOT EXISTS evaluation_protocols (
    protocol_id TEXT PRIMARY KEY,
    version INTEGER NOT NULL,
    name TEXT NOT NULL,
    hypotheses_json TEXT NOT NULL,
    analysis_rules_json TEXT NOT NULL,
    state TEXT NOT NULL DEFAULT 'draft' CHECK(state IN ('draft','frozen','superseded')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    frozen_at TEXT,
    UNIQUE(name,version)
);
CREATE TABLE IF NOT EXISTS rubric_versions (
    rubric_id TEXT PRIMARY KEY,
    version INTEGER NOT NULL,
    rubric_json TEXT NOT NULL,
    state TEXT NOT NULL DEFAULT 'draft' CHECK(state IN ('draft','frozen','superseded')),
    UNIQUE(version)
);
CREATE TABLE IF NOT EXISTS evaluator_registry (
    evaluator_id TEXT PRIMARY KEY,
    pseudonym TEXT NOT NULL UNIQUE,
    informed INTEGER NOT NULL DEFAULT 0,
    active INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS evaluation_rounds (
    round_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    protocol_id TEXT NOT NULL,
    rubric_id TEXT NOT NULL,
    kind TEXT NOT NULL CHECK(kind IN ('human','judge','adjudication')),
    label TEXT NOT NULL,
    model TEXT,
    blind INTEGER NOT NULL DEFAULT 1,
    state TEXT NOT NULL DEFAULT 'draft' CHECK(state IN ('draft','active','completed','archived')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(run_id) REFERENCES experiment_runs(run_id),
    FOREIGN KEY(protocol_id) REFERENCES evaluation_protocols(protocol_id),
    FOREIGN KEY(rubric_id) REFERENCES rubric_versions(rubric_id)
);
CREATE TABLE IF NOT EXISTS evaluation_assignments (
    assignment_id TEXT PRIMARY KEY,
    round_id TEXT NOT NULL,
    response_id TEXT NOT NULL,
    evaluator_id TEXT NOT NULL,
    state TEXT NOT NULL DEFAULT 'assigned' CHECK(state IN ('assigned','submitted','adjudicated')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(round_id,response_id,evaluator_id),
    FOREIGN KEY(round_id) REFERENCES evaluation_rounds(round_id),
    FOREIGN KEY(response_id) REFERENCES responses(response_id),
    FOREIGN KEY(evaluator_id) REFERENCES evaluator_registry(evaluator_id)
);
ALTER TABLE human_evaluations ADD COLUMN round_id TEXT REFERENCES evaluation_rounds(round_id);
ALTER TABLE human_evaluations ADD COLUMN assignment_id TEXT REFERENCES evaluation_assignments(assignment_id);
ALTER TABLE human_evaluations ADD COLUMN evaluator_id TEXT REFERENCES evaluator_registry(evaluator_id);
ALTER TABLE human_evaluations ADD COLUMN submitted_at TEXT;
ALTER TABLE automated_evaluations ADD COLUMN round_id TEXT REFERENCES evaluation_rounds(round_id);
ALTER TABLE automated_evaluations ADD COLUMN judge_prompt TEXT;
ALTER TABLE automated_evaluations ADD COLUMN provider TEXT;
ALTER TABLE automated_evaluations ADD COLUMN parameters_json TEXT NOT NULL DEFAULT '{}';
ALTER TABLE automated_evaluations ADD COLUMN attempt INTEGER NOT NULL DEFAULT 1;
CREATE TABLE IF NOT EXISTS response_claims (
    claim_id TEXT PRIMARY KEY,
    response_id TEXT NOT NULL,
    ordinal INTEGER NOT NULL,
    claim_text TEXT NOT NULL,
    UNIQUE(response_id,ordinal),
    FOREIGN KEY(response_id) REFERENCES responses(response_id)
);
CREATE TABLE IF NOT EXISTS claim_evidence (
    claim_id TEXT NOT NULL,
    citation_id TEXT,
    support TEXT NOT NULL CHECK(support IN ('complete','partial','absent')),
    note TEXT,
    evaluator_id TEXT NOT NULL,
    PRIMARY KEY(claim_id,citation_id,evaluator_id),
    FOREIGN KEY(claim_id) REFERENCES response_claims(claim_id),
    FOREIGN KEY(citation_id) REFERENCES citations(citation_id),
    FOREIGN KEY(evaluator_id) REFERENCES evaluator_registry(evaluator_id)
);

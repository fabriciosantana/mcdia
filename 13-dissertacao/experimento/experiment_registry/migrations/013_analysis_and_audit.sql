CREATE TABLE IF NOT EXISTS analysis_reports (
    report_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    protocol_id TEXT NOT NULL,
    report_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(run_id) REFERENCES experiment_runs(run_id),
    FOREIGN KEY(protocol_id) REFERENCES evaluation_protocols(protocol_id)
);
CREATE TABLE IF NOT EXISTS audit_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    action TEXT NOT NULL,
    actor TEXT,
    detail_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TRIGGER IF NOT EXISTS prevent_frozen_battery_member_insert BEFORE INSERT ON battery_members
WHEN (SELECT state FROM question_batteries WHERE battery_id=NEW.battery_id) IN ('frozen','archived')
BEGIN SELECT RAISE(ABORT,'frozen battery is immutable'); END;
CREATE TRIGGER IF NOT EXISTS prevent_frozen_battery_member_update BEFORE UPDATE ON battery_members
WHEN (SELECT state FROM question_batteries WHERE battery_id=OLD.battery_id) IN ('frozen','archived')
BEGIN SELECT RAISE(ABORT,'frozen battery is immutable'); END;
CREATE TRIGGER IF NOT EXISTS prevent_frozen_battery_member_delete BEFORE DELETE ON battery_members
WHEN (SELECT state FROM question_batteries WHERE battery_id=OLD.battery_id) IN ('frozen','archived')
BEGIN SELECT RAISE(ABORT,'frozen battery is immutable'); END;

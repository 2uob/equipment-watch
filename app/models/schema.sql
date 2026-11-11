CREATE TABLE IF NOT EXISTS equipment (
    id INTEGER PRIMARY KEY,
    code TEXT NOT NULL UNIQUE, -- 'EQ-01'
    name TEXT NOT NULL,
    site TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1 -- 1 = 감시대상
);

CREATE TABLE IF NOT EXISTS reading (
    id INTEGER PRIMARY KEY,
    equipment_id INTEGER NOT NULL REFERENCES equipment(id),
    measured_at TEXT NOT NULL,
    metric TEXT NOT NULL,
    value REAL NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_reading_eq_time ON reading(
    equipment_id, measured_at
);

CREATE TABLE IF NOT EXISTS alert (
    id INTEGER PRIMARY KEY,
    equipment_id INTEGER NOT NULL REFERENCES equipment(id),
    monitor TEXT NOT NULL,
    level TEXT NOT NULL,
    opened_at TEXT NOT NULL,
    closed_at TEXT,
    message TEXT NOT NULL,
    suppressed_by INTEGER REFERENCES alert(id),
    is_shadow INTEGER NOT NULL DEFAULT 0,
    dispatched_at TEXT
);

CREATE TABLE IF NOT EXISTS dispatch_log (
    id INTEGER PRIMARY KEY,
    alert_id INTEGER NOT NULL REFERENCES alert(id),
    channel TEXT NOT NULL,
    sent_at TEXT NOT NULL,
    payload TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS diagnostic_run (
    id INTEGER PRIMARY KEY,
    equipment_id INTEGER NOT NULL REFERENCES equipment(id),
    started_at TEXT NOT NULL,
    finished_at TEXT,
    rule_verdict TEXT NOT NULL,
    rule_reason TEXT NOT NULL,
    llm_summary TEXT,
    llm_model TEXT,
    llm_status TEXT NOT NULL DEFAULT 'skipped',
    llm_elapsed_ms INTEGER
);

CREATE TABLE IF NOT EXISTS diagnostic_item (
    id INTEGER PRIMARY KEY,
    run_id INTEGER NOT NULL REFERENCES diagnostic_run(id),
    seq INTEGER NOT NULL,
    name TEXT NOT NULL,
    command TEXT NOT NULL,
    expected TEXT NOT NULL,
    observed TEXT NOT NULL,
    matched INTEGER NOT NULL,
    rule_code TEXT
);
import sqlite3
from pathlib import Path
from config import DB_PATH

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS person (

    -- Core identifying attributes (the golden record)
    person_id            TEXT PRIMARY KEY,
    first_name           TEXT,
    last_name            TEXT,
    dob                  TEXT,
    zip                  TEXT,

    -- Multi-tier hashed keys (deterministic, stored for matching)
    id_key_strict_name_dob_zip        TEXT UNIQUE,   -- first|last|dob|zip
    id_key_medium_name_dob    TEXT UNIQUE,   -- first|last|dob
    id_key_medium_name_zip    TEXT UNIQUE,   -- first|last|zip
    id_key_weak_name          TEXT,          -- first|last (NOT unique!)

    -- Audit metadata
    created_timestamp    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_timestamp    TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

CREATE TABLE IF NOT EXISTS validation_run (
    run_id TEXT PRIMARY KEY,
    dataset_name TEXT,
    run_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    organization TEXT,
    quarter TEXT,
    triggered_by TEXT,
    completed INTEGER CHECK (completed IN (0, 1)),
    run_description TEXT
);

CREATE TABLE IF NOT EXISTS participant (
    participant_id TEXT PRIMARY KEY,
    person_id TEXT NOT NULL,
    dataset_name TEXT NOT NULL,  -- "training data (CC)" or "TPI (GJC)" 
    org TEXT,                     -- EWIB, CWP, NCR, etc.
    
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (person_id) REFERENCES person(person_id)
);

CREATE TABLE IF NOT EXISTS dataset_column (
    column_id TEXT PRIMARY KEY,
    dataset_name TEXT,
    sheet_name TEXT,
    column_name TEXT,
    UNIQUE(dataset_name, sheet_name, column_name)
);

CREATE TABLE IF NOT EXISTS participant_presence_log(
    run_id TEXT,
    participant_id TEXT,
    status TEXT,
    row_number INT,
    sheet_name TEXT NOT NULL,     -- which sheet this row came from
    quarter TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (run_id, participant_id),
    FOREIGN KEY (run_id) REFERENCES validation_run(run_id),
    FOREIGN KEY (participant_id) REFERENCES participant(participant_id)
);

CREATE TABLE IF NOT EXISTS cell_value_history (
    history_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    participant_id TEXT NOT NULL,
    column_id TEXT NOT NULL,
    value_raw TEXT,
    value_normalized TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES validation_run(run_id),
    FOREIGN KEY (participant_id) REFERENCES participant(participant_id),
    FOREIGN KEY (column_id) REFERENCES dataset_column(column_id)
);

CREATE TABLE IF NOT EXISTS validation_rule (
    rule_id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_name TEXT,
    rule_type TEXT,
    logic_json TEXT,
    description TEXT
);

CREATE TABLE IF NOT EXISTS validation_violation (
    violation_id TEXT PRIMARY KEY,
    run_id TEXT,
    rule_id TEXT,
    participant_id TEXT,
    column_id TEXT,
    normalized TEXT,
    raw_value TEXT,
    severity TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS participant_key_mismatch (
    mismatch_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,

    org TEXT NOT NULL,
    quarter TEXT NOT NULL,
    sheet_name TEXT NOT NULL,

    id_key TEXT NOT NULL,
    issue TEXT NOT NULL,          -- e.g. duplicate_in_sheet, missing_in_other_sheet, etc.

    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (run_id) REFERENCES validation_run(run_id)
);

CREATE INDEX IF NOT EXISTS idx_ppl_run_status ON participant_presence_log(run_id, status);
CREATE INDEX IF NOT EXISTS idx_ppl_participant_run ON participant_presence_log(participant_id, run_id, status);

CREATE INDEX IF NOT EXISTS idx_vr_org_dataset_quarter_ts ON validation_run(organization, dataset_name, quarter, run_timestamp);
CREATE INDEX IF NOT EXISTS idx_vr_run_ts ON validation_run(run_id, run_timestamp);

CREATE INDEX IF NOT EXISTS idx_cvh_run_part_col ON cell_value_history(run_id, participant_id, column_id);
CREATE INDEX IF NOT EXISTS idx_cvh_part_col_run ON cell_value_history(participant_id, column_id, run_id);

CREATE INDEX IF NOT EXISTS idx_dc_dataset_sheet_colname ON dataset_column(dataset_name, sheet_name, column_name);
CREATE INDEX IF NOT EXISTS idx_vv_run_rule ON validation_violation(run_id, rule_id);

"""

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    conn.close()
    print(f"✅ SQLite DB initialized at: {DB_PATH}")

if __name__ == "__main__":
    init_db()

"""
SQLite Schema Initialization
============================

This module defines and initializes the core SQLite schema used by the
OWS validation engine. The database supports:

- participant identity resolution,
- longitudinal validation tracking,
- normalized cell-value history,
- rule-based validation auditing,
- participant presence monitoring across runs, and
- cross-run change detection.

Overview
--------
The schema is designed to support reproducible, auditable validation of
externally submitted Excel workbooks (e.g., CareerConneCT and Good Jobs
Challenge datasets). Rather than treating each workbook as an isolated
file, the database preserves historical validation context across runs.

Core Tables
-----------
person
    Canonical identity table representing the "golden record" for an
    individual participant. Stores deterministic matching keys used for
    participant resolution across submissions.

participant
    Dataset-specific participant instance linked to a canonical person.
    Allows the same individual to appear across organizations, datasets,
    and reporting periods.

validation_run
    Metadata describing a single validation execution, including dataset,
    organization, quarter, timestamp, and completion status.

participant_presence_log
    Tracks whether participants were present or missing during a given
    validation run. Supports longitudinal monitoring and disappearance
    detection across submissions.

dataset_column
    Registry of normalized dataset columns used for historical value
    tracking and rule evaluation.

cell_value_history
    Stores raw and normalized cell values over time for each participant
    and column combination. Enables change detection and audit tracing.

validation_rule
    Registry of configured validation rules and associated metadata.

validation_violation
    Stores rule violations generated during validation runs.

participant_key_mismatch
    Tracks identifier inconsistencies and duplicate-key issues detected
    across sheets or workbooks.

Design Notes
------------
The schema emphasizes:

- auditability over minimal storage,
- deterministic participant tracking,
- support for cross-run comparisons,
- normalized relational structure, and
- compatibility with SQLite-based local workflows.

Indexes are included for the most common validation-engine access
patterns, including:

- participant presence lookups,
- historical value retrieval,
- run-based reporting, and
- rule violation analysis.

Functions
---------
init_db()
    Creates all tables and indexes defined in ``SCHEMA_SQL`` if they do
    not already exist.
"""
import sqlite3
from config import TEST_DB_PATH

VALIDATION_SCHEMA_SQL = """
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

def init_db(db_path):

    """
    Initialize the SQLite validation database.

    Creates all tables, indexes, and constraints defined in
    ``VALIDATION_SCHEMA_SQL`` if they do not already exist.

    Foreign-key enforcement is enabled prior to schema creation.

    Returns
    -------
    None
    """

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.executescript(VALIDATION_SCHEMA_SQL)
    conn.commit()
    conn.close()
    print(f"✅ SQLite DB initialized at: {db_path}")

if __name__ == "__main__":
    init_db()

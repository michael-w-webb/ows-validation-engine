import sqlite3
import pandas as pd
from pathlib import Path

pd.set_option("display.max_colwidth", None)
pd.set_option("display.width", 0)
pd.set_option("display.max_columns", None)

DB_PATH = Path(__file__).parent / "validation_dev.db"
conn = sqlite3.connect(DB_PATH)

print(f"\n🔍 Inspecting Validation DB: {DB_PATH}\n")


# ============================================================
# 1️⃣ Recent validation runs
# ============================================================
runs = pd.read_sql_query("""
    SELECT run_id, dataset_name, organization, quarter, 
           triggered_by, run_timestamp
    FROM validation_run
    ORDER BY run_timestamp DESC
    LIMIT 20
""", conn)

print("=== Recent validation runs ===")
print(runs, "\n")


# ============================================================
# 2️⃣ People table
# ============================================================
people = pd.read_sql_query("""
    SELECT person_id,
           first_name, last_name, dob, zip,
           id_key_strict_name_dob_zip,
           id_key_medium_name_dob,
           id_key_medium_name_zip,
           id_key_weak_name,
           created_timestamp, updated_timestamp
    FROM person
    ORDER BY created_timestamp DESC
    LIMIT 20
""", conn)

print("=== Person records (golden identities) ===")
print(people, "\n")


# ============================================================
# 3️⃣ Participant table
# ============================================================
participants = pd.read_sql_query("""
    SELECT participant_id,
           person_id,
           dataset_name, sheet_name,
           org, quarter,
           row_number,
           created_timestamp
    FROM participant
    ORDER BY created_timestamp DESC
    LIMIT 20
""", conn)

print("=== Participant records (each upload row mapped to a person) ===")
print(participants, "\n")


# ============================================================
# 4️⃣ Participant presence per run
# ============================================================
presence = pd.read_sql_query("""
    SELECT run_id, participant_id, status, timestamp
    FROM participant_presence_log
    ORDER BY timestamp DESC
    LIMIT 20
""", conn)

print("=== Participant presence across runs ===")
print(presence, "\n")


# ============================================================
# 5️⃣ Logged cell values
# ============================================================
cell_history = pd.read_sql_query("""
    SELECT history_id,
           run_id,
           participant_id,
           column_id,
           value_raw,
           value_normalized,
           timestamp
    FROM cell_value_history
    ORDER BY timestamp DESC
    LIMIT 20
""", conn)

print("=== Cell value history (normalized sheet-by-sheet snapshots) ===")
print(cell_history, "\n")


# ============================================================
# 6️⃣ Dataset column registry
# ============================================================
columns = pd.read_sql_query("""
    SELECT column_id, dataset_name, sheet_name, column_name
    FROM dataset_column
    ORDER BY dataset_name, sheet_name, column_name
    LIMIT 30
""", conn)

print("=== Registered dataset columns ===")
print(columns, "\n")


# ============================================================
# 7️⃣ Validation violations (optional table)
# ============================================================
# Only show if the table exists
try:
    violations = pd.read_sql_query("""
        SELECT rule_id, normalized, raw_value, severity, timestamp
        FROM validation_violation
        ORDER BY timestamp DESC
        LIMIT 20
    """, conn)

    print("=== Validation violations (if logging enabled) ===")
    print(violations, "\n")

except Exception:
    print("=== Validation violations table not found ===\n")



error_count = pd.read_sql_query("""SELECT rule_id,
       COUNT(*) AS hits
FROM validation_violation
GROUP BY rule_id
ORDER BY hits DESC;""", conn)

print(error_count)


conn.close()

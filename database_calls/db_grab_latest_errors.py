import sqlite3
import pandas as pd
from pathlib import Path

# ======================
# CONFIG
# ======================

DB_PATH = Path("validation_dev.db")
ORG = "TWP"

# ======================
# CONNECT
# ======================

conn = sqlite3.connect(DB_PATH)

# ======================
# QUERY
# ======================

query = """
WITH latest_run AS (
    SELECT run_id
    FROM validation_run
    WHERE organization = ?
    ORDER BY run_timestamp DESC
    LIMIT 1
)

SELECT
    v.run_id,
    v.participant_id,
    dc.sheet_name,
    dc.column_name,
    v.raw_value,
    v.normalized,
    vr.rule_id,
    vr.rule_name,
    vr.rule_type,
    vr.description,
    v.severity
FROM validation_violation v
JOIN latest_run lr
    ON v.run_id = lr.run_id
LEFT JOIN validation_rule vr
    ON v.rule_id = vr.rule_id
LEFT JOIN dataset_column dc
    ON v.column_id = dc.column_id
ORDER BY dc.sheet_name, dc.column_name, v.participant_id;
"""

df = pd.read_sql_query(query, conn, params=[ORG])

# ======================
# OUTPUT
# ======================

print(f"\nCross-rule violations for most recent {ORG} run:\n")
print(df)

# Optional export
output_path = Path(f"{ORG}_latest_cross_rule_errors.xlsx")
df.to_excel(output_path, index=False)

print(f"\nSaved to: {output_path}")

conn.close()
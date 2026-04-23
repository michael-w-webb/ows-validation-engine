#!/usr/bin/env python3
"""
Aggregate export (single sheet) with columns:
Org, column_name, column_values, counts

Behavior:
- Uses value_normalized from cell_value_history.
- Normalizes dataset_column.column_name by lower-casing for matching.
- Restricts to each participant's latest run (by validation_run.run_timestamp).
- Counts distinct participant_id per (Org, column_name, column_values).
- Writes a single Excel sheet named "aggregates".

Open this file and click Run (no CLI args needed).
"""

import sqlite3
from pathlib import Path
import pandas as pd


# ============================
# 🔧 CONFIG (edit as needed)
# ============================

# Columns to aggregate (case-insensitive match to dataset_column.column_name)
COLUMN_NAMES = [
    "gender",
    # "credential_type_1",
    # "dislocated_worker",
    # "employment_status_at_exit",
    # "ethnicity",
]

# Output Excel path (single sheet)
OUTPUT_PATH = Path(r"C:\Users\DalyRob\Desktop\aggregates.xlsx")

# SQLite database path
DB_PATH = Path(r"C:\Users\DalyRob\OneDrive - State of Connecticut\Documents\GitHub Repos\ows-validation-engine\validation_dev.db")


# ----------------------------------------------
# SQL template: compute Org counts for one column
# ----------------------------------------------
SQL_COUNTS_BY_ORG_VALUE = r"""
WITH latest_run_per_participant AS (
    -- Determine the latest run per participant by run_timestamp
    SELECT
        cvh.participant_id,
        vr.run_id,
        vr.run_timestamp,
        ROW_NUMBER() OVER (
            PARTITION BY cvh.participant_id
            ORDER BY vr.run_timestamp DESC, vr.run_id DESC
        ) AS rn
    FROM cell_value_history AS cvh
    JOIN validation_run      AS vr
      ON vr.run_id = cvh.run_id
),
participants_with_latest_run AS (
    SELECT participant_id, run_id
    FROM latest_run_per_participant
    WHERE rn = 1
),
filtered_cvh AS (
    -- Keep only rows from each participant's latest run, join to columns
    SELECT
        cvh.participant_id,
        cvh.column_id,
        cvh.value_normalized,
        cvh.timestamp,
        LOWER(dc.column_name) AS column_name_norm
    FROM cell_value_history AS cvh
    JOIN participants_with_latest_run AS plr
      ON plr.participant_id = cvh.participant_id
     AND plr.run_id = cvh.run_id
    JOIN dataset_column AS dc
      ON dc.column_id = cvh.column_id
),
latest_values AS (
    -- Latest value per (participant, column_name) within the latest run
    SELECT
        participant_id,
        column_name_norm AS column_name,
        COALESCE(NULLIF(TRIM(value_normalized), ''), 'Unknown') AS value_normalized,
        timestamp,
        ROW_NUMBER() OVER (
            PARTITION BY participant_id, column_name_norm
            ORDER BY timestamp DESC
        ) AS rn
    FROM filtered_cvh
),
latest_target AS (
    -- Restrict to the target column and take the latest row (exists implies participant has a value for this column)
    SELECT
        participant_id,
        value_normalized AS column_values
    FROM latest_values
    WHERE column_name = ? AND rn = 1
)
SELECT
    COALESCE(p.org, 'Unknown')            AS Org,
    ?                                      AS column_name,
    COALESCE(lt.column_values, 'Unknown')  AS column_values,
    COUNT(DISTINCT p.participant_id)       AS counts
FROM participant AS p
JOIN participants_with_latest_run AS plr
  ON plr.participant_id = p.participant_id
JOIN latest_target AS lt
  ON lt.participant_id = p.participant_id
GROUP BY Org, column_name, column_values
ORDER BY Org, column_name, column_values;
"""


def run_query_for_column(conn: sqlite3.Connection, target_col: str) -> pd.DataFrame:
    """
    Execute the aggregation SQL for a single target column name.

    Args:
        conn: sqlite3 connection
        target_col: the dataset_column.column_name to aggregate (case-insensitive)

    Returns:
        pandas DataFrame with columns:
        Org, column_name, column_values, counts
    """
    # We match on lower(column_name) inside SQL; second param is the label to print in output
    params = (target_col.strip().lower(), target_col.strip())
    df = pd.read_sql_query(SQL_COUNTS_BY_ORG_VALUE, conn, params=params)
    return df


def main():
    # Basic checks
    if not DB_PATH.exists():
        raise FileNotFoundError(f"DB not found at: {DB_PATH}")

    # Connect
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA foreign_keys = ON;")

    all_frames = []
    for col in COLUMN_NAMES:
        df = run_query_for_column(conn, col)
        # Stable sort—ensures consistent final ordering across concatenated frames
        df = df.sort_values(by=["Org", "column_name", "column_values"], kind="mergesort")
        all_frames.append(df)

    conn.close()

    # Concatenate all target column frames
    if all_frames:
        out_df = pd.concat(all_frames, ignore_index=True)
    else:
        out_df = pd.DataFrame(columns=["Org", "column_name", "column_values", "counts"])

    # Write single-sheet Excel
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(OUTPUT_PATH, engine="openpyxl") as writer:
        out_df.to_excel(writer, index=False, sheet_name="aggregates")

    print(f"✅ Wrote aggregates to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
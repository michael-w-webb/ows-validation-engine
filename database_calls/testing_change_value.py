import pandas as pd
import sqlite3
from config import DB_PATH

def get_value_changes(conn, curr_id, prev_id):
    return pd.read_sql_query("""
    WITH current_run AS (
        SELECT 
            participant_id, 
            column_id,
            CASE
                WHEN value_normalized IS NULL THEN NULL
                WHEN LOWER(TRIM(value_normalized)) IN ('', 'nan', '<na>', '<nat>', 'none') THEN NULL
                ELSE TRIM(value_normalized)
            END AS val
        FROM cell_value_history
        WHERE run_id = :curr_id
    ),
    previous_run AS (
        SELECT 
            participant_id, 
            column_id,
            CASE
                WHEN value_normalized IS NULL THEN NULL
                WHEN LOWER(TRIM(value_normalized)) IN ('', 'nan', '<na>', '<nat>', 'none') THEN NULL
                ELSE TRIM(value_normalized)
            END AS val
        FROM cell_value_history
        WHERE run_id = :prev_id
    )
    SELECT 
        COALESCE(c.participant_id, p.participant_id) AS participant_id,
        COALESCE(c.column_id, p.column_id) AS column_id,
        dc.column_name,
        p.val AS old_value,
        c.val AS new_value
    FROM current_run c
    FULL OUTER JOIN previous_run p 
        ON c.participant_id = p.participant_id 
       AND c.column_id = p.column_id
    LEFT JOIN dataset_column dc
        ON dc.column_id = COALESCE(c.column_id, p.column_id)
    WHERE c.val IS NOT p.val;
    """, conn, params={"curr_id": curr_id, "prev_id": prev_id})

conn = sqlite3.connect(DB_PATH)

dataset_name = "TPI"

orgs = pd.read_sql_query("""
SELECT DISTINCT organization
FROM validation_run
WHERE dataset_name = ?
  AND completed = 1
""", conn, params=[dataset_name])

all_dfs = []

for org in orgs["organization"]:

    run_lookup = pd.read_sql_query("""
    SELECT run_id, quarter, run_timestamp
    FROM validation_run
    WHERE organization = ?
      AND dataset_name = ?
      AND completed = 1
    ORDER BY run_timestamp
    """, conn, params=[org, dataset_name])

    if run_lookup.empty:
        continue

    latest_runs = (
        run_lookup
        .sort_values("run_timestamp")
        .drop_duplicates("quarter", keep="last")
        .sort_values("run_timestamp")
        .reset_index(drop=True)
    )

    # build adjacent comparisons
    for i in range(1, len(latest_runs)):
        prev_row = latest_runs.iloc[i - 1]
        curr_row = latest_runs.iloc[i]

        df = get_value_changes(
            conn,
            curr_id=curr_row["run_id"],
            prev_id=prev_row["run_id"]
        )

        if df.empty:
            continue

        df["organization"] = org
        df["from_quarter"] = prev_row["quarter"]
        df["to_quarter"] = curr_row["quarter"]

        all_dfs.append(df)

final_df = pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame()

final_df.to_csv("value_changes_all_orgs.csv")
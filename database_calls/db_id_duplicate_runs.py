import sqlite3
import pandas as pd
from pathlib import Path
import os

DOCUMENTS = Path(os.environ["DOCUMENTS"])

DB_PATH = Path(__file__).parent / "validation_dev.db"
conn = sqlite3.connect(DB_PATH)

df = pd.read_sql_query("""
SELECT
    organization,
    dataset_name,
    quarter,
    COUNT(*) AS run_count,
    MIN(run_timestamp) AS first_run,
    MAX(run_timestamp) AS last_run
FROM validation_run
GROUP BY organization, dataset_name, quarter
HAVING COUNT(*) > 1
ORDER BY run_count DESC;""", conn)

print(df)

df_row_count = pd.read_sql_query("""
SELECT
    vr.run_id,
    vr.organization,
    vr.dataset_name,
    vr.quarter,
    COUNT(l.participant_id) AS row_count
FROM validation_run vr
LEFT JOIN participant_presence_log l
  ON l.run_id = vr.run_id
GROUP BY vr.run_id
ORDER BY row_count ASC;""", conn)

print(df_row_count)

output_path = DOCUMENTS / "dfs_with_row_count.csv"

df_row_count.to_csv(output_path)

    
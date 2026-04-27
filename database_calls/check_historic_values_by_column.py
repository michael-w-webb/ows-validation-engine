import sqlite3
import pandas as pd
from config import DB_PATH

conn = sqlite3.connect(DB_PATH)

query = """SELECT
    p.person_id,
    pe.first_name,
    pe.last_name,
    vr.quarter,
    cvh.value_normalized,
    vr.run_timestamp
FROM participant p
JOIN person pe 
    ON p.person_id = pe.person_id
JOIN cell_value_history cvh 
    ON p.participant_id = cvh.participant_id
JOIN dataset_column dc 
    ON cvh.column_id = dc.column_id
JOIN validation_run vr
    ON cvh.run_id = vr.run_id
WHERE p.org = 'Charter_Oak_State_College_Foundation'
  AND dc.column_name = 'Employment Status at exit'
ORDER BY p.person_id, vr.run_timestamp;"""

df = pd.read_sql_query(query, conn)
conn.close()

df = df.sort_values('run_timestamp')
df = df.drop_duplicates(
    subset=['person_id', 'quarter'],
    keep='last'
)

df_pivot = df.pivot_table(
    index=['first_name', 'last_name'],
    columns='quarter',
    values='value_normalized',
    aggfunc='first'
)

df_pivot = df_pivot.reset_index()

df_pivot.to_csv("employment_status_history.csv", index=False)
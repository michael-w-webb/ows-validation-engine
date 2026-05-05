import pandas as pd
import sqlite3
from config import DB_PATH

conn = sqlite3.connect(DB_PATH)

df = pd.read_sql_query("""SELECT
    cvh.run_id,
    vr.organization,
    vr.quarter,
    dc.column_name,
    cvh.value_raw,
    cvh.value_normalized,
    cvh.timestamp
FROM cell_value_history cvh
JOIN dataset_column dc
    ON cvh.column_id = dc.column_id
JOIN validation_run vr
    ON cvh.run_id = vr.run_id
WHERE cvh.participant_id = '242cb2a8-6223-4844-95d0-d8059e18670e'
  AND dc.column_name = 'Employment Status at exit'
  AND vr.organization = 'Charter_Oak_State_College_Foundation'
ORDER BY vr.run_timestamp;""", conn)

print(df["value_raw"])
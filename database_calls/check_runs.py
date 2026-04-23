import sqlite3
import pandas as pd
from config import DB_PATH

conn = sqlite3.connect(DB_PATH)
    

query = """
SELECT
    run_id AS run,
    organization AS org,
    quarter,
    run_description
FROM validation_run
WHERE quarter = 'PY4_Q3'
  AND run_description IS NULL
ORDER BY run_timestamp DESC;
"""

df = pd.read_sql_query(query, conn)

print(df)
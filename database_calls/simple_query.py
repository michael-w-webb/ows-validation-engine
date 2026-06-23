import sqlite3
from config import DB_PATH
import pandas as pd


conn = sqlite3.connect(DB_PATH)

df = pd.read_sql_query("""

SELECT
    COUNT(*) AS participants_with_presence
FROM participant pt

LEFT JOIN cell_value_history cvh
    ON pt.participant_id = cvh.participant_id

INNER JOIN participant_presence_log ppl
    ON pt.participant_id = ppl.participant_id

WHERE cvh.participant_id IS NULL;

""", conn)

print(df)

conn.close()
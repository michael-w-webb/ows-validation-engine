import sqlite3
from config import DB_PATH

conn = sqlite3.connect(DB_PATH)

cursor = conn.execute("""

DELETE FROM validation_run
WHERE run_id IN (

    SELECT vr.run_id
    FROM validation_run vr

    LEFT JOIN cell_value_history cvh
        ON vr.run_id = cvh.run_id

    LEFT JOIN participant_presence_log ppl
        ON vr.run_id = ppl.run_id

    WHERE
        cvh.run_id IS NULL
        AND ppl.run_id IS NULL

);
                                      
""")

conn.commit()

print(f"Deleted {cursor.rowcount} rows.")

conn.close()
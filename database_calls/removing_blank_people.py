import pandas as pd
import sqlite3
from config import DB_PATH

conn = sqlite3.connect(DB_PATH)

conn.executescript("""

BEGIN TRANSACTION;

-- Remove cell history
DELETE FROM cell_value_history
WHERE participant_id IN (

    SELECT participant_id
    FROM participant
    WHERE person_id IN (
        SELECT person_id
        FROM person
        WHERE first_name IS NULL
          AND last_name IS NULL
    )

);

-- Remove presence logs
DELETE FROM participant_presence_log
WHERE participant_id IN (

    SELECT participant_id
    FROM participant
    WHERE person_id IN (
        SELECT person_id
        FROM person
        WHERE first_name IS NULL
          AND last_name IS NULL
    )

);

-- Remove validation violations
DELETE FROM validation_violation
WHERE participant_id IN (

    SELECT participant_id
    FROM participant
    WHERE person_id IN (
        SELECT person_id
        FROM person
        WHERE first_name IS NULL
          AND last_name IS NULL
    )

);

                   
-- Remove participants
DELETE FROM participant
WHERE person_id IN (
    SELECT person_id
    FROM person
    WHERE first_name IS NULL
      AND last_name IS NULL
);

-- Finally remove people
DELETE FROM person
WHERE first_name IS NULL
  AND last_name IS NULL;

COMMIT;
                       
""")

print("query finished.")
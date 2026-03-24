import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path(__file__).parent / "validation_dev.db"
conn = sqlite3.connect(DB_PATH)

find_value = pd.read_sql_query("""
WITH personal_columns AS (
    SELECT column_id, column_name
    FROM dataset_column
    WHERE dataset_name = 'training data'
      AND sheet_name = 'Report'
),

provider_by_quarter AS (
    SELECT
        cvh.participant_id,
        pc.column_name,
        ppl.quarter,
        cvh.value_normalized AS value_of_interest,
        ROW_NUMBER() OVER (
            PARTITION BY cvh.participant_id, pc.column_name, ppl.quarter
            ORDER BY cvh.timestamp DESC
        ) AS rn
    FROM cell_value_history cvh
    JOIN personal_columns pc
      ON cvh.column_id = pc.column_id
    JOIN participant_presence_log ppl
      ON cvh.run_id = ppl.run_id
     AND cvh.participant_id = ppl.participant_id
),

latest_values AS (
    SELECT
        participant_id,
        column_name,
        quarter,
        value_of_interest
    FROM provider_by_quarter
    WHERE rn = 1
),

participants_with_changes AS (
    SELECT participant_id, column_name
    FROM latest_values
    GROUP BY participant_id, column_name
    HAVING COUNT(DISTINCT value_of_interest) FILTER (
        WHERE value_of_interest IS NOT NULL
    ) > 1
)

SELECT
    p.participant_id,
    p.person_id,
    p.dataset_name,
    p.org,
    lv.column_name,
    lv.quarter,
    lv.value_of_interest

FROM latest_values lv
JOIN participants_with_changes pwc
  ON lv.participant_id = pwc.participant_id
 AND lv.column_name = pwc.column_name
JOIN participant p
  ON p.participant_id = lv.participant_id

ORDER BY
    p.org,
    lv.column_name,
    p.participant_id,
    lv.quarter;
""", conn)

find_value.to_csv(r"C:\Users\webbm\OneDrive - State of Connecticut\Documents\find_value_report.csv", index=False)

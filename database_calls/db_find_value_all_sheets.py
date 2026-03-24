import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path(__file__).parent / "validation_dev.db"
conn = sqlite3.connect(DB_PATH)

find_value = pd.read_sql_query("""
WITH target_columns AS (
    SELECT
        column_id,
        column_name,
        sheet_name
    FROM dataset_column
    WHERE dataset_name = 'training data'
      AND sheet_name IN (
          'Personal Information',
          'Training',
          'Credential',
          'Outcomes',
          'Report'
      )
),

ordered_values AS (
    SELECT
        p.org,
        cvh.participant_id,
        tc.sheet_name,
        tc.column_name,
        ppl.quarter,
        cvh.value_normalized AS value_of_interest,

        LAG(cvh.value_normalized) OVER (
            PARTITION BY cvh.participant_id, tc.sheet_name, tc.column_name
            ORDER BY
                CAST(SUBSTR(ppl.quarter, 3, 1) AS INTEGER),
                CAST(SUBSTR(ppl.quarter, 6, 1) AS INTEGER)
        ) AS previous_value

    FROM cell_value_history cvh
    JOIN target_columns tc
      ON cvh.column_id = tc.column_id
    JOIN participant_presence_log ppl
      ON cvh.run_id = ppl.run_id
     AND cvh.participant_id = ppl.participant_id
    JOIN participant p
      ON p.participant_id = cvh.participant_id
),

cleaned_values AS (
    SELECT *
    FROM ordered_values
    WHERE
        value_of_interest IS NOT NULL
        AND TRIM(value_of_interest) <> ''
        AND LOWER(TRIM(value_of_interest)) <> 'nan'
        AND previous_value IS NOT NULL
        AND TRIM(previous_value) <> ''
        AND LOWER(TRIM(previous_value)) <> 'nan'
),

changes AS (
    SELECT *
    FROM cleaned_values
    WHERE LOWER(value_of_interest) <> LOWER(previous_value)
),

first_change AS (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY participant_id, sheet_name, column_name
               ORDER BY
                   CAST(SUBSTR(quarter, 3, 1) AS INTEGER),
                   CAST(SUBSTR(quarter, 6, 1) AS INTEGER)
           ) AS change_rank
    FROM changes
)

SELECT
    org,
    participant_id,
    sheet_name,
    column_name,
    previous_value AS original_value,
    value_of_interest AS new_value,
    quarter AS change_quarter

FROM first_change
WHERE change_rank = 1

ORDER BY
    org,
    sheet_name,
    column_name,
    participant_id;
""", conn)

find_value.to_csv(r"C:\Users\webbm\OneDrive - State of Connecticut\Documents\find_value_all_sheets_report.csv", index=False)

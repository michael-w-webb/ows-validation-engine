import sqlite3
import pandas as pd
from pathlib import Path

from config import (
    DB_PATH,
    OUTPUT_DIRECTORY
)

conn = sqlite3.connect(DB_PATH)

sql_query = """ WITH multi_run_participants AS (

    SELECT
        participant_id
    FROM participant_presence_log
    GROUP BY participant_id
    HAVING COUNT(DISTINCT run_id) > 1

),

eligible_participants AS (

    SELECT DISTINCT
        p.participant_id,
        p.person_id,
        p.dataset_name,
        p.org,

        pe.first_name,
        pe.last_name

    FROM participant p

    INNER JOIN multi_run_participants mrp
        ON p.participant_id = mrp.participant_id

    LEFT JOIN person pe
        ON p.person_id = pe.person_id

    INNER JOIN cell_value_history cvh
        ON p.participant_id = cvh.participant_id

    INNER JOIN dataset_column dc
        ON cvh.column_id = dc.column_id

    -- WHERE p.dataset_name = 'training data'
    WHERE p.dataset_name = 'TPI'

        -- Nonblank names
        AND pe.first_name IS NOT NULL
        AND pe.last_name IS NOT NULL

        AND TRIM(pe.first_name) != ''
        AND TRIM(pe.last_name) != ''

        -- AND dc.column_name = 'Date of Program Entry (Enrollment Date)'
        AND dc.column_name = 'Training Start Date'
        AND cvh.value_normalized IS NOT NULL

        AND DATE(cvh.value_normalized) >= DATE('2025-07-01')

        -- Training filter
        -- AND dc.column_name = 'Date Entered Training'
        -- AND cvh.value_normalized IS NOT NULL
),

ranked_participants AS (

    SELECT
        participant_id,
        person_id,
        dataset_name,
        org,
        first_name,
        last_name,

        ROW_NUMBER() OVER (
            PARTITION BY org
            ORDER BY RANDOM()
        ) AS random_rank,

        COUNT(*) OVER (
            PARTITION BY org
        ) AS org_total

    FROM eligible_participants
)

SELECT
    participant_id,
    person_id,
    first_name,
    last_name,
    dataset_name,
    org

FROM ranked_participants

WHERE random_rank <= MAX(
    5,
    CAST(org_total * 0.05 + 0.9999 AS INT)
)

ORDER BY
    org,
    random_rank;

"""

df = pd.read_sql_query(
    sql_query,
    conn
)

print(f"Rows returned: {len(df)}")
print(df.head())

conn.close()

# Create output directory if needed
sample_dir = (
    OUTPUT_DIRECTORY / "gjc_random_samples_3"
)

sample_dir.mkdir(
    parents=True,
    exist_ok=True
)

# Write one CSV per org
for org, org_df in df.groupby("org"):

    # Clean filename
    safe_org = (
        str(org)
        .strip()
        .replace("/", "_")
        .replace("\\", "_")
        .replace(" ", "_")
    )

    output_path = (
        sample_dir /
        f"{safe_org}_random_sample.csv"
    )

    org_df = org_df[["first_name","last_name"]]

    org_df.to_csv(
        output_path,
        index=False
    )

    print(
        f"Saved {len(org_df)} rows to "
        f"{output_path}"
    )
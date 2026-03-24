import sqlite3
import pandas as pd
from pathlib import Path

# ----------------------------
# CONFIG
# ----------------------------
DB_PATH = Path(__file__).resolve().parent / "validation_dev.db"
OUTPUT_PATH = Path(__file__).resolve().parent / "raw_null_audit_by_run.xlsx"

QUERY = """
SELECT
    cvh.run_id,
    vr.organization,
    vr.dataset_name,
    vr.quarter,
    vr.run_timestamp,

    COUNT(*) AS total_values,

    SUM(
        CASE
            WHEN cvh.value_raw IS NULL
              OR TRIM(cvh.value_raw) = ''
            THEN 1 ELSE 0
        END
    ) AS null_or_blank_raw_count,

    ROUND(
        100.0 *
        SUM(
            CASE
                WHEN cvh.value_raw IS NULL
                  OR TRIM(cvh.value_raw) = ''
                THEN 1 ELSE 0
            END
        ) / COUNT(*),
        2
    ) AS percent_null_or_blank_raw

FROM cell_value_history cvh
JOIN validation_run vr
    ON cvh.run_id = vr.run_id

GROUP BY
    cvh.run_id,
    vr.organization,
    vr.dataset_name,
    vr.quarter,
    vr.run_timestamp

ORDER BY vr.run_timestamp DESC;
"""

# ----------------------------
# EXECUTION
# ----------------------------
def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")

    df = pd.read_sql_query(QUERY, conn)
    conn.close()

    if df.empty:
        print("No runs found in database.")
        return

    print("\nRaw NULL Audit by Run\n")
    print(df.to_string(index=False))

    # Write to Excel
    df.to_excel(OUTPUT_PATH, index=False)
    print(f"\nSaved audit file to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
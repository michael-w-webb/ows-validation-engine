import sqlite3
import pandas as pd
from pathlib import Path

# ----------------------------
# CONFIG
# ----------------------------
DB_PATH = Path(__file__).resolve().parent / "validation_dev.db"
OUTPUT_DIR = r"C:\Users\webbm\OneDrive - State of Connecticut\Documents"

# ----------------------------
# QUERY
# ----------------------------
QUERY = """
WITH target_columns AS (
    SELECT column_id, column_name
    FROM dataset_column
    WHERE dataset_name = 'TPI'
      AND column_name IN (
            'Employment Status',
            'Training End Date'
      )
),

latest_values AS (
    SELECT
        cvh.participant_id,
        tc.column_name,
        cvh.value_normalized,
        ROW_NUMBER() OVER (
            PARTITION BY cvh.participant_id, tc.column_name
            ORDER BY cvh.timestamp DESC
        ) AS rn
    FROM cell_value_history cvh
    JOIN target_columns tc
        ON cvh.column_id = tc.column_id
    JOIN participant p
        ON cvh.participant_id = p.participant_id
    WHERE p.dataset_name = 'TPI'
),

filtered_latest AS (
    SELECT
        participant_id,
        column_name,
        value_normalized
    FROM latest_values
    WHERE rn = 1
)

SELECT
    p.participant_id,
    p.person_id,
    pr.first_name,
    pr.last_name,
    p.org,

    MAX(CASE 
        WHEN fl.column_name = 'Employment Status'
        THEN fl.value_normalized
    END) AS employment_status,

    MAX(CASE 
        WHEN fl.column_name = 'Training End Date'
        THEN fl.value_normalized
    END) AS training_end_date

FROM filtered_latest fl
JOIN participant p
    ON fl.participant_id = p.participant_id
JOIN person pr
    ON p.person_id = pr.person_id

GROUP BY 
    p.participant_id,
    p.person_id,
    pr.first_name,
    pr.last_name,
    p.org

HAVING
    employment_status IN (
        'Still seeking employment',
        'Seeking Employment',
        'Could not contact',
        'In Job Search Assistance'
    )

ORDER BY p.org, pr.last_name, pr.first_name;
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
        print("No participants found.")
        return

    # ----------------------------
    # Parse Training End Date
    # ----------------------------
    df["training_end_date_parsed"] = pd.to_datetime(
        df["training_end_date"], errors="coerce"
    )

    today = pd.Timestamp.today().normalize()

    df["days_since_training_end"] = (
        today - df["training_end_date_parsed"]
    ).dt.days

    # ----------------------------
    # Filter: 6+ months (>= 180 days)
    # ----------------------------
    df = df[df["days_since_training_end"] >= 180]

    if df.empty:
        print("No participants meet employment + 6 month criteria.")
        return

    df = df.drop(columns=["training_end_date_parsed"])

    total_written = 0

    for org, org_df in df.groupby("org"):

        safe_org = org.replace(" ", "_")
        output_path = Path(
            OUTPUT_DIR + rf"\{safe_org}_six_months_post_training.xlsx"
        )

        # Add blank columns
        org_df = org_df.copy()
        org_df["Was the wage match completed (yes/no)"] = ""
        org_df["If wage match shows unemployment, date of last attempted contact (XX/XX/XXXX)"] = ""
        org_df["Contact successful? (yes/no)"] = ""

        # ----------------------------
        # Write with ExcelWriter
        # ----------------------------
        with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:

            sheet = "Participants"

            org_df = org_df.drop(columns=["participant_id", "person_id"])

            org_df.to_excel(writer, sheet_name=sheet, index=False)

            workbook  = writer.book
            worksheet = writer.sheets[sheet]

            MIN_WRAP_THRESHOLD = 20
            MAX_WIDTH = 30

            for i, col in enumerate(org_df.columns):

                # Compute natural width from data + header
                column_series = org_df[col].astype(str)
                natural_width = max(
                    column_series.map(len).max(),
                    len(col)
                ) + 2  # padding

                if natural_width < MIN_WRAP_THRESHOLD:
                    final_width = natural_width
                else:
                    final_width = MAX_WIDTH

                worksheet.set_column(i, i, final_width)

            # Wrap format for header only
            header_format = workbook.add_format({
                "bold": True,
                "text_wrap": True,
                "valign": "top",
                "align": "center",
                "border": 1
            })

            # Rewrite header row with wrapping
            for col_num, col_name in enumerate(org_df.columns):
                worksheet.write(0, col_num, col_name, header_format)

            # Increase header row height so wrapping is visible
            worksheet.set_row(0, 45)

        print(f"{org}: {len(org_df)} participants → {output_path}")
        total_written += 1

    print(f"\nCreated {total_written} org files in:")
    print(OUTPUT_DIR)


if __name__ == "__main__":
    main()
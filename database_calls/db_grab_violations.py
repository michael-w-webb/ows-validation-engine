import sqlite3
import pandas as pd
from pathlib import Path
import argparse
import sys

DB_PATH = Path("validation_dev.db")


def main():
    parser = argparse.ArgumentParser(
        description="Export validation errors for most recent run(s) by org and quarter."
    )

    parser.add_argument(
        "quarter",
        help="Quarter (e.g., PY4_Q2)"
    )

    parser.add_argument(
        "--org",
        default="*",
        help="Organization (e.g., EWIB). Use * or omit for all orgs."
    )

    parser.add_argument(
        "--dataset",
        default=None,
        help="Optional dataset name (e.g., 'training data')"
    )

    args = parser.parse_args()

    quarter = args.quarter
    org = args.org
    dataset_name = args.dataset

    if not DB_PATH.exists():
        sys.exit(f"Database not found at {DB_PATH.resolve()}")

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")

    # -------------------------------------------------
    # Build run selection query
    # -------------------------------------------------
    if org == "*" or org is None:
        # Latest run per org for the quarter
        run_query = """
            SELECT vr.run_id
            FROM validation_run vr
            JOIN (
                SELECT organization, MAX(run_timestamp) AS max_ts
                FROM validation_run
                WHERE quarter = ?
                {dataset_filter}
                GROUP BY organization
            ) latest
            ON vr.organization = latest.organization
            AND vr.run_timestamp = latest.max_ts
            WHERE vr.quarter = ?
            {dataset_filter_2}
        """
        params = [quarter]
        dataset_filter = ""
        dataset_filter_2 = ""

        if dataset_name:
            dataset_filter = "AND dataset_name = ?"
            dataset_filter_2 = "AND vr.dataset_name = ?"
            params = [quarter, dataset_name, quarter, dataset_name]
        else:
            params = [quarter, quarter]

        run_query = run_query.format(
            dataset_filter=dataset_filter,
            dataset_filter_2=dataset_filter_2
        )

        run_df = pd.read_sql_query(run_query, conn, params=params)

    else:
        # Single org
        if dataset_name:
            run_df = pd.read_sql_query("""
                SELECT run_id
                FROM validation_run
                WHERE organization = ?
                  AND quarter = ?
                  AND dataset_name = ?
                ORDER BY run_timestamp DESC
                LIMIT 1;
            """, conn, params=[org, quarter, dataset_name])
        else:
            run_df = pd.read_sql_query("""
                SELECT run_id
                FROM validation_run
                WHERE organization = ?
                  AND quarter = ?
                ORDER BY run_timestamp DESC
                LIMIT 1;
            """, conn, params=[org, quarter])

    if run_df.empty:
        conn.close()
        sys.exit("No runs found.")

    run_ids = run_df["run_id"].tolist()

    # -------------------------------------------------
    # Pull errors for selected run(s)
    # -------------------------------------------------
    placeholders = ",".join(["?"] * len(run_ids))

    errors = pd.read_sql_query(f"""
        SELECT
            vv.violation_id,
            vv.run_id,
            vr.dataset_name,
            vr.organization,
            vr.quarter,

            vv.participant_id,
            p.person_id,
            per.first_name,
            per.last_name,

            vv.column_id,          -- <- raw column_id
            dc.column_name,        -- <- human-readable column name
            dc.sheet_name,

            vrule.rule_name,
            vrule.rule_type,

            vv.raw_value,
            vv.normalized,
            vv.severity,
            vv.timestamp

        FROM validation_violation vv
        JOIN validation_run vr
            ON vv.run_id = vr.run_id
        LEFT JOIN dataset_column dc
            ON vv.column_id = dc.column_id
        LEFT JOIN validation_rule vrule
            ON vv.rule_id = vrule.rule_id
        LEFT JOIN participant p
            ON vv.participant_id = p.participant_id
        LEFT JOIN person per
            ON p.person_id = per.person_id
        WHERE vv.run_id IN ({placeholders})
        ORDER BY vr.organization, dc.sheet_name, dc.column_name, vv.participant_id;
    """, conn, params=run_ids)

    conn.close()

    output_name = f"errors_{quarter}"
    if org != "*" and org is not None:
        output_name += f"_{org}"

    output_path = Path(f"{output_name}.csv")

    if errors.empty:
        print("No validation errors found.")
    else:
        errors.to_csv(output_path, index=False)
        print(f"Exported {len(errors)} errors to {output_path.resolve()}")


if __name__ == "__main__":
    main()
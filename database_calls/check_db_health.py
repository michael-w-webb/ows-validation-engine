# database_calls/check_db_health.py

import sqlite3
import pandas as pd

from config import DB_PATH


CHECKS = {

    # ==========================================================
    # CRITICAL
    # ==========================================================

    "participant_missing_person": {

        "severity": "critical",

        "count_query": """

            SELECT COUNT(*)
            FROM participant pt

            LEFT JOIN person p
                ON pt.person_id = p.person_id

            WHERE p.person_id IS NULL

        """,

        "breakdown_query": """

            SELECT
                pt.dataset_name,
                COUNT(*) AS cnt

            FROM participant pt

            LEFT JOIN person p
                ON pt.person_id = p.person_id

            WHERE p.person_id IS NULL

            GROUP BY
                pt.dataset_name

            ORDER BY
                cnt DESC

        """

    },

    "cvh_missing_participant": {

        "severity": "critical",

        "count_query": """

            SELECT COUNT(*)
            FROM cell_value_history cvh

            LEFT JOIN participant pt
                ON cvh.participant_id = pt.participant_id

            WHERE pt.participant_id IS NULL

        """,

        "breakdown_query": """

            SELECT
                vr.dataset_name,
                COUNT(*) AS cnt

            FROM cell_value_history cvh

            LEFT JOIN participant pt
                ON cvh.participant_id = pt.participant_id

            LEFT JOIN validation_run vr
                ON cvh.run_id = vr.run_id

            WHERE pt.participant_id IS NULL

            GROUP BY
                vr.dataset_name

            ORDER BY
                cnt DESC

        """

    },

    "cvh_missing_run": {

        "severity": "critical",

        "count_query": """

            SELECT COUNT(*)
            FROM cell_value_history cvh

            LEFT JOIN validation_run vr
                ON cvh.run_id = vr.run_id

            WHERE vr.run_id IS NULL

        """

    },

    "cvh_missing_column": {

        "severity": "critical",

        "count_query": """

            SELECT COUNT(*)
            FROM cell_value_history cvh

            LEFT JOIN dataset_column dc
                ON cvh.column_id = dc.column_id

            WHERE dc.column_id IS NULL

        """

    },

    "presence_missing_participant": {

        "severity": "critical",

        "count_query": """

            SELECT COUNT(*)
            FROM participant_presence_log ppl

            LEFT JOIN participant pt
                ON ppl.participant_id = pt.participant_id

            WHERE pt.participant_id IS NULL

        """,

        "breakdown_query": """

            SELECT
                vr.dataset_name,
                COUNT(*) AS cnt

            FROM participant_presence_log ppl

            LEFT JOIN participant pt
                ON ppl.participant_id = pt.participant_id

            LEFT JOIN validation_run vr
                ON ppl.run_id = vr.run_id

            WHERE pt.participant_id IS NULL

            GROUP BY
                vr.dataset_name

            ORDER BY
                cnt DESC

        """

    },

    "presence_missing_run": {

        "severity": "critical",

        "count_query": """

            SELECT COUNT(*)
            FROM participant_presence_log ppl

            LEFT JOIN validation_run vr
                ON ppl.run_id = vr.run_id

            WHERE vr.run_id IS NULL

        """

    },

    # ==========================================================
    # WARNINGS
    # ==========================================================

    "orphaned_persons": {

        "severity": "warning",

        "count_query": """

            SELECT COUNT(*)
            FROM person p

            LEFT JOIN participant pt
                ON p.person_id = pt.person_id

            WHERE pt.person_id IS NULL

        """

    },

    "participants_without_cvh": {

        "severity": "warning",

        "count_query": """

            SELECT COUNT(*)
            FROM participant pt

            LEFT JOIN cell_value_history cvh
                ON pt.participant_id = cvh.participant_id

            WHERE cvh.participant_id IS NULL

        """,

        "breakdown_query": """

            SELECT
                pt.dataset_name,
                COUNT(*) AS cnt

            FROM participant pt

            LEFT JOIN cell_value_history cvh
                ON pt.participant_id = cvh.participant_id

            WHERE cvh.participant_id IS NULL

            GROUP BY
                pt.dataset_name

            ORDER BY
                cnt DESC

        """

    },

    "runs_without_cvh": {

        "severity": "warning",

        "count_query": """

            SELECT COUNT(*)
            FROM validation_run vr

            LEFT JOIN cell_value_history cvh
                ON vr.run_id = cvh.run_id

            WHERE cvh.run_id IS NULL

        """,

        "breakdown_query": """

            SELECT
                vr.dataset_name,
                COUNT(*) AS cnt

            FROM validation_run vr

            LEFT JOIN cell_value_history cvh
                ON vr.run_id = cvh.run_id

            WHERE cvh.run_id IS NULL

            GROUP BY
                vr.dataset_name

            ORDER BY
                cnt DESC

        """

    },

    "runs_without_presence_logs": {

        "severity": "warning",

        "count_query": """

            SELECT COUNT(*)
            FROM validation_run vr

            LEFT JOIN participant_presence_log ppl
                ON vr.run_id = ppl.run_id

            WHERE ppl.run_id IS NULL

        """,

        "breakdown_query": """

            SELECT
                vr.dataset_name,
                COUNT(*) AS cnt

            FROM validation_run vr

            LEFT JOIN participant_presence_log ppl
                ON vr.run_id = ppl.run_id

            WHERE ppl.run_id IS NULL

            GROUP BY
                vr.dataset_name

            ORDER BY
                cnt DESC

        """

    },

    "orphaned_presence_logs": {

        "severity": "warning",

        "count_query": """

            SELECT COUNT(*)
            FROM participant_presence_log ppl

            LEFT JOIN participant pt
                ON ppl.participant_id = pt.participant_id

            WHERE pt.participant_id IS NULL

        """,

        "breakdown_query": """

            SELECT
                vr.dataset_name,
                COUNT(*) AS cnt

            FROM participant_presence_log ppl

            LEFT JOIN participant pt
                ON ppl.participant_id = pt.participant_id

            LEFT JOIN validation_run vr
                ON ppl.run_id = vr.run_id

            WHERE pt.participant_id IS NULL

            GROUP BY
                vr.dataset_name

            ORDER BY
                cnt DESC

        """

    },

    # ==========================================================
    # INFO
    # ==========================================================

    "blank_person_names": {

        "severity": "info",

        "count_query": """

            SELECT COUNT(*)
            FROM person

            WHERE
                COALESCE(first_name, '') = ''
                OR COALESCE(last_name, '') = ''

        """,

        "breakdown_query": """

            SELECT
                pt.dataset_name,
                COUNT(DISTINCT p.person_id) AS cnt

            FROM person p

            INNER JOIN participant pt
                ON p.person_id = pt.person_id

            WHERE
                COALESCE(p.first_name, '') = ''
                OR COALESCE(p.last_name, '') = ''

            GROUP BY
                pt.dataset_name

            ORDER BY
                cnt DESC

        """

    },

    "persons_missing_dob_and_zip": {

        "severity": "info",

        "count_query": """

            SELECT COUNT(DISTINCT p.person_id)

            FROM person p

            INNER JOIN participant pt
                ON p.person_id = pt.person_id

            WHERE
                p.dob IS NULL
                AND p.zip IS NULL

        """,

        "breakdown_query": """

            SELECT
                pt.dataset_name,
                COUNT(DISTINCT p.person_id) AS cnt

            FROM person p

            INNER JOIN participant pt
                ON p.person_id = pt.person_id

            WHERE
                p.dob IS NULL
                AND p.zip IS NULL

            GROUP BY
                pt.dataset_name

            ORDER BY
                cnt DESC

        """

    }

}


def _run_count_check(conn, query):

    df = pd.read_sql_query(
        query,
        conn
    )

    if df.empty:
        return 0

    return int(df.iloc[0, 0])


def _run_breakdown_check(conn, query):

    return pd.read_sql_query(
        query,
        conn
    )


def check_db_health():

    conn = sqlite3.connect(DB_PATH)

    results = {
        "status": "PASS",
        "checks": {}
    }

    try:

        for name, config in CHECKS.items():

            count = _run_count_check(
                conn,
                config["count_query"]
            )

            breakdown = pd.DataFrame()

            if "breakdown_query" in config:

                breakdown = _run_breakdown_check(
                    conn,
                    config["breakdown_query"]
                )

            results["checks"][name] = {

                "severity": config["severity"],
                "count": count,
                "breakdown": breakdown

            }

            if (
                config["severity"] == "critical"
                and count > 0
            ):

                results["status"] = "FAIL"

        return results

    finally:

        conn.close()


def print_db_health():

    results = check_db_health()

    print()
    print("=" * 80)
    print("DATABASE HEALTH CHECK")
    print("=" * 80)
    print()

    print(f"Status: {results['status']}")
    print()

    for severity in [
        "critical",
        "warning",
        "info"
    ]:

        print(f"{severity.upper()} CHECKS")
        print()

        for name, result in results["checks"].items():

            if result["severity"] != severity:
                continue

            print(
                f"  {name:<35}"
                f"{result['count']:,}"
            )

            if not result["breakdown"].empty:

                for _, row in result["breakdown"].iterrows():

                    print(
                        f"      "
                        f"{str(row['dataset_name']):<25}"
                        f"{int(row['cnt']):,}"
                    )

            print()

    print()


if __name__ == "__main__":

    print_db_health()
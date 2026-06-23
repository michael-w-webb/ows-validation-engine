import sqlite3

from api.config import WB_DEF_DB_PATH


def clear_active_validation_runs():

    conn = sqlite3.connect(WB_DEF_DB_PATH)

    try:

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT COUNT(*)

            FROM validation_run

            WHERE status IN (
                'queued',
                'running'
            )
            """
        )

        count = cursor.fetchone()[0]

        print(
            f"Found {count} active runs"
        )

        cursor.execute(
            """
            DELETE FROM validation_run

            WHERE status IN (
                'queued',
                'running'
            )
            """
        )

        conn.commit()

        print(
            f"Deleted {cursor.rowcount} rows"
        )

    finally:

        conn.close()


if __name__ == "__main__":

    clear_active_validation_runs()
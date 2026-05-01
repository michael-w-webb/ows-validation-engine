import sqlite3
from config import DB_PATH


def cleanup_py4_q3_none_runs():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")

    try:
        cur = conn.cursor()

        # Get target run_ids
        run_ids = [row[0] for row in cur.execute("""
            SELECT run_id
            FROM validation_run
            WHERE quarter = ?
            AND organization = ?
            AND dataset_name = ?                                   
              """, ("PY4_Q3", "CWP", "TPI")).fetchall()]

        if not run_ids:
            print("No matching runs found.")
            return

        placeholders = ",".join(["?"] * len(run_ids))

        # Delete dependent data
        cur.execute(f"""
            DELETE FROM cell_value_history
            WHERE run_id IN ({placeholders})
        """, run_ids)

        cur.execute(f"""
            DELETE FROM validation_violation
            WHERE run_id IN ({placeholders})
        """, run_ids)

        # Remove associations
        cur.execute(f"""
            DELETE FROM participant_presence_log
            WHERE run_id IN ({placeholders})
        """, run_ids)

        # Delete orphan participants
        cur.execute("""
            DELETE FROM participant
            WHERE participant_id NOT IN (
                SELECT DISTINCT participant_id
                FROM participant_presence_log
            )
        """)

        conn.commit()
        print(f"✅ Cleaned up {len(run_ids)} runs and orphaned participants")

    except Exception as e:
        conn.rollback()
        print("❌ Error:", e)

    finally:
        conn.close()


if __name__ == "__main__":
    cleanup_py4_q3_none_runs()
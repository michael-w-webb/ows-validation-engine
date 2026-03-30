import sqlite3
import pandas as pd
from pathlib import Path
from config import DB_PATH
import sqlite3
import pandas as pd


def apply_confirmed_matches(conn, match_df):
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("BEGIN;")

    try:
        confirmed = match_df[match_df["confirmed_match"] == 1]

        for _, row in confirmed.iterrows():
            conn.execute(
                """
                UPDATE participant
                SET person_id = ?
                WHERE participant_id = ?;
                """,
                (row["train_person_id"], row["cc_participant_id"])
            )

        # Prune orphaned person records
        conn.execute("""
            DELETE FROM person
            WHERE person_id NOT IN (
                SELECT DISTINCT person_id FROM participant
            );
        """)

        conn.commit()
        print("✅ Confirmed matches applied successfully.")

    except Exception as e:
        conn.rollback()
        print("❌ Error occurred. Rolled back.")
        raise e


def main():
    
    MATCH_FILE = Path("cc_to_ct_hires_resolved_matches.csv")

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")

    print("🔎 Loading confirmed match file...")
    match_df = pd.read_csv(MATCH_FILE)

    required_cols = {
        "cc_participant_id",
        "train_person_id",
        "confirmed_match"
    }

    if not required_cols.issubset(match_df.columns):
        raise ValueError("Match file missing required columns.")

    confirmed_count = (match_df["confirmed_match"] == 1).sum()
    print(f"✅ {confirmed_count} confirmed matches found.")

    # Pre-merge audit
    before_person_count = pd.read_sql_query(
        "SELECT COUNT(*) AS n FROM person;", conn
    )["n"].iloc[0]

    before_participant_count = pd.read_sql_query(
        "SELECT COUNT(*) AS n FROM participant;", conn
    )["n"].iloc[0]

    print(f"Before merge: {before_person_count} persons, {before_participant_count} participants")

    # Apply merge
    apply_confirmed_matches(conn, match_df)

    # Post-merge audit
    after_person_count = pd.read_sql_query(
        "SELECT COUNT(*) AS n FROM person;", conn
    )["n"].iloc[0]

    after_participant_count = pd.read_sql_query(
        "SELECT COUNT(*) AS n FROM participant;", conn
    )["n"].iloc[0]

    print(f"After merge: {after_person_count} persons, {after_participant_count} participants")
    print(f"Persons removed: {before_person_count - after_person_count}")

    conn.close()

if __name__ == "__main__":
    main()
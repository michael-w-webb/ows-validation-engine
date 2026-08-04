import sqlite3
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv


def apply_confirmed_matches(conn, match_df):
    """
    For each confirmed match, move the training/CC participant onto the
    person_id already linked with the portal participant.

    Expected columns in match_df:
      - portal_participant_id (UUID or string)
      - training_participant_id (UUID or string)
      - confirmed_match (1 = confirmed)
    """
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("BEGIN;")

    try:
        # Normalize confirmed flag to int in case it's read as string "1"/"0"
        confirmed = match_df[match_df["confirmed_match"].astype(str).str.strip().isin(["1", "true", "True"])]

        skipped_missing_ids = 0
        skipped_no_portal_person = 0
        updated_rows = 0

        for _, row in confirmed.iterrows():
            portal_pid = row.get("portal_participant_id")
            training_pid = row.get("training_participant_id")

            # Normalize to strings and strip whitespace
            portal_pid = None if pd.isna(portal_pid) else str(portal_pid).strip()
            training_pid = None if pd.isna(training_pid) else str(training_pid).strip()

            # Skip rows missing required IDs
            if not portal_pid or not training_pid:
                skipped_missing_ids += 1
                continue

            # 1) Get the person_id currently linked to the portal participant
            cur = conn.execute(
                "SELECT person_id FROM participant WHERE participant_id = ?;",
                (portal_pid,)
            )
            rec = cur.fetchone()
            if not rec or rec[0] is None or str(rec[0]).strip() == "":
                # No person_id on portal participant; optionally log for follow-up
                skipped_no_portal_person += 1
                continue

            portal_person_id = str(rec[0]).strip()

            # 2) Point the training participant at the portal's person_id so that it gets their race, gender, and ethnicity data
            conn.execute(
                """
                UPDATE participant
                SET person_id = ?
                WHERE participant_id = ?;
                """,
                (portal_person_id, training_pid)
            )
            updated_rows += 1

        # 3) Prune orphaned person records (no participants pointing to them)
        conn.execute("""
            DELETE FROM person
            WHERE person_id NOT IN (
                SELECT DISTINCT person_id
                FROM participant
                WHERE person_id IS NOT NULL
            );
        """)

        conn.commit()
        print("✅ Confirmed matches applied successfully.")
        print(f"   ↳ Updated training participants: {updated_rows}")
        print(f"   ↳ Skipped (missing IDs): {skipped_missing_ids}")
        print(f"   ↳ Skipped (portal participant had no person_id): {skipped_no_portal_person}")

    except Exception as e:
        conn.rollback()
        print("❌ Error occurred. Rolled back.")
        raise e


def main():
    load_dotenv()

    DB_PATH = Path(__file__).parent / "validation_dev.db"
    MATCH_FILE = Path("training_vs_portal_fuzzy_CVH_3_2_2026_14_ManuallyConfirmed.csv")  # adjust as needed

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")

    # (Optional) Indexes for performance (fine for TEXT columns too)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_participant_id ON participant(participant_id);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_participant_person_id ON participant(person_id);")

    print("🔎 Loading confirmed match file...")
    match_df = pd.read_csv(MATCH_FILE)

    required_cols = {
        "portal_participant_id",
        "training_participant_id",
        "confirmed_match"
    }

    if not required_cols.issubset(match_df.columns):
        missing = required_cols - set(match_df.columns)
        raise ValueError(f"Match file missing required columns: {missing}")

    # Clean up IDs from CSV (strip whitespace)
    for col in ["portal_participant_id", "training_participant_id"]:
        match_df[col] = match_df[col].astype(str).str.strip()

    confirmed_count = match_df["confirmed_match"].astype(str).str.strip().isin(["1", "true", "True"]).sum()
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
    print(f"Persons removed (orphans): {before_person_count - after_person_count}")

    conn.close()


if __name__ == "__main__":
    main()

# ############################# Mike's OG Code which moves the portal participant person_ID to the cc participant's person_ID##########################
# import sqlite3
# import pandas as pd
# from pathlib import Path
# from dotenv import load_dotenv
# import sqlite3
# import pandas as pd


# def apply_confirmed_matches(conn, match_df):
#     conn.execute("PRAGMA foreign_keys = ON;")
#     conn.execute("BEGIN;")

#     try:
#         confirmed = match_df[match_df["confirmed_match"] == 1]

#         for _, row in confirmed.iterrows():
#             conn.execute(
#                 """
#                 UPDATE participant
#                 SET person_id = ?
#                 WHERE participant_id = ?;
#                 """,
#                 (row["training_person_id"], row["portal_participant_id"])
#             )

#         # Prune orphaned person records
#         conn.execute("""
#             DELETE FROM person
#             WHERE person_id NOT IN (
#                 SELECT DISTINCT person_id FROM participant
#             );
#         """)

#         conn.commit()
#         print("✅ Confirmed matches applied successfully.")

#     except Exception as e:
#         conn.rollback()
#         print("❌ Error occurred. Rolled back.")
#         raise e


# def main():
    
#     load_dotenv()

#     DB_PATH = Path(__file__).parent / "validation_dev.db"
#     MATCH_FILE = Path("training_vs_portal_fuzzy_CVH_3_2_2026_13_ManuallyConfirmed.csv") #12 has been vlookup checked against the manual work I've already completed.

#     conn = sqlite3.connect(DB_PATH)
#     conn.execute("PRAGMA foreign_keys = ON;")

#     print("🔎 Loading confirmed match file...")
#     match_df = pd.read_csv(MATCH_FILE)

#     required_cols = {
#         "portal_participant_id", # Mike had "cc_participant_id" for CTHires # In my resolved matches file, this is training_participant_id
#         "training_person_id", # Mike had "train_person_id" for CC # In my resolved matches file, this is training_person_id
#         "confirmed_match"
#     }

#     if not required_cols.issubset(match_df.columns):
#         raise ValueError("Match file missing required columns.")

#     confirmed_count = (match_df["confirmed_match"] == 1).sum()
#     print(f"✅ {confirmed_count} confirmed matches found.")

#     # Pre-merge audit
#     before_person_count = pd.read_sql_query(
#         "SELECT COUNT(*) AS n FROM person;", conn
#     )["n"].iloc[0]

#     before_participant_count = pd.read_sql_query(
#         "SELECT COUNT(*) AS n FROM participant;", conn
#     )["n"].iloc[0]

#     print(f"Before merge: {before_person_count} persons, {before_participant_count} participants")

#     # Apply merge
#     apply_confirmed_matches(conn, match_df)

#     # Post-merge audit
#     after_person_count = pd.read_sql_query(
#         "SELECT COUNT(*) AS n FROM person;", conn
#     )["n"].iloc[0]

#     after_participant_count = pd.read_sql_query(
#         "SELECT COUNT(*) AS n FROM participant;", conn
#     )["n"].iloc[0]

#     print(f"After merge: {after_person_count} persons, {after_participant_count} participants")
#     print(f"Persons removed: {before_person_count - after_person_count}")

#     conn.close()

# if __name__ == "__main__":
#     main()
import sqlite3
import pandas as pd
from pathlib import Path
import os
from dotenv import load_dotenv
import sqlite3
import pandas as pd
from rapidfuzz import process, fuzz


def get_cc_demo_singletons(conn):
    """
    Get cc_demo_pull participants whose person_id has exactly one participant_id.
    """
    query = """
    SELECT 
        per.person_id,
        per.first_name,
        per.last_name,
        per.dob,
        per.zip,
        part.participant_id
    FROM participant part
    JOIN person per ON per.person_id = part.person_id
    WHERE part.dataset_name = 'cc_demo_pull'
      AND per.person_id IN (
          SELECT person_id
          FROM participant
          GROUP BY person_id
          HAVING COUNT(participant_id) = 1
      );
    """
    return pd.read_sql_query(query, conn)


def get_training_participants(conn):
    """
    Get training_data participants.
    """
    query = """
    SELECT 
        per.person_id,
        per.first_name,
        per.last_name,
        per.dob,
        per.zip,
        part.participant_id
    FROM participant part
    JOIN person per ON per.person_id = part.person_id
    WHERE part.dataset_name = 'training data';
    """
    return pd.read_sql_query(query, conn)


def normalize_name(x):
    if pd.isna(x):
        return ""
    return str(x).strip().casefold()


def build_match_key(df):
    return (
        df["first_name"].map(normalize_name) + "|" +
        df["last_name"].map(normalize_name) 
    )


def fuzzy_match(cc_df, train_df, min_score=90):
    cc_df = cc_df.copy()
    train_df = train_df.copy()

    cc_df["match_key"] = build_match_key(cc_df)
    train_df["match_key"] = build_match_key(train_df)

    training_keys = train_df["match_key"].tolist()

    matches = []

    for _, cc_row in cc_df.iterrows():
        key = cc_row["match_key"]

        if not key.strip("|"):
            continue

        result = process.extractOne(
            key,
            training_keys,
            scorer=fuzz.token_sort_ratio
        )

        if result and result[1] >= min_score:
            matched_key, score, _ = result

            train_row = train_df.loc[
                train_df["match_key"] == matched_key
            ].iloc[0]

            # Build combined row
            combined = {}

            # Add all cc fields
            for col in cc_df.columns:
                combined[f"cc_{col}"] = cc_row[col]

            # Add all training fields
            for col in train_df.columns:
                combined[f"train_{col}"] = train_row[col]

            combined["fuzzy_score"] = score

            matches.append(combined)

    return pd.DataFrame(matches)


def main():

    load_dotenv()

    DOCUMENTS = Path(os.environ["DOCUMENTS"])

    DB_PATH = Path(__file__).parent / "validation_dev.db"
    conn = sqlite3.connect(DB_PATH)

    cc_df = get_cc_demo_singletons(conn)
    train_df = get_training_participants(conn)

    match_df = fuzzy_match(cc_df, train_df, min_score=92)

    print(match_df.head())
    match_df.to_csv("cc_to_training_fuzzy_matches.csv", index=False)
    train_df.to_csv("cc_singletons.csv", index=False)

    conn.close()


if __name__ == "__main__":
    main()

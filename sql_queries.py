import sqlite3
import pandas as pd
from pathlib import Path



#### Participants with blank Race/Ethnicity in portal data
# sql = """
# SELECT COUNT(DISTINCT cvh.participant_id)
# FROM cell_value_history cvh
# JOIN dataset_column dc
#   ON dc.column_id = cvh.column_id
# WHERE dc.dataset_name = 'portal data';
#   --AND dc.column_name = 'Race/Ethnicity'
#   --AND (cvh.value_normalized IS NOT NULL OR NOT TRIM(cvh.value_normalized) = '');
# """






#### EXECUTING SQL QUERY ####

# Path to your SQLite database
DB_PATH = Path(__file__).resolve().parent / "validation_dev.db"

# Connect to the database
conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON;")


#### CC Participants with their Portal Participant ID
sql = """
SELECT *,
    pr.person_id,
    pr.first_name,
    pr.last_name,
    pr.dob,
    pr.zip,
    pr.gender,
    cc.participant_id            AS cc_participant_id,
    cc.org                       AS cc_org,
    portal.participant_id        AS portal_participant_id
FROM person AS pr
JOIN participant AS cc
  ON cc.person_id = pr.person_id
 AND cc.dataset_name = 'training data'
LEFT JOIN participant AS portal
  ON portal.person_id = pr.person_id
 AND portal.dataset_name = 'portal data'
"""



# Execute query and load into DataFrame
df = pd.read_sql_query(sql, conn)

# Print result
print(df)


# ✅ Export to CSV
output_path = Path(__file__).resolve().parent / "cc_people_with_portal_info13_1.csv"
df.to_csv(output_path, index=False)

cc_portal_participant_ids = df['portal_participant_id'].dropna().unique().tolist()

print(f"✅ Exported {len(df):,} rows to {output_path}")
print(f"🔎 Found {len(cc_portal_participant_ids)} unique portal participant IDs for CC participants")





# Step 1: get the column_id for 'Race'
column_id = pd.read_sql(
    "SELECT column_id FROM dataset_column WHERE column_name = 'Race';",
    conn
)


# Step 2: get all cell_value_history rows for those column_ids
race_df = pd.read_sql(
    f"""
    SELECT *
    FROM cell_value_history
    WHERE column_id = ?;
    """,
    conn,
    params=(column_id['column_id'].iloc[0],)
)

# Step 3: filter race_df to participant IDs
race_df = race_df[race_df['participant_id'].isin(cc_portal_participant_ids)]


# Ensure consistent dtype to avoid false mismatches
race_ids = pd.Series(race_df['participant_id']).dropna().astype('string').unique().tolist()
portal_ids = pd.Series(cc_portal_participant_ids, dtype='string').tolist()

# Compute unmatched
unmatched_ids = sorted(set(portal_ids) - set(race_ids))

# Save to CSV
pd.DataFrame({'participant_id': unmatched_ids}).to_csv('cc_portal_race_unmatched13_1.csv', index=False)


# 1) Get unique, non-null portal participant IDs from your existing df
portal_participant_ids = (
    df["portal_participant_id"]
    .dropna()
    .astype(str)  # ensure consistent type for SQLite TEXT
    .unique()
    .tolist()
)

print(f"🔎 Found {len(portal_participant_ids)} unique portal participant IDs to query")

# Early exit: nothing to query
if not portal_participant_ids:
    race_df = pd.DataFrame(
        columns=[
            "history_id", "run_id", "participant_id", "column_id",
            "value_raw", "value_normalized", "timestamp"
        ]
    )
else:
    # 2) Build the SQL with parameter placeholders
    base_sql = """
    SELECT
        cvh.history_id,
        cvh.run_id,
        cvh.participant_id,
        cvh.column_id,
        cvh.value_raw,
        cvh.value_normalized,
        cvh.timestamp,
        dc.column_name
    FROM cell_value_history AS cvh
    JOIN dataset_column AS dc
      ON dc.column_id = cvh.column_id
    -- WHERE dc.column_name = 'Race'
      WHERE cvh.participant_id IN ({placeholders})
    """

    # 3) SQLite has a default max of 999 bind parameters; chunk to be safe
    MAX_BIND_PARAMS = 999
    # Our query only binds the IN list, so chunk size = 999
    def chunk_list(lst, size):
        for i in range(0, len(lst), size):
            yield lst[i:i + size]

    # 4) Execute per-chunk and concat
    conn = sqlite3.connect(DB_PATH)
    try:
        frames = []
        for chunk in chunk_list(portal_participant_ids, MAX_BIND_PARAMS):
            placeholders = ",".join(["?"] * len(chunk))
            sql = base_sql.format(placeholders=placeholders)
            df_chunk = pd.read_sql_query(sql, conn, params=chunk)
            frames.append(df_chunk)

        print(f"Length of placeholders: {len(chunk)}")
        race_df = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    finally:
        conn.close()

# race_df now contains the Race cell value history for those portal participants
# ✅ Export to CSV
output_path_2 = Path(__file__).resolve().parent / "cc_portal_race13_1.csv"
race_df.to_csv(output_path_2, index=False)

print(f"✅ Exported {len(race_df):,} rows to {output_path_2}")


# Close connection
conn.close()
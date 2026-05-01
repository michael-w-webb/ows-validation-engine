import sqlite3
import pandas as pd
from config import DB_PATH

conn = sqlite3.connect(DB_PATH)

DATASET = "TPI"

# -----------------------------
# 1. Get last 5 completed runs
# -----------------------------
runs = pd.read_sql_query("""
    SELECT run_id, organization, quarter, run_timestamp
    FROM validation_run
    WHERE dataset_name = ?
      AND completed = 1
    ORDER BY run_timestamp DESC
    LIMIT 5
""", conn, params=[DATASET])

if runs.empty:
    print("No completed runs found.")
    exit()

print("\n=== LAST 5 RUNS ===")
print(runs)

# -----------------------------
# 2. Loop through runs
# -----------------------------
for _, row in runs.iterrows():
    run_id = row["run_id"]
    org = row["organization"]
    quarter = row["quarter"]

    print("\n" + "="*60)
    print(f"Run: {run_id}")
    print(f"Org: {org} | Quarter: {quarter}")

    # --- pull presence data ---
    presence = pd.read_sql_query("""
        SELECT participant_id, status
        FROM participant_presence_log
        WHERE run_id = ?
    """, conn, params=[run_id])

    if presence.empty:
        print("⚠️ No presence rows found (flush likely failed)")
        continue

    # -----------------------------
    # 3. Basic counts
    # -----------------------------
    total = len(presence)
    counts = presence["status"].value_counts()

    missing_count = counts.get("missing", 0)
    present_count = counts.get("present", 0)

    print(f"Total rows: {total}")
    print(f"Present: {present_count}")
    print(f"Missing: {missing_count}")

    # -----------------------------
    # 4. Check overwrite issue
    # -----------------------------
    # If a participant appears multiple times, check if missing got overwritten
    dupes = (
        presence.groupby("participant_id")["status"]
        .nunique()
        .reset_index()
    )

    overwritten = dupes[dupes["status"] > 1]

    print(f"Participants with multiple statuses (possible overwrite): {len(overwritten)}")

    # -----------------------------
    # 5. Sample missing IDs
    # -----------------------------
    if missing_count > 0:
        sample_missing = presence[
            presence["status"] == "missing"
        ]["participant_id"].head(5)

        print("Sample missing participant_ids:")
        print(sample_missing.tolist())
    else:
        print("⚠️ No missing participants recorded")

# -----------------------------
# 6. Cross-run persistence check
# -----------------------------
print("\n=== CROSS-RUN CHECK ===")

cross = pd.read_sql_query("""
    SELECT 
    ppl.participant_id, 
    COUNT(DISTINCT ppl.run_id) as run_count
FROM participant_presence_log ppl
JOIN validation_run vr
  ON ppl.run_id = vr.run_id
WHERE vr.dataset_name = ?
GROUP BY ppl.participant_id
HAVING run_count >= 3
LIMIT 10
""", conn, params=[DATASET])

print("Participants appearing across multiple runs:")
print(cross)
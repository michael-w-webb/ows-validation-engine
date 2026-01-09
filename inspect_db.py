import sqlite3
import pandas as pd
from pathlib import Path

pd.set_option("display.max_colwidth", None)
pd.set_option("display.width", 0)
pd.set_option("display.max_columns", None)

DB_PATH = Path(__file__).parent / "validation_dev.db"
conn = sqlite3.connect(DB_PATH)

print(f"\n🔍 Inspecting Validation DB: {DB_PATH}\n")


# ============================================================
# 1️⃣ Recent validation runs
# ============================================================
runs = pd.read_sql_query("""
    SELECT run_id, dataset_name, organization, quarter, 
           triggered_by, run_timestamp
    FROM validation_run
    ORDER BY run_timestamp DESC
    LIMIT 20
""", conn)

print("=== Recent validation runs ===")
print(runs, "\n")


# ============================================================
# 2️⃣ People table
# ============================================================
people = pd.read_sql_query("""
    SELECT person_id,
           first_name, last_name, dob, zip,
           id_key_strict_name_dob_zip,
           id_key_medium_name_dob,
           id_key_medium_name_zip,
           id_key_weak_name,
           created_timestamp, updated_timestamp
    FROM person
    ORDER BY created_timestamp DESC
    LIMIT 20
""", conn)

print("=== Person records (golden identities) ===")
print(people, "\n")


# ============================================================
# 3️⃣ Participant table
# ============================================================
participants = pd.read_sql_query("""
    SELECT participant_id,
           person_id,
           dataset_name,
           org, 
           created_timestamp
    FROM participant
    ORDER BY created_timestamp DESC
    LIMIT 20
""", conn)

print("=== Participant records (each upload row mapped to a person) ===")
print(participants, "\n")


# ============================================================
# 4️⃣ Participant presence per run
# ============================================================
presence = pd.read_sql_query("""
    SELECT run_id, participant_id, status, timestamp
    FROM participant_presence_log
    ORDER BY timestamp DESC
    LIMIT 20
""", conn)

print("=== Participant presence across runs ===")
print(presence, "\n")


# ============================================================
# 5️⃣ Logged cell values
# ============================================================
cell_history = pd.read_sql_query("""
    SELECT history_id,
           run_id,
           participant_id,
           column_id,
           value_raw,
           value_normalized,
           timestamp
    FROM cell_value_history
    ORDER BY timestamp DESC
    LIMIT 20
""", conn)

print("=== Cell value history (normalized sheet-by-sheet snapshots) ===")
print(cell_history, "\n")


# ============================================================
# 6️⃣ Dataset column registry
# ============================================================
columns = pd.read_sql_query("""
    SELECT column_id, dataset_name, sheet_name, column_name
    FROM dataset_column
    ORDER BY dataset_name, sheet_name, column_name
    LIMIT 30
""", conn)

print("=== Registered dataset columns ===")
print(columns, "\n")


# ============================================================
# 7️⃣ Validation violations (optional table)
# ============================================================
# Only show if the table exists
try:
    violations = pd.read_sql_query("""
        SELECT rule_id, normalized, raw_value, severity, timestamp
        FROM validation_violation
        ORDER BY timestamp DESC
        LIMIT 20
    """, conn)

    print("=== Validation violations (if logging enabled) ===")
    print(violations, "\n")

except Exception:
    print("=== Validation violations table not found ===\n")



error_count = pd.read_sql_query("""SELECT rule_id,
       COUNT(*) AS hits
FROM validation_violation
GROUP BY rule_id
ORDER BY hits DESC;""", conn)

print(error_count)

find_participant = pd.read_sql_query("""WITH latest_presence AS (
    SELECT
        ppl.*,
        ROW_NUMBER() OVER (
            PARTITION BY participant_id, quarter
            ORDER BY timestamp DESC
        ) AS rn
    FROM participant_presence_log ppl
)
SELECT
    p.participant_id,
    p.person_id,
    p.dataset_name,
    p.org,

    MAX(CASE WHEN lp.quarter = 'PY2_Q1' THEN lp.status END) AS "PY2 Q1",                                    
    MAX(CASE WHEN lp.quarter = 'PY2_Q2' THEN lp.status END) AS "PY2 Q2",
    MAX(CASE WHEN lp.quarter = 'PY2_Q3' THEN lp.status END) AS "PY2 Q3",                                    
    MAX(CASE WHEN lp.quarter = 'PY2_Q4' THEN lp.status END) AS "PY2 Q4",
    MAX(CASE WHEN lp.quarter = 'PY3_Q1' THEN lp.status END) AS "PY3 Q1",
    MAX(CASE WHEN lp.quarter = 'PY3_Q2' THEN lp.status END) AS "PY3 Q2",
    MAX(CASE WHEN lp.quarter = 'PY3_Q3' THEN lp.status END) AS "PY3 Q3",
    MAX(CASE WHEN lp.quarter = 'PY3_Q4' THEN lp.status END) AS "PY3 Q4",
    MAX(CASE WHEN lp.quarter = 'PY4_Q1' THEN lp.status END) AS "PY4 Q1"

FROM participant p
LEFT JOIN latest_presence lp
  ON p.participant_id = lp.participant_id
 AND lp.rn = 1

GROUP BY
    p.participant_id,
    p.person_id,
    p.dataset_name,
    p.org;

""", conn)

find_participant.to_csv(r"C:\Users\webbm\OneDrive - State of Connecticut\Documents\find_participant.csv", index=False)


find_value = pd.read_sql_query("""
WITH provider_by_quarter AS (
    SELECT
        cvh.participant_id,
        ppl.quarter,
        cvh.value_normalized AS value_of_interest,
        ROW_NUMBER() OVER (
            PARTITION BY cvh.participant_id, ppl.quarter
            ORDER BY cvh.timestamp DESC
        ) AS rn
    FROM cell_value_history cvh
    JOIN participant_presence_log ppl
      ON cvh.run_id = ppl.run_id
     AND cvh.participant_id = ppl.participant_id
    WHERE cvh.column_id = (
        SELECT column_id
        FROM dataset_column
        WHERE column_name = 'CareerConneCT Training Provider' -- column of interest
          AND dataset_name = 'training data' -- dataset of interest
          AND sheet_name = 'Training' -- sheet of interest
    )
)
SELECT
    p.participant_id,
    p.person_id,
    p.dataset_name,
    p.org,

    MAX(CASE WHEN pbq.quarter = 'PY2_Q1' THEN pbq.value_of_interest END) AS "PY2 Q1",                       
    MAX(CASE WHEN pbq.quarter = 'PY2_Q2' THEN pbq.value_of_interest END) AS "PY2 Q2",
    MAX(CASE WHEN pbq.quarter = 'PY2_Q3' THEN pbq.value_of_interest END) AS "PY2 Q3",
    MAX(CASE WHEN pbq.quarter = 'PY2_Q4' THEN pbq.value_of_interest END) AS "PY2 Q4",
    MAX(CASE WHEN pbq.quarter = 'PY3_Q1' THEN pbq.value_of_interest END) AS "PY3 Q1",
    MAX(CASE WHEN pbq.quarter = 'PY3_Q2' THEN pbq.value_of_interest END) AS "PY3 Q2",
    MAX(CASE WHEN pbq.quarter = 'PY3_Q3' THEN pbq.value_of_interest END) AS "PY3 Q3",
    MAX(CASE WHEN pbq.quarter = 'PY3_Q4' THEN pbq.value_of_interest END) AS "PY3 Q4",
    MAX(CASE WHEN pbq.quarter = 'PY4_Q1' THEN pbq.value_of_interest END) AS "PY4 Q1"

FROM participant p
LEFT JOIN provider_by_quarter pbq
  ON p.participant_id = pbq.participant_id
 AND pbq.rn = 1

GROUP BY
    p.participant_id,
    p.person_id,
    p.dataset_name,
    p.org

ORDER BY
    p.org,
    p.participant_id;
""", conn)


find_value.to_csv(r"C:\Users\webbm\OneDrive - State of Connecticut\Documents\find_value.csv", index=False)

multimember = pd.read_sql_query("""
    SELECT
    person_id,
    COUNT(DISTINCT dataset_name) AS dataset_count
FROM participant
GROUP BY person_id
HAVING COUNT(DISTINCT dataset_name) > 1
ORDER BY dataset_count DESC;
""", conn)
    
print("=== Participants in both Programs ===")
print(multimember, "\n")


presence_counts = pd.read_sql_query("""WITH first_present AS (
    SELECT
        participant_id,
        MIN(timestamp) AS first_present_ts
    FROM participant_presence_log
    WHERE status = 'present'
    GROUP BY participant_id
)
SELECT
    p.dataset_name,
    p.org,
    COUNT(DISTINCT p.participant_id) AS missing_count
FROM participant_presence_log l
JOIN first_present fp
  ON l.participant_id = fp.participant_id
JOIN participant p
  ON p.participant_id = l.participant_id
WHERE l.status = 'missing'
  AND l.timestamp > fp.first_present_ts
GROUP BY p.dataset_name, p.org
ORDER BY missing_count DESC;
""", conn)

print("=== Presence by org over time ===")
print(presence_counts, "\n")


case_counts_by_run = pd.read_sql_query("""SELECT
    l.run_id,
    vr.dataset_name,
    vr.quarter,
    vr.organization,
    vr.run_timestamp,
    COUNT(DISTINCT l.participant_id) AS participants_present
FROM participant_presence_log l
JOIN validation_run vr
  ON vr.run_id = l.run_id
WHERE l.status = 'present'
GROUP BY l.run_id, vr.dataset_name, vr.quarter, vr.run_timestamp
ORDER BY vr.run_timestamp;""", conn)

print("=== case counts by run ===")
print(case_counts_by_run[case_counts_by_run["organization"]=="Connecticut_State_Building_Trades_Training_Institute"], "\n")

case_counts_by_run.to_csv(r"C:\Users\webbm\OneDrive - State of Connecticut\Documents\case_counts_by_run.csv", index=False)

missing_and_present_by_run = pd.read_sql_query("""
SELECT
    vr.dataset_name,
    vr.quarter,
    vr.organization,
    SUM(CASE WHEN l.status = 'present' THEN 1 ELSE 0 END) AS present_count,
    SUM(CASE WHEN l.status = 'missing' THEN 1 ELSE 0 END) AS missing_count,
    COUNT(DISTINCT l.participant_id) AS total_participants
FROM participant_presence_log l
JOIN validation_run vr
  ON vr.run_id = l.run_id
GROUP BY
    l.run_id,
    vr.dataset_name,
    vr.organization,
    vr.quarter,
    vr.run_timestamp
ORDER BY vr.run_timestamp;
""", conn)

print("---- missing and present by quarter ---- ")
print(missing_and_present_by_run[missing_and_present_by_run["organization"]=="CWP_IT"], "\n")

latest_runs_by_org_dataset = pd.read_sql_query(
    """
    SELECT
        vr.run_id,
        vr.organization,
        vr.dataset_name,
        vr.quarter,
        vr.run_timestamp
    FROM validation_run vr
    JOIN (
        SELECT
            organization,
            dataset_name,
            MAX(run_timestamp) AS max_ts
        FROM validation_run
        GROUP BY organization, dataset_name
    ) latest
      ON vr.organization = latest.organization
     AND vr.dataset_name = latest.dataset_name
     AND vr.run_timestamp = latest.max_ts
    ORDER BY vr.organization, vr.dataset_name;
    """,
    conn
)

print("=== Latest runs by organization and dataset ===")
print(latest_runs_by_org_dataset["run_id"])

from rapidfuzz import process, fuzz

person_check = pd.read_sql_query("""SELECT
    p.person_id,
    p.participant_id,
    p.org,
    p.dataset_name
FROM participant p
WHERE p.person_id IN (
    SELECT person_id
    FROM participant
    GROUP BY person_id
    HAVING COUNT(*) > 1
)
ORDER BY
    p.person_id,
    p.participant_id;""", conn)

person_check.to_csv(r"C:\Users\webbm\OneDrive - State of Connecticut\Documents\person_check.csv", index=False)

def fuzzy_missing_vs_present_for_run(conn, run_id, org=None, dataset=None):
    df = pd.read_sql_query(
        """
        SELECT
            l.status,
            l.participant_id,
            per.person_id,
            LOWER(TRIM(per.first_name)) AS first_name,
            LOWER(TRIM(per.last_name)) AS last_name,
            per.dob,
            per.zip
        FROM participant_presence_log l
        JOIN participant p
          ON p.participant_id = l.participant_id
        JOIN person per
          ON per.person_id = p.person_id
        WHERE l.run_id = ?
        """,
        conn,
        params=(run_id,)
    )

    missing = df[df["status"] == "missing"].copy()
    present = df[df["status"] == "present"].copy()

    if missing.empty or present.empty:
        return pd.DataFrame()

    present = present.reset_index(drop=True)

    missing["name_key"] = (
        missing["first_name"].fillna("") + " " +
        missing["last_name"].fillna("")
    ).str.strip()

    present["name_key"] = (
        present["first_name"].fillna("") + " " +
        present["last_name"].fillna("")
    ).str.strip()

    matches = []

    for _, m in missing.iterrows():
        best = process.extractOne(
            m["name_key"],
            present["name_key"],
            scorer=fuzz.token_sort_ratio,
            score_cutoff=0
        )

        if best:
            match_name, score, idx = best
            p = present.iloc[idx]

            matches.append({
                "run_id": run_id,
                "organization": org,
                "dataset_name": dataset,
                "missing_participant_id": m["participant_id"],
                "present_participant_id": p["participant_id"],
                "missing_name": m["name_key"],
                "present_name": match_name,
                "score": score,
                "missing_dob": m["dob"],
                "present_dob": p["dob"],
                "missing_zip": m["zip"],
                "present_zip": p["zip"],
                "dob_match": m["dob"] == p["dob"] and pd.notna(m["dob"]),
                "zip_match": m["zip"] == p["zip"] and pd.notna(m["zip"]),
            })

    return pd.DataFrame(matches)

all_fuzzy_matches = []

for _, row in latest_runs_by_org_dataset.iterrows():
    run_id = row["run_id"]
    org = row.get("organization")
    dataset = row.get("dataset_name")

    result = fuzzy_missing_vs_present_for_run(
        conn,
        run_id=run_id,
        org=org,
        dataset=dataset
    )

    if not result.empty:
        all_fuzzy_matches.append(result)

if all_fuzzy_matches:
    fuzzy_matches_all = pd.concat(all_fuzzy_matches, ignore_index=True)
else:
    fuzzy_matches_all = pd.DataFrame()

ct_hires_ids = pd.read_sql_query("""WITH ranked_ct_hires AS (
    SELECT
        cvh.participant_id,
        cvh.value_normalized AS ct_hires_username,
        vr.run_id,
        vr.run_timestamp,
        ROW_NUMBER() OVER (
            PARTITION BY cvh.participant_id
            ORDER BY vr.run_timestamp DESC
        ) AS rn
    FROM cell_value_history cvh
    JOIN dataset_column dc
      ON dc.column_id = cvh.column_id
    JOIN validation_run vr
      ON vr.run_id = cvh.run_id
    WHERE dc.column_name = 'CT Hires Username'
)
SELECT
    participant_id,
    ct_hires_username,
    run_id,
    run_timestamp
FROM ranked_ct_hires
WHERE rn = 1;
""", conn)

### match missing participant CT Hires IDs
fuzzy_matches_all = fuzzy_matches_all.merge(
    ct_hires_ids.rename(columns={
        "participant_id":"missing_participant_id",
        "ct_hires_username":"missing_ct_hires_id"
        }), on = "missing_participant_id", how="left")

#### match present participant CT Hires IDs
fuzzy_matches_all = fuzzy_matches_all.merge(
    ct_hires_ids.rename(columns={
        "participant_id":"present_participant_id",
        "ct_hires_username":"present_ct_hires_id"
        }), on = "present_participant_id", how="left")

fuzzy_matches_all["ct_hires_id_match"] = (
    fuzzy_matches_all["missing_ct_hires_id"] ==
    fuzzy_matches_all["present_ct_hires_id"]
)

def ct_hires_status(row):
    m = row["missing_ct_hires_id"]
    p = row["present_ct_hires_id"]

    if pd.notna(m) and pd.notna(p):
        return "CT_HIRES_MATCH" if m == p else "CT_HIRES_CONFLICT"
    if pd.notna(m) or pd.notna(p):
        return "CT_HIRES_ONE_SIDED"
    return "CT_HIRES_MISSING_BOTH"


fuzzy_matches_all["ct_hires_status"] = fuzzy_matches_all.apply(
    ct_hires_status, axis=1
)

def reconciliation_category(row):
    score = row["score"]
    dob = row["dob_match"]
    zip_ = row["zip_match"]
    ct = row["ct_hires_status"]

    # 🟢 Category 1 — Strong Identity Signal
    if ct == "CT_HIRES_MATCH":
        return "STRONG_IDENTITY"
    if score >= 90 and dob and zip_:
        return "STRONG_IDENTITY"

    # 🟡 Category 2 — Moderate / Likely
    if score >= 85 and dob:
        return "LIKELY_MATCH"
    if score >= 85 and zip_:
        return "LIKELY_MATCH"
    if ct == "CT_HIRES_ONE_SIDED" and score >= 85 and dob:
        return "LIKELY_MATCH"

    # 🟠 Category 3 — Weak but Plausible
    if score >= 80:
        return "WEAK_PLAUSIBLE"
    if dob or zip_:
        return "WEAK_PLAUSIBLE"

    # 🔴 Category 4 — Very Weak / Informational
    return "NO_PLAUSIBLE_MATCH"

fuzzy_matches_all["reconciliation_category"] = fuzzy_matches_all.apply(
    reconciliation_category, axis=1
)

suppress_present = (
    (fuzzy_matches_all["reconciliation_category"] == "NO_PLAUSIBLE_MATCH") &
    (fuzzy_matches_all["score"] < 80) &
    (~fuzzy_matches_all["dob_match"]) &
    (~fuzzy_matches_all["zip_match"]) &
    (fuzzy_matches_all["ct_hires_status"] != "CT_HIRES_MATCH")
)

present_fields = [
    "present_participant_id",
    "present_name",
    "present_dob",
    "present_zip",
    "present_ct_hires_id",
    "ct_hires_status",
    "run_id",
    "run_timestamp_y",
    "ct_hires_id_match",
    "score",
    "run_id_y",
    "dob_match",
    "zip_match"
]

fuzzy_matches_all.loc[suppress_present, present_fields] = pd.NA

summary = (
    fuzzy_matches_all
    .groupby(["organization", "dataset_name"])
    .agg(
        matches=("missing_participant_id", "count"),
        strong_matches=("score", lambda s: (s >= 90).sum())
    )
)

print(summary)

pariticpant_count_by_run = pd.read_sql_query("""SELECT
    run_id,
    COUNT(*) AS row_count
FROM participant_presence_log
GROUP BY run_id;""", conn)

print(pariticpant_count_by_run.sort_values(by="row_count"))

strong_matches = fuzzy_matches_all

fuzzy_matches_all.to_excel(r"C:\Users\webbm\OneDrive - State of Connecticut\Documents\strong_matches_comparison.xlsx", index=False)

conn.close()

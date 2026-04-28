import pandas as pd
import sqlite3
from config import DB_PATH

value_change_rules = {
                    "CTHires Username or State ID #": {"type": "any"},
                    "City": {"type": "any"},
                    "Zip Code": {"type": "any"},
                    "Date of Birth": {"type": "date_change", "tolerance_days": 30},
                    "Training Start Date": {"type": "date_change", "tolerance_days": 30},
                    "Training End Date": {"type": "date_change", "tolerance_days": 30},
                    "Job Start Date": {"type": "date_change", "tolerance_days": 30},
                    "Employment Status": {"type": "forbidden_value_change",
                                        "initial_value_set":["employed in-field by an employer who doesn't partner with your training program",
                        "employed in-field by an employer who partners with your training program",
                        "employed out of field"],
                                        "current_value_set":["still seeking employment", "in job search assistance","not seeking employment in-field","could not contact","","<na>","nan",None]},
                    "Training Completion Status": {"type": "forbidden_value_change",
                                                "initial_value_set":["completed training on time","yes but not continuous"],
                                        "current_value_set":["did not complete training (please code exit reason)","","<na>","nan",None]},
                        }
    

def get_value_changes(conn, curr_id, prev_id):
    return pd.read_sql_query("""
    WITH current_run AS (
        SELECT 
            participant_id, 
            column_id,
            CASE
                WHEN value_normalized IS NULL THEN NULL
                WHEN LOWER(TRIM(value_normalized)) IN ('', 'nan', '<na>', '<nat>', 'none') THEN NULL
                ELSE TRIM(value_normalized)
            END AS val
        FROM cell_value_history
        WHERE run_id = :curr_id
    ),
    previous_run AS (
        SELECT 
            participant_id, 
            column_id,
            CASE
                WHEN value_normalized IS NULL THEN NULL
                WHEN LOWER(TRIM(value_normalized)) IN ('', 'nan', '<na>', '<nat>', 'none') THEN NULL
                ELSE TRIM(value_normalized)
            END AS val
        FROM cell_value_history
        WHERE run_id = :prev_id
    )
    SELECT 
        COALESCE(c.participant_id, p.participant_id) AS participant_id,
        COALESCE(c.column_id, p.column_id) AS column_id,
        dc.column_name,
        p.val AS old_value,
        c.val AS new_value
    FROM current_run c
    FULL OUTER JOIN previous_run p 
        ON c.participant_id = p.participant_id 
       AND c.column_id = p.column_id
    LEFT JOIN dataset_column dc
        ON dc.column_id = COALESCE(c.column_id, p.column_id)
    WHERE c.val IS NOT p.val;
    """, conn, params={"curr_id": curr_id, "prev_id": prev_id})

conn = sqlite3.connect(DB_PATH)

dataset_name = "TPI"

orgs = ["TWP"]

if orgs == None:

    df = pd.read_sql_query("""
    SELECT DISTINCT organization
    FROM validation_run
    WHERE dataset_name = ?
    AND completed = 1
    """, conn, params=[dataset_name])

    orgs = df["organization"]

all_dfs = []

for org in orgs:

    run_lookup = pd.read_sql_query("""
    SELECT run_id, quarter, run_timestamp
    FROM validation_run
    WHERE organization = ?
      AND dataset_name = ?
      AND completed = 1
    ORDER BY run_timestamp
    """, conn, params=[org, dataset_name])

    if run_lookup.empty:
        continue

    latest_runs = (
        run_lookup
        .sort_values("run_timestamp")
        .drop_duplicates("quarter", keep="last")
        .sort_values("run_timestamp")
        .reset_index(drop=True)
    )

    # build adjacent comparisons
    for i in range(1, len(latest_runs)):
        prev_row = latest_runs.iloc[i - 1]
        curr_row = latest_runs.iloc[i]

        df = get_value_changes(
            conn,
            curr_id=curr_row["run_id"],
            prev_id=prev_row["run_id"]
        )

        if df.empty:
            continue

        df["organization"] = org
        df["from_quarter"] = prev_row["quarter"]
        df["to_quarter"] = curr_row["quarter"]

        all_dfs.append(df)

final_df = pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame()

def quarter_key(q):
    py, qtr = q.split("_")
    year = int(py.replace("PY", ""))
    quarter = int(qtr.replace("Q", ""))
    return year * 10 + quarter

final_df["quarter_order"] = final_df["to_quarter"].apply(quarter_key)

latest_changes = (
    final_df
    .sort_values("quarter_order")
    .drop_duplicates(
        subset=["organization", "participant_id", "column_id"],
        keep="last"
    )
)

def evaluate_change(row, rules):
    col = row["column_name"]
    
    if col not in rules:
        return False

    rule = rules[col]
    old = row["old_value"]
    new = row["new_value"]

    # normalize null-ish values
    def clean(v):
        if pd.isna(v):
            return None
        v = str(v).strip().lower()
        if v in ["", "nan", "<na>", "<nat>", "none"]:
            return None
        return v

    old = clean(old)
    new = clean(new)

    # -----------------------
    # ANY change
    # -----------------------
    if rule["type"] == "any":
        return old != new

    # -----------------------
    # DATE change with tolerance
    # -----------------------
    if rule["type"] == "date_change":
        if old is None or new is None:
            return False

        try:
            old_dt = pd.to_datetime(old)
            new_dt = pd.to_datetime(new)
        except:
            return False

        diff = abs((new_dt - old_dt).days)
        return diff > rule["tolerance_days"]

    # -----------------------
    # Forbidden transitions
    # -----------------------
    if rule["type"] == "forbidden_value_change":
        return (
            old in [v.lower() if isinstance(v, str) else v for v in rule["initial_value_set"]]
            and new in [v.lower() if isinstance(v, str) else v for v in rule["current_value_set"]]
        )

    return False

latest_changes["flagged"] = latest_changes.apply(
    lambda row: evaluate_change(row, value_change_rules),
    axis=1
)

flagged_df = latest_changes[latest_changes["flagged"]].copy()

# Get only relevant keys
flagged_keys = flagged_df[
    ["organization", "participant_id", "column_id"]
].drop_duplicates()

# Filter full change history to just those keys
filtered_final_df = final_df.merge(
    flagged_keys,
    on=["organization", "participant_id", "column_id"],
    how="inner"
)

def clean_val(v):
    if pd.isna(v):
        return None
    v = str(v).strip().lower()
    if v in ["", "nan", "<na>", "<nat>", "none"]:
        return None
    return v

def build_history(group):
    history = []
    
    # first old_value
    first_old = clean_val(group.iloc[0]["old_value"])
    history.append(first_old)
    
    # then all new_values
    history.extend(group["new_value_clean"].tolist())
    
    return history

filtered_final_df["new_value_clean"] = filtered_final_df["new_value"].map(clean_val)

history_df = (
    filtered_final_df
    .sort_values(["organization", "participant_id", "column_id", "quarter_order"])
    .groupby(["organization", "participant_id", "column_id"])
    .apply(build_history)
    .reset_index(name="value_history")
)

def add_initial_blank(hist):
    if not hist:
        return hist
    if hist[0] is not None:
        return [None] + hist
    return hist

flagged_with_history = flagged_df.merge(
    history_df,
    on=["organization", "participant_id", "column_id"],
    how="left"
)

flagged_with_history.to_csv("flagged_value_changes.csv", index=False)
#############################################################################################

"""
================================================================================
SYNTHETIC NON‑PARTICIPANT‑LEVEL DATA GENERATOR (OPTIMIZED + IDEMPOTENT)
================================================================================
"""

import pandas as pd
import uuid
from pathlib import Path
from datetime import datetime, UTC
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

# =============================================================================
# CONFIGURATION
# =============================================================================

BASE_DIR = Path(
    r"C:\Users\DalyRob\OneDrive - State of Connecticut\Documents\GitHub Repos\ows-validation-engine\database\cc_db_parquet_output"
)

OUTPUT_DIR = BASE_DIR / "parquet_with_NonParticipantLevelData"

AGGREGATE_FILE = Path(
    r"C:\Users\DalyRob\State of Connecticut\OWS HQ - Documents\CareerConneCT\Data\Grantee Management (QPRs)\DataSummary_Non-Participant-Level_CCT.xlsx"
)

# =============================================================================
# UTILITIES
# =============================================================================

def generate_run_id():
    return f"NPLD_{datetime.now(UTC).strftime('%Y%m%d')}"

def load_parquet_tables(base_path):
    return {p.stem: pd.read_parquet(p) for p in base_path.glob("*.parquet")}

def ensure_output_folder(path: Path):
    path.mkdir(exist_ok=True)

def normalize_quarter(excel_quarter, known_quarters):
    v1 = excel_quarter
    v2 = excel_quarter.replace("_", " ")
    if v1 in known_quarters:
        return v1
    if v2 in known_quarters:
        return v2
    return excel_quarter

# =============================================================================
# CORE — FAST, IDEMPOTENT
# =============================================================================

def add_synthetic_npld(tables, agg_df, run_id):

    df_person = tables["person"]
    df_participant = tables["participant"]
    df_presence = tables["participant_presence_log"]
    df_cvh = tables["cell_value_history"]
    df_dataset_col = tables["dataset_column"]

    known_quarters = set(df_presence["quarter"].dropna().unique())

    presence_with_org = df_presence.merge(
        df_participant[["participant_id", "org"]],
        on="participant_id",
        how="left"
    )

    existing_npld = presence_with_org[
        presence_with_org["sheet_name"] == "NPLD"
    ]

    existing_pairs = set(
        zip(
            existing_npld["org"].fillna(""),
            existing_npld["quarter"].fillna("")
        )
    )

    print(f"Found {len(existing_pairs)} existing NPLD (org, quarter) pairs.")

    work_items = []
    for _, row in agg_df.iterrows():

        grant = str(row["Grant"])
        org = str(row["Org"])
        excel_quarter = row["Quarter"]
        quarter = normalize_quarter(excel_quarter, known_quarters)

        if (org, quarter) in existing_pairs:
            print(f"✔ Skipping existing period: {org} {quarter}")
            continue

        work_items.append({
            "grant": grant,
            "org": org,
            "quarter": quarter,
            "received": int(row["Received Training?"]),
            "completed": int(row["Training Completed?"]),
            "employment": int(row["Employment Status at exit"])
        })

    print(f"Will process {len(work_items)} new periods.")

    person_rows = []
    participant_rows = []
    presence_rows = []
    cvh_rows = []

    next_counter = 1

    # -------------------------------------------------------------
    # BUILD LOOKUP: column_name → column_id
    # -------------------------------------------------------------
    dataset_col_lookup = dict(
        zip(df_dataset_col["column_name"], df_dataset_col["column_id"])
    )

    # Expected NPLD column names
    npld_columns = [
        "Received Training?",
        "Training Completed?",
        "Employment Status at exit"
    ]

    # Verify all exist
    missing = [c for c in npld_columns if c not in dataset_col_lookup]
    if missing:
        raise ValueError(f"Missing expected NPLD columns in dataset_column: {missing}")

    # Pre-compute NPLD column_id set
    npld_col_ids = {dataset_col_lookup[c] for c in npld_columns}

    all_column_ids = set(df_dataset_col["column_id"].unique())

    # ------------------------------------------------------------------
    # GENERATE SYNTHETIC ROWS
    # ------------------------------------------------------------------
    for item in work_items:

        org = item["org"]
        grant = item["grant"]
        quarter = item["quarter"]
        received = item["received"]
        completed = item["completed"]
        employment_count = item["employment"]

        print(f"➕ Adding {received} synthetic rows for {org} {quarter} (Grant: {grant})...")

        for i in range(received):

            pid = f"NonParticipantLevelData{next_counter}"
            next_counter += 1

            # PERSON -----------------------------------------------------------
            person_rows.append({
                "person_id": pid,
                "first_name": "NonParticipantLevelData",
                "last_name": str(next_counter),
                "dob": "",
                "zip": "",
                "id_key_strict_name_dob_zip": "",
                "id_key_medium_name_dob": "",
                "id_key_medium_name_zip": "",
                "id_key_weak_name": "",
                "created_timestamp": datetime.now(UTC),
                "updated_timestamp": datetime.now(UTC)
            })

            # PARTICIPANT ------------------------------------------------------
            participant_rows.append({
                "participant_id": pid,
                "person_id": pid,
                "dataset_name": grant,
                "org": org,
                "created_timestamp": datetime.now(UTC)
            })

            # PRESENCE ---------------------------------------------------------
            presence_rows.append({
                "run_id": run_id,
                "participant_id": pid,
                "status": "present",
                "row_number": i + 1,
                "sheet_name": "NPLD",
                "quarter": quarter,
                "timestamp": datetime.now(UTC)
            })

            # TRAINING FLAGS ---------------------------------------------------
            cvh_payload = {
                "Received Training?": "Yes",
                "Training Completed?": "Yes" if i < completed else "No",
                "Employment Status at exit": "Employed" if i < employment_count else None
            }

            # CVH — REAL NPLD VALUES (Use existing column_ids)
            for col_name, value in cvh_payload.items():
                col_id = dataset_col_lookup[col_name]
                cvh_rows.append({
                    "history_id": str(uuid.uuid4()),
                    "run_id": run_id,
                    "participant_id": pid,
                    "column_id": col_id,
                    "value_raw": value,
                    "value_normalized": value,
                    "timestamp": datetime.now(UTC)
                })

            # CVH — BLANK VALUES FOR ALL OTHER COLUMNS -------------------------
            for col_id in all_column_ids:
                if col_id in npld_col_ids:
                    continue
                cvh_rows.append({
                    "history_id": str(uuid.uuid4()),
                    "run_id": run_id,
                    "participant_id": pid,
                    "column_id": col_id,
                    "value_raw": None,
                    "value_normalized": None,
                    "timestamp": datetime.now(UTC)
                })

    # ------------------------------------------------------------------
    # APPEND ALL RESULTS
    # ------------------------------------------------------------------
    if person_rows:
        df_person = pd.concat([df_person, pd.DataFrame(person_rows)], ignore_index=True)
    if participant_rows:
        df_participant = pd.concat([df_participant, pd.DataFrame(participant_rows)], ignore_index=True)
    if presence_rows:
        df_presence = pd.concat([df_presence, pd.DataFrame(presence_rows)], ignore_index=True)
    if cvh_rows:
        df_cvh = pd.concat([df_cvh, pd.DataFrame(cvh_rows)], ignore_index=True)

    tables["person"] = df_person
    tables["participant"] = df_participant
    tables["participant_presence_log"] = df_presence
    tables["cell_value_history"] = df_cvh
    tables["dataset_column"] = df_dataset_col

    return tables

# =============================================================================
# SAVE
# =============================================================================

def save_parquet_tables(tables, output_dir):
    for name, df in tables.items():
        df.to_parquet(output_dir / f"{name}.parquet", index=False)

# =============================================================================
# MAIN
# =============================================================================

def main():

    ensure_output_folder(OUTPUT_DIR)

    print("\nLoading parquet database...")
    tables = load_parquet_tables(BASE_DIR)

    print("Loading Excel aggregate file...")
    agg_df = pd.read_excel(AGGREGATE_FILE)

    run_id = generate_run_id()
    print(f"Run ID: {run_id}")

    print("Processing NPLD...")
    tables = add_synthetic_npld(tables, agg_df, run_id)

    print("Saving enriched parquet database...")
    save_parquet_tables(tables, OUTPUT_DIR)

    print("\n================================================================================")
    print("SUCCESS! Synthetic NPLD Parquet Database Generated.")
    print(f"Output: {OUTPUT_DIR}")
    print("================================================================================\n")


if __name__ == "__main__":
    main()
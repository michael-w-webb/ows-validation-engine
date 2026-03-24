import pandas as pd

from cc_workbook_definitions import workbook_definitions as td_defs
from ct_hires_west_ed_workbook_definitions import workbook_definitions as full_pull_defs
from cc_ss_workbook_definitions import workbook_definitions as ss_defs

from pathlib import Path
import sqlite3
from dotenv import load_dotenv
import hmac
import hashlib

import os

load_dotenv()  # loads .env file

PEPPER = os.environ.get("LINKING_ID_PEPPER")

DATASET_SALT = {
    "training data": "td_v1",
    "cc_supportive_services": "ss_v1",
    "cc_full_pull": "fp_v1"
}

PII_COLUMNS = {
    "training data": [
        "First Name",
        "Last Name",
        "CT Hires Username",
        "CT Hires State ID #",
        "Zip Code",
        "Client Date of Birth"
    ],
    "cc_supportive_services": [
        "First Name",
        "Last Name",
        "CT Hires Username",
        "Zip Code"
    ],
    "cc_full_pull": [
        "First Name",
        "Last Name",
        "Zip Code",
        "Client Date of Birth",
        "CTHIRES Username"
    ]
}

if not PEPPER:
    raise ValueError("LINKING_ID_PEPPER must be set")

def ensure_linking_first(df):
    if "linking_id" not in df.columns:
        return df

    return df[["linking_id"] + [c for c in df.columns if c != "linking_id"]]

def create_linking_id(df, dataset_name):

    pii_cols = PII_COLUMNS.get(dataset_name, [])
    available_cols = [c for c in pii_cols if c in df.columns]

    if not available_cols:
        df["linking_id"] = pd.NA
        return df

    def hash_row(row):
        values = [str(row[c]).strip().lower() for c in available_cols]
        raw = "|".join(values)

        digest = hmac.new(
            PEPPER.encode(),
            raw.encode(),
            hashlib.sha256
        ).hexdigest()

        return digest

    df["linking_id"] = df.apply(hash_row, axis=1)

    return df

def split_pii(df, dataset_name):

    pii_cols = PII_COLUMNS.get(dataset_name, [])
    pii_present = [c for c in pii_cols if c in df.columns]

    pii_df = df[["linking_id"] + pii_present].copy()
    non_pii_df = df.drop(columns=pii_present, errors="ignore").copy()

    return non_pii_df, pii_df

def get_latest_runs_per_org(conn, dataset_name):

    return pd.read_sql_query(
        """
        SELECT run_id, organization, quarter
        FROM (
            SELECT
                run_id,
                organization,
                quarter,
                ROW_NUMBER() OVER (
                    PARTITION BY organization
                    ORDER BY run_timestamp DESC
                ) AS rn
            FROM validation_run
            WHERE dataset_name = ?
        )
        WHERE rn = 1
        """,
        conn,
        params=[dataset_name]
    )

def get_canonical_columns(dataset_name):

    base_cols = [
        "participant_id",
        "organization",
        "quarter"
    ]

    if dataset_name == "training data":
        dataset_cols = list(
            td_defs["training data"]["simple format"]["Report"]["labels"].keys()
        )

    elif dataset_name == "cc_supportive_services":
        dataset_cols = list(
            ss_defs["cc_supportive_services"]["simple format"]["Aggregate Report"]["labels"].keys()
        )

    elif dataset_name == "cc_full_pull":
        dataset_cols = list(
            full_pull_defs["cc_full_pull"]["simple format"]["Report"]["labels"].keys()
        )

    else:
        raise ValueError(f"Unknown dataset: {dataset_name}")

    pii_cols = set(PII_COLUMNS.get(dataset_name, []))

    expanded_cols = []

    for col in dataset_cols:
        if col in pii_cols:
            expanded_cols.append(col)  # normalized only, no suffix
        else:
            expanded_cols.append(f"{col}_raw")
            expanded_cols.append(f"{col}_normalized")

    seen = set()
    ordered = []

    for col in base_cols + expanded_cols:
        if col not in seen:
            ordered.append(col)
            seen.add(col)

    return ordered

def enforce_canonical_order(df, canonical_cols):

    for col in canonical_cols:
        if col not in df.columns:
            df[col] = pd.NA

    return df[canonical_cols]

def build_dataset(conn, run_id, dataset_name):

    df = pd.read_sql_query(
        """
        SELECT
            cvh.participant_id,
            dc.column_name,
            cvh.value_raw,
            cvh.value_normalized,
            vr.organization,
            vr.quarter
        FROM cell_value_history cvh
        JOIN dataset_column dc
            ON cvh.column_id = dc.column_id
        JOIN validation_run vr
            ON vr.run_id = cvh.run_id
        WHERE cvh.run_id = ?
        AND vr.dataset_name = ?
        """,
        conn,
        params=[run_id, dataset_name]
    )

    if df.empty:
        return pd.DataFrame()

    index_cols = ["participant_id", "organization", "quarter"]

    pii_cols = set(PII_COLUMNS.get(dataset_name, []))

    # ------------------------
    # NORMALIZED (ALL columns)
    # ------------------------
    wide_norm = (
        df.pivot_table(
            index=index_cols,
            columns="column_name",
            values="value_normalized",
            aggfunc="last"
        )
        .rename(columns=lambda c: c if c in pii_cols else f"{c}_normalized")
    )

    # ------------------------
    # RAW (NON-PII only)
    # ------------------------
    df_non_pii = df[~df["column_name"].isin(pii_cols)]

    wide_raw = (
        df_non_pii.pivot_table(
            index=index_cols,
            columns="column_name",
            values="value_raw",
            aggfunc="last"
        )
        .add_suffix("_raw")
    )

    wide = pd.concat([wide_raw, wide_norm], axis=1).reset_index()

    if dataset_name not in ["training data", "cc_supportive_services"]:
        wide = wide.drop(columns=["organization", "quarter"], errors="ignore")

    return wide

def rebuild_datasets(conn):

    outputs = {}

    # ------------------------
    # Training Data
    # ------------------------
    training_runs = get_latest_runs_per_org(conn, "training data")

    frames = []

    for _, row in training_runs.iterrows():
        df = build_dataset(conn, row.run_id, "training data")
        if not df.empty:
            frames.append(df)

    if frames:
        df = pd.concat(frames, ignore_index=True)

        canonical_cols = get_canonical_columns("training data")

        df = enforce_canonical_order(df, canonical_cols)
        df = create_linking_id(df, "training data")

        non_pii, pii = split_pii(df, "training data")

        non_pii = ensure_linking_first(non_pii)
        pii = ensure_linking_first(pii)

        # Ensure linking_id is first column
        non_pii = non_pii[["linking_id"] + [c for c in non_pii.columns if c != "linking_id"]]
        pii = pii[["linking_id"] + [c for c in pii.columns if c != "linking_id"]]

        outputs["training_data"] = non_pii
        outputs["training_data_pii"] = pii

    # ------------------------
    # Supportive Services
    # ------------------------
    ss_runs = get_latest_runs_per_org(conn, "cc_supportive_services")

    frames = []

    for _, row in ss_runs.iterrows():
        df = build_dataset(conn, row.run_id, "cc_supportive_services")
        if not df.empty:
            frames.append(df)

    if frames:
        df = pd.concat(frames, ignore_index=True)

        canonical_cols = get_canonical_columns("cc_supportive_services")

        df = enforce_canonical_order(df, canonical_cols)
        df = create_linking_id(df, "cc_supportive_services")

        non_pii, pii = split_pii(df, "cc_supportive_services")

        non_pii = non_pii[["linking_id"] + [c for c in non_pii.columns if c != "linking_id"]]
        pii = pii[["linking_id"] + [c for c in pii.columns if c != "linking_id"]]

        outputs["supportive_services"] = non_pii
        outputs["supportive_services_pii"] = pii

    # ------------------------
    # Full Pull
    # ------------------------
    full_pull = pd.read_sql_query(
        """
        SELECT run_id
        FROM validation_run
        WHERE dataset_name = 'cc_full_pull'
        ORDER BY run_timestamp DESC
        LIMIT 1
        """,
        conn
    )

    if not full_pull.empty:

        df = build_dataset(
            conn,
            full_pull.iloc[0]["run_id"],
            "cc_full_pull"
        )

        if not df.empty:

            canonical_cols = get_canonical_columns("cc_full_pull")

            df = enforce_canonical_order(df, canonical_cols)
            df = create_linking_id(df, "cc_full_pull")

            non_pii, pii = split_pii(df, "cc_full_pull")

            non_pii = non_pii[["linking_id"] + [c for c in non_pii.columns if c != "linking_id"]]
            pii = pii[["linking_id"] + [c for c in pii.columns if c != "linking_id"]]

            outputs["full_pull"] = non_pii
            outputs["full_pull_pii"] = pii

    return outputs

def resolve_run_id(conn, run_id=None, grab_latest=False, organization=None, dataset_name=None):

    if run_id:
        return run_id

    if grab_latest:

        query = """
        SELECT run_id
        FROM validation_run
        WHERE 1=1
        """

        params = []

        if organization:
            query += " AND organization = ?"
            params.append(organization)

        if dataset_name:
            query += " AND dataset_name = ?"
            params.append(dataset_name)

        query += " ORDER BY run_timestamp DESC LIMIT 1"

        result = pd.read_sql_query(query, conn, params=params)

        if result.empty:
            raise ValueError(f"No runs found for dataset {dataset_name}")

        return result.iloc[0]["run_id"]

    raise ValueError("You must provide run_id or set grab_latest=True.")

### CT Hires West Ed Submission PII to separate

# "First Name": [
#       "FIRSTNAME"
#     ],
#     "Last Name": [
#       "LASTNAME"
#     ],
#     "Zip Code": [
#       "ZIPCODE"
#     ],
#     "Client Date of Birth": [
#       "DATEOFBIRTH"

### CC Supportive Services PII to separate 

    # "First Name": ["First Name"],

    # "Last Name": ["Last Name"],

    # "CT Hires Username": [
    #     "CT Hires Username",
    #     "CTH State ID",
    #     "CTHires_Username"
    # ],

    # "Zip Code": ["Zip Code", "ZIP"],

#### CC workbook defintions PII 

#  "First Name": [
#       "First Name"
#     ],
#     "Last Name": [
#       "Last Name"
#     ],
#     "CT Hires Username": [
#       "CT Hires Username",
#       "CTHires User Name"
#     ],
#     "CT Hires State ID #": [
#       "State ID #"
#     ],
    # "Zip Code": [
    #   "Zip Code"
    # ],
    # "Client Date of Birth": [
    #   "Client Date of Birth",
    #   "DOB"
    # ],



DB_PATH = Path("validation_dev.db")

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON;")

outputs = rebuild_datasets(conn)

output_dir = Path(r"C:\Users\webbm\OneDrive - State of Connecticut\Documents\outputs")
output_dir.mkdir(exist_ok=True)

for name, df in outputs.items():
    file_path = output_dir / f"{name}.xlsx"
    df.to_excel(file_path, index=False)

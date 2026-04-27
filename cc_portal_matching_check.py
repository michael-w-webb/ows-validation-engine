import sqlite3
import pandas as pd
from pathlib import Path

# Prefer rapidfuzz; fall back to fuzzywuzzy if not available
try:
    from rapidfuzz import process, fuzz
    RF_AVAILABLE = True
except ImportError:
    from fuzzywuzzy import process, fuzz
    RF_AVAILABLE = False

# ----------------------------
# CONFIG
# ----------------------------
DB_PATH = Path(__file__).resolve().parent / "validation_dev.db"
DATASET_A = "training data"  # source dataset name
DATASET_B = "portal data"    # target dataset name

# Default expected column names (case-insensitive)
DEFAULT_COL_NAMES = {
    "first_name": ["First Name"],
    "last_name": ["Last Name"],
    "dob": ["dob", "Client Date of Birth"],
    "zip": ["zip", "postal code", "zipcode", "Zip Code"],
}


# ----------------------------
# Utilities
# ----------------------------
def _lower_list(values):
    return [v.lower() for v in values]

def _fetch_dataset_fields_from_cvh(
    conn: sqlite3.Connection,
    dataset_name: str,
    column_names: dict = None,
) -> pd.DataFrame:
    """
    Get the latest (per participant & column) dataset-level values for
    First Name, Last Name, DOB, ZIP from cell_value_history, scoped to a given dataset.

    Returns columns:
    - participant_id, person_id, org, dataset_name
    - first_name, last_name, dob, zip
    - last_update_timestamp (max run_timestamp among the captured fields for that participant)
    """
    column_names = column_names or DEFAULT_COL_NAMES

    # Prepare a flat list of all target column names (lowercased)
    first_names = _lower_list(column_names.get("first_name", ["first name"]))
    last_names  = _lower_list(column_names.get("last_name",  ["last name"]))
    dobs        = _lower_list(column_names.get("dob",        ["dob"]))
    zips        = _lower_list(column_names.get("zip",        ["zip"]))

    targets = list(set(first_names + last_names + dobs + zips))
    placeholders = ",".join(["?"] * len(targets))

    # We will select the latest value per participant & column_name (lowercased) using ROW_NUMBER
    # Then pivot those into columns.
    df = pd.read_sql_query(
        f"""
        WITH ranked AS (
            SELECT
                p.participant_id,
                p.person_id,
                p.org,
                p.dataset_name,
                LOWER(dc.column_name) AS column_name_lower,
                cvh.value_normalized AS value_norm,
                vr.run_timestamp,
                ROW_NUMBER() OVER (
                    PARTITION BY p.participant_id, LOWER(dc.column_name)
                    ORDER BY vr.run_timestamp DESC
                ) AS rn
            FROM participant p
            JOIN dataset_column dc
              ON dc.dataset_name = p.dataset_name
            JOIN cell_value_history cvh
              ON cvh.column_id = dc.column_id
             AND cvh.participant_id = p.participant_id
            JOIN validation_run vr
              ON vr.run_id = cvh.run_id
            WHERE p.dataset_name = ?
              AND LOWER(dc.column_name) IN ({placeholders})
        )
        SELECT
            participant_id,
            person_id,
            org,
            dataset_name,
            MAX(CASE WHEN column_name_lower IN ({",".join(["?"]*len(first_names))}) THEN value_norm END) AS first_name,
            MAX(CASE WHEN column_name_lower IN ({",".join(["?"]*len(last_names))})  THEN value_norm END) AS last_name,
            MAX(CASE WHEN column_name_lower IN ({",".join(["?"]*len(dobs))})       THEN value_norm END) AS dob,
            MAX(CASE WHEN column_name_lower IN ({",".join(["?"]*len(zips))})       THEN value_norm END) AS zip,
            MAX(run_timestamp) AS last_update_timestamp
        FROM ranked
        WHERE rn = 1
        GROUP BY participant_id, person_id, org, dataset_name
        """,
        conn,
        params=([dataset_name] + targets + first_names + last_names + dobs + zips)
    )

    # Build name_key: use normalized values if present, then lower/strip
    df["first_name"] = df["first_name"].astype(str).str.lower().str.strip().replace({"nan": ""})
    df["last_name"]  = df["last_name"].astype(str).str.lower().str.strip().replace({"nan": ""})
    df["name_key"]   = (df["first_name"].fillna("") + " " + df["last_name"].fillna("")).str.strip()

    return df


def _reconciliation_category(m: pd.Series) -> str:
    """
    Categorization WITHOUT CT Hires:
    - STRONG: score >= 90 AND dob_match AND zip_match
    - LIKELY: score >= 85 AND (dob_match OR zip_match)
    - WEAK_PLAUSIBLE: score >= 80 OR (dob_match OR zip_match)
    - NO_PLAUSIBLE_MATCH: otherwise
    """
    score = m["score"]
    dob = m["dob_match"]
    zip_ = m["zip_match"]

    # 🟢 Strong identity
    if score >= 90 and dob and zip_:
        return "STRONG_IDENTITY"

    # 🟡 Likely match
    if score >= 85 and (dob or zip_):
        return "LIKELY_MATCH"

    # 🟠 Weak but plausible
    if score >= 80:
        return "WEAK_PLAUSIBLE"
    if dob or zip_:
        return "WEAK_PLAUSIBLE"

    # 🔴 Very weak / informational
    return "NO_PLAUSIBLE_MATCH"


def fuzzy_match_between_datasets(
    conn: sqlite3.Connection,
    dataset_a: str = DATASET_A,
    dataset_b: str = DATASET_B,
    scorer=fuzz.token_sort_ratio,
    score_cutoff: int = 0,
    require_mutual_best: bool = False,
    dedupe_portal_matches: bool = True,
    column_names: dict = None,
) -> pd.DataFrame:
    """
    Fuzzy-match participants from dataset_a (training) to dataset_b (portal),
    using dataset-level field values sourced from cell_value_history.

    Parameters:
    - require_mutual_best: only keep pairs where A's best is B and B's best is A
    - dedupe_portal_matches: avoid pairing the same portal participant to multiple training participants
    - column_names: optional dict to override DEFAULT_COL_NAMES per dataset label
      keys: 'first_name', 'last_name', 'dob', 'zip' -> lists of acceptable column names (case-insensitive)

    Returns: DataFrame of matches with signals & categorization.
    """
    # 1) Pull dataset-scoped values from CVH
    training = _fetch_dataset_fields_from_cvh(conn, dataset_a, column_names)
    portal   = _fetch_dataset_fields_from_cvh(conn, dataset_b, column_names)

    if training.empty or portal.empty:
        return pd.DataFrame()

    training = training.reset_index(drop=True)
    portal = portal.reset_index(drop=True)

    # 2) Build portal search space for process.extractOne
    portal_name_list = portal["name_key"].tolist()

    # 3) Perform fuzzy matching
    matches = []
    used_portal_indices = set()

    for a_idx, a in training.iterrows():
        # Skip rows with no useful name
        if not a["name_key"]:
            continue

        best = process.extractOne(
            a["name_key"],
            portal_name_list,
            scorer=scorer,
            score_cutoff=score_cutoff
        )
        if not best:
            continue

        match_name, score, p_idx = best

        # Optionally dedupe — skip if already paired to another training record
        if dedupe_portal_matches and p_idx in used_portal_indices:
            continue

        b = portal.iloc[p_idx]

        # Validate mutual best if requested
        mutual_best = False
        if require_mutual_best:
            back_best = process.extractOne(
                b["name_key"],
                training["name_key"].tolist(),
                scorer=scorer,
                score_cutoff=score_cutoff
            )
            if back_best:
                _, _, back_a_idx = back_best
                mutual_best = (back_a_idx == a_idx)
                if not mutual_best:
                    # Skip non-mutual matches
                    continue

        # Track used portal index if deduping
        if dedupe_portal_matches:
            used_portal_indices.add(p_idx)

        # Signals (DOB/ZIP) — only count as match if both present AND equal
        dob_match = (a["dob"] == b["dob"]) and pd.notna(a["dob"]) and pd.notna(b["dob"])
        zip_match = (a["zip"] == b["zip"]) and pd.notna(a["zip"]) and pd.notna(b["zip"])

        matches.append({
            # Dataset metadata
            "dataset_a": dataset_a,
            "dataset_b": dataset_b,

            # IDs & Org
            "training_participant_id": a["participant_id"],
            "portal_participant_id": b["participant_id"],
            "training_person_id": a["person_id"],
            "portal_person_id": b["person_id"],
            "training_org": a["org"],
            "portal_org": b["org"],

            # Names
            "training_name": a["name_key"],
            "portal_name": match_name,
            "score": score,

            # Core signals (dataset-level)
            "training_first_name": a["first_name"],
            "training_last_name": a["last_name"],
            "training_dob": a["dob"],
            "training_zip": a["zip"],
            "portal_first_name": b["first_name"],
            "portal_last_name": b["last_name"],
            "portal_dob": b["dob"],
            "portal_zip": b["zip"],
            "dob_match": dob_match,
            "zip_match": zip_match,

            # Timestamps (latest seen among target fields in each dataset)
            "training_last_update": a["last_update_timestamp"],
            "portal_last_update": b["last_update_timestamp"],

            # Mutual best & positions
            "mutual_best": mutual_best,
            "training_index": a_idx,
            "portal_index": p_idx,
        })

    result = pd.DataFrame(matches)
    if result.empty:
        return result

    # 4) Reconciliation category (no CT)
    result["reconciliation_category"] = result.apply(_reconciliation_category, axis=1)

    # 5) Optional suppression of portal-side fields for very weak matches
    suppress_portal = (
        (result["reconciliation_category"] == "NO_PLAUSIBLE_MATCH") &
        (result["score"] < 80) &
        (~result["dob_match"]) &
        (~result["zip_match"])
    )

    portal_fields_to_suppress = [
        "portal_participant_id",
        "portal_name",
        "portal_first_name",
        "portal_last_name",
        "portal_dob",
        "portal_zip",
        "portal_org",
        "portal_last_update",
    ]

    result.loc[suppress_portal, portal_fields_to_suppress] = pd.NA

    return result


def summarize_matches(df: pd.DataFrame) -> pd.DataFrame:
    """
    High-level summary by org and category.
    """
    if df.empty:
        return pd.DataFrame()

    summary = (
        df.groupby(["training_org", "portal_org"])
          .agg(
              total_matches=("training_participant_id", "count"),
              strong_identity=("reconciliation_category", lambda s: (s == "STRONG_IDENTITY").sum()),
              likely_match=("reconciliation_category", lambda s: (s == "LIKELY_MATCH").sum()),
              weak_plausible=("reconciliation_category", lambda s: (s == "WEAK_PLAUSIBLE").sum()),
              no_plausible=("reconciliation_category", lambda s: (s == "NO_PLAUSIBLE_MATCH").sum()),
          )
          .reset_index()
    )
    return summary


if __name__ == "__main__":
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")

    # Run the cross-dataset fuzzy match (dataset-level fields via CVH)
    cross_matches = fuzzy_match_between_datasets(
        conn,
        dataset_a=DATASET_A,
        dataset_b=DATASET_B,
        scorer=fuzz.token_sort_ratio,
        score_cutoff=0,
        require_mutual_best=False,   # set True to only keep mutual-best pairs
        dedupe_portal_matches=True,  # avoid pairing a portal record to multiple training records
        column_names=DEFAULT_COL_NAMES
    )

    print("✅ Cross-dataset matches built:", len(cross_matches))
    if RF_AVAILABLE:
        print("Using rapidfuzz for matching.")
    else:
        print("Using fuzzywuzzy for matching. (Install 'rapidfuzz' for better performance.)")

    # Summary
    summary_df = summarize_matches(cross_matches)
    print("\n=== Summary by Org ===")
    print(summary_df)

    # Save full results
    out_path = Path(r"C:\Users\DalyRob\State of Connecticut\OWS PII Storage - Documents\Datasets for Validation\Portal\training_vs_portal_fuzzy_CVH_3_2_2026_15.xlsx")
    try:
        cross_matches.to_excel(out_path, index=False)
        print(f"\n📄 Saved full match output to: {out_path}")
    except Exception as e:
        print(f"⚠️ Could not save Excel: {e}")


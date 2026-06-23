import json
import sqlite3
import hashlib
from pathlib import Path

import pandas as pd

from applications.run_validation_for_file import run_validation_for_file

from applications.career_connect_grantee_sheets.workbook_definitions import (
    workbook_definitions,
)

from applications.career_connect_grantee_sheets.cross_rule_sets import (
    CONNECTED_PRESENCE_RULES,
    CONDITIONALLY_BLANK_UNLESS_RULES,
    CONDITIONALLY_ALLOWED_RULES,
    CONDITIONALLY_REQUIRED_RULES,
    CONDITIONALLY_REQUIRED_BY_DATE_COMPARISON_RULES,
)

from config import TEST_FILE


EXPECTED_DIR = Path("tests/expected")


cross_rules = [
    ("Connected Presence", CONNECTED_PRESENCE_RULES),
    ("Conditionally Blank", CONDITIONALLY_BLANK_UNLESS_RULES),
    ("Conditionally Allowed", CONDITIONALLY_ALLOWED_RULES),
    ("Conditionally Required", CONDITIONALLY_REQUIRED_RULES),
    ("Conditionally Required by Date", CONDITIONALLY_REQUIRED_BY_DATE_COMPARISON_RULES),
]


def fingerprint(series):

    values = (
        series
        .astype(object)
        .where(series.notna(), "")
        .astype(str)
    )

    return hashlib.sha256(
        values.to_csv(index=False).encode()
    ).hexdigest()


def test_end_to_end_validation(test_db):

    # --------------------------------------------------
    # Run Validation
    # --------------------------------------------------

    engine = run_validation_for_file(
        file_path=TEST_FILE,
        workbook_format="four sheet format",
        file_type="training data",
        workbook_definitions=workbook_definitions,
        cross_rules=cross_rules,
        db_path=test_db,
    )

    # --------------------------------------------------
    # Database Counts
    # --------------------------------------------------

    conn = sqlite3.connect(test_db)

    person_count = conn.execute(
        "SELECT COUNT(*) FROM person"
    ).fetchone()[0]

    participant_count = conn.execute(
        "SELECT COUNT(*) FROM participant"
    ).fetchone()[0]

    cvh_count = conn.execute(
        "SELECT COUNT(*) FROM cell_value_history"
    ).fetchone()[0]

    conn.close()

    # --------------------------------------------------
    # Mismatch Summary
    # --------------------------------------------------

    mismatches = pd.DataFrame(engine.mismatches)

    summary = (
        mismatches
        .groupby(
            ["sheet", "issue"]
        )
        .size()
        .reset_index(name="count")
        .sort_values(
            ["sheet", "issue"]
        )
        .reset_index(drop=True)
    )

    # --------------------------------------------------
    # Error Summary
    # --------------------------------------------------

    errors = pd.DataFrame(engine.get_all_errors())

    error_summary = (
        errors
        .groupby(
            ["sheet", "severity"]
        )
        .size()
        .reset_index(name="count")
        .sort_values(
            ["sheet", "severity"]
        )
        .reset_index(drop=True)
    )

    # --------------------------------------------------
    # Returnable Data
    # --------------------------------------------------

    df = engine.returnable_data

    actual_hashes = {
        col: fingerprint(df[col])
        for col in df.columns
    }

    # --------------------------------------------------
    # Expected Outputs
    # --------------------------------------------------

    with open(
        EXPECTED_DIR / "metadata.json",
        "r"
    ) as f:

        expected_metadata = json.load(f)

    expected_mismatch_summary = pd.read_csv(
        EXPECTED_DIR / "mismatch_summary.csv"
    )

    expected_error_summary = pd.read_csv(
        EXPECTED_DIR / "error_summary.csv"
    )

    with open(
        EXPECTED_DIR / "returnable_column_hashes.json",
        "r"
    ) as f:

        expected_hashes = json.load(f)

    # --------------------------------------------------
    # Metadata Assertions
    # --------------------------------------------------

    assert person_count == expected_metadata["person_count"]

    assert participant_count == expected_metadata[
        "participant_count"
    ]

    assert cvh_count == expected_metadata[
        "cvh_count"
    ]

    assert len(errors) == expected_metadata[
        "error_count"
    ]

    assert list(df.shape) == expected_metadata[
        "returnable_shape"
    ]

    # --------------------------------------------------
    # Summary Assertions
    # --------------------------------------------------

    pd.testing.assert_frame_equal(
        summary,
        expected_mismatch_summary,
        check_dtype=False,
    )

    pd.testing.assert_frame_equal(
        error_summary,
        expected_error_summary,
        check_dtype=False,
    )

    # --------------------------------------------------
    # Column Hash Assertions
    # --------------------------------------------------

    assert set(actual_hashes.keys()) == set(
        expected_hashes.keys()
    )

    mismatched_columns = []

    for column, expected_hash in expected_hashes.items():

        actual_hash = actual_hashes[column]

        if actual_hash != expected_hash:

            mismatched_columns.append(column)

    assert not mismatched_columns, (
        "Column hash mismatches:\n"
        + "\n".join(mismatched_columns)
    )
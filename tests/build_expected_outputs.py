# tests/build_expected_outputs.py

import json
import sqlite3
import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
from tests.init_test_db import init_db


import pandas as pd

from applications.run_validation_for_file import run_validation_for_file
from applications.career_connect_grantee_sheets.workbook_definitions import workbook_definitions
from applications.career_connect_grantee_sheets.cross_rule_sets import (
    CONNECTED_PRESENCE_RULES,
    CONDITIONALLY_BLANK_UNLESS_RULES,
    CONDITIONALLY_ALLOWED_RULES,
    CONDITIONALLY_REQUIRED_RULES,
    CONDITIONALLY_REQUIRED_BY_DATE_COMPARISON_RULES,
)

from config import TEST_FILE, TEST_DB_PATH


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


def build_expected():

    with TemporaryDirectory() as temp_dir:

        db_path = Path(temp_dir) / "expected_build.db"

        init_db(db_path)

        engine = run_validation_for_file(
            file_path=TEST_FILE,
            workbook_format="four sheet format",
            file_type="training data",
            workbook_definitions=workbook_definitions,
            cross_rules=cross_rules,
            db_path=db_path,
        )

        conn = sqlite3.connect(db_path)

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

        mismatches = pd.DataFrame(engine.mismatches)

        mismatch_summary = (
            mismatches
            .groupby(["sheet", "issue"])
            .size()
            .reset_index(name="count")
            .sort_values(["sheet", "issue"])
            .reset_index(drop=True)
        )

        errors = pd.DataFrame(engine.get_all_errors())

        error_summary = (
            errors
            .groupby(["sheet", "severity"])
            .size()
            .reset_index(name="count")
            .sort_values(["sheet", "severity"])
            .reset_index(drop=True)
        )

        df = engine.returnable_data

        column_hashes = {
            col: fingerprint(df[col])
            for col in df.columns
        }

        metadata = {
            "person_count": person_count,
            "participant_count": participant_count,
            "cvh_count": cvh_count,
            "error_count": len(errors),
            "returnable_shape": list(df.shape),
        }

        mismatch_summary.to_csv(
            EXPECTED_DIR / "mismatch_summary.csv",
            index=False,
        )

        error_summary.to_csv(
            EXPECTED_DIR / "error_summary.csv",
            index=False,
        )

        with open(
            EXPECTED_DIR / "metadata.json",
            "w"
        ) as f:
            json.dump(metadata, f, indent=4)

        with open(
            EXPECTED_DIR / "returnable_column_hashes.json",
            "w"
        ) as f:
            json.dump(column_hashes, f, indent=4)

        print("Expected outputs updated.")

        


if __name__ == "__main__":
    build_expected()
#!/usr/bin/env python3
"""
Aggregate long-form SQLite data into wide tables for Power BI visuals,
grouping by high-level (HL) variables and pivoting low-level (LL) variables.

- Counts distinct linking_id (privacy-preserving).
- Performs heavy work in SQL.
- Outputs CSV files: one per (HL, LL) pair.

Usage:
  python aggregate_pbi.py \
    --db validation_dev.db \
    --run-id <RUN_ID> \
    --output-dir ./agg_output_run_<RUN_ID> \
    --hl gender age race \
    --suppression-threshold 5 \
    --age-bands 16-24 25-34 35-44 45-54 55+ \
    --as-of run_timestamp

Author: M365 Copilot
"""

import argparse
import csv
import os
import sqlite3
import sys
from datetime import datetime
from typing import Dict, List, Tuple, Set, Optional, Any


# ------------------------------------------------------------------------------
# Canonical label maps (from your schema). Org-specific maps are intentionally ignored.
# We only need the "simple_format_pa25_119_data_labels" for header normalization.
# ------------------------------------------------------------------------------
simple_format_pa25_119_data_labels = {
  "First Name": [
      "First Name"
    ],
    "Last Name": [
      "Last Name"
    ],
  'town_person': [
    'city',
    'City',
    'Town/Region',
    'Town at Intake',
    '102 County Code',
    'Town of Residence',
    'City, State County',
    '102 County Code of Residence'
  ],
  'gender': [
    'gender',
    'Gender',
    'Gender Identity - Self-Identify',
    'Gender ',
    '201 Sex (WIOA)'
  ],
  'disability': [
    'Disability',
    '203 Category of Disability',
    'Do you have a disability?',
    'Are you an ADS(Aging Disability Services) participant?',
    'Youth with a disability and / or special needs',
    '202 Individual with a Disability (WIOA)'
  ],
  'tanf': [
    'Receipt of TANF'
  ],
  'ssi/ssdi': [
    'Do you currently receive, or have you received in the past six months: Supplemental Security Income',
    'Do you currently receive, or have you received in the past six months, any of the following: Supplemental Security Income',
    'Do you currently receive, or have you received in the past six months: Social Security Disability Income',
    'Do you currently receive, or have you received in the past six months, any of the following: Social Security Disability Income'
  ],
  'snap': [
    'Receipt of SNAP'
  ],
  'foster_care': [
    'Foster Care/Ward of State'
  ],
  'date_entered_training_1': [
    'Start Date',
    'Date Entered Training 1',
    '1302 Date Entered Training 1',
    'Training Start Date',
    'Date Entered Training ',
    'Start Dt',
    '1302 Date Entered Training #1 (WIOA)'
  ],
  'employment_status_at_exit': [
    'Employment Status at Exit',
    'Employment Status',
    'Employment Status at Placement End',
    'Completed-Employed',
    'Completed-Enrolled in PSEd or Adv Trng or Mil',
  ],
  'naics': [
    'Industry '
  ],
  'hourly_wage_at_exit': [
    'Hourly Wage at Exit',
    'Hourly Earnings',
    'Hourly Wage'
  ],
  'state': [
    '101 State Code of Residence (WIOA)',
    'State',
    'state'
  ],
  'town': [
    '102 County Code of Residence'
  ],
  'zip_code': [
    'Zip Code at Intake',
    'Zip Code',
    '103 Zip Code of Residence',
    'zip'
  ],
  'received_training': [
    'Received Training',
    '1300 Received Training',
    '1300 Received Training (WIOA)'
  ],
  'type_training_1': [
    'Type of Training Service 1',
    '1303 Type of Training Service 1',
    '1303 Type of Training Service #1 (WIOA)',
    'Type of Training '
  ],
  'cip_training_1': [
    'Career ConneCT Training Provider CIP Code',
    'Training CIP Code',
    '1305 Eligible Training Provider - CIP Code\n(WIOA)'
  ],
  'onet_training_1': [
    'Occupational Skills Training Code 1',
    '1306 Occupational Skills Training Code 1',
    'O*NET Code',
    'O*NET-SOC Code (XX-XXXX.XX)',
    '1306 Occupational Skills Training Code #1'
  ],
  'training_completed_1': [
    'Training Completed 1',
    '1307 Training Completed 1',
    'Training Completion Status',
    'Completion Status',
    '1307 Training Completed #1',
    'Training Completed '
  ],
  'date_training_completed_1': [
    'Date Completed or Withdrew from Training 1',
    '1308 Date Completed or Withdrew from Training 1',
    'Training End Date',
    'Date Completed Training ',
    '1308 Date Completed, or Withdrew from, Training #1',
    'End Date'
  ],
  'date_entered_training_2': [
    'Date Entered Training 2',
    '1309 Date Entered Training 2',
    '1309 Date Entered Training #2',
    'Start Date_2'
  ],
  'type_training_2': [
    'Type of Training Service 2',
    '1310 Type of Training Service 2',
    '1310 Type of Training Service #2 (WIOA)'
  ],
  'onet_training_2': [
    'Occupational Skills Training Code 2',
    '1311 Occupational Skills Training Code 2',
    '1311 Occupational Skills Training Code #2'
  ],
  'training_completed_2': [
    'Training Completed 2',
    '1312 Training Completed 2',
    '1312 Training Completed #2'
  ],
  'date_training_completed_2': [
    'Date Completed or Withdrew from Training 2',
    '1313 Date Completed or Withdrew from Training 2',
    '1313 Date Completed, or Withdrew from, Training #2',
    'End Date_2'
  ],
  'date_entered_training_3': [
    'Date Entered Training 3',
    '1314 Date Entered Training 3',
    '1314 Date Entered Training #3'
  ],
  'type_training_3': [
    'Type of Training Service 3',
    '1315 Type of Training Service 3',
    '1315 Type of Training Service #3 (WIOA)'
  ],
  'onet_training_3': [
    'Occupational Skills Training Code 3',
    '1316 Occupational Skills Training Code 3',
    '1316 Occupational Skills Training Code #3'
  ],
  'training_completed_3': [
    'Training Completed 3',
    '1317 Training Completed 3',
    '1317 Training Completed #3'
  ],
  'date_training_completed_3': [
    'Date Completed or Withdrew from Training 3',
    '1318 Date Completed or Withdrew from Training 3',
    '1318 Date Completed, or Withdrew from, Training #3'
  ],
  'employment_status_after_exit_q1': [
    '1600 Employed in 1st Quarter After Exit Quarter\n(WIOA)'
  ],
  'type_of_employment_after_exit_q1': [
    '1601 Type of Employment Match 1st Quarter After Exit Quarter (WIOA)'
  ],
  'employment_onet_q1': [
    'Occupational Code of Employment after Exit',
    'O*NET Code',
    '1610 Occupational Code (if available)'
  ],
  'employment_onet_q2': [
    'Occupational Code of Employment 2nd Quarter after Exit Quarter',
    '1612 Occupational Code of Employment 2nd Quarter After Exit Quarter\n(If available)'
  ],
  'employment_onet_q4': [
    'Occupational Code of Employment 4th Quarter after Exit Quarter',
    '1613 Occupational Code of Employment 4th Quarter After Exit Quarter\n(If available)'
  ],
  'employment_naics': [
    'Occupation (NAICS) code',
    'NAICS 2 Digit Code',
    'NAICS 6 Digit Code',
    'NAICS 6 Digit Description'
  ],
  'employment_naics_q1': [
    '1614 Industry Code of Employment 1st Quarter After Exit Quarter'
  ],
  'employment_town': [
    'Town'
  ],
  'employer': [
    'Employer',
    'Employer Name',
    'Entity Name'
  ],
  'job_title': [
    'Job Title ',
    'Job Title'
  ],
  'employer_zip_code': [
    'Employer Zip Code',
    'Zip Code'
  ],
  'employment_naics_q2': [
    '1615 Industry Code of Employment 2nd Quarter After Exit Quarter'
  ],
  'employment_naics_q3': [
    '1616 Industry Code of Employment 3rd Quarter After Exit Quarter'
  ],
  'employment_naics_q4': [
    '1617 Industry Code of Employment 4th Quarter After Exit Quarter'
  ],
  'employment_onet': [
    'O*NET Code'
  ],
  'wages_prior_q3': [
    '1700 Wages 3rd Quarter Prior to Participation Quarter'
  ],
  'wages_prior_q2': [
    '1701 Wages 2nd Quarter Prior to Participation Quarter'
  ],
  'wages_prior_q1': [
    '1702 Wages 1st Quarter Prior to Participation Quarter'
  ],
  'wages_after_exit': [
    'Hourly Wage',
    '1703 Wages 1st Quarter After Exit Quarter\n(WIOA)',
    'Wage'
  ],
  'wages_after_exit_q1': [
    '1703 Wages 1st Quarter After Exit Quarter\n(WIOA)'
  ],
  'hours_prior': [
    'Average Hours per Week',
    'Hours'
  ],
  'wages_after_exit_q2': [
    '1704 Wages 2nd Quarter After Exit Quarter\n(WIOA)'
  ],
  'wages_after_exit_q3': [
    '1705 Wages 3rd Quarter After Exit Quarter\n(WIOA)'
  ],
  'wages_after_exit_q4': [
    '1706 Wages 4th Quarter After Exit Quarter\n(WIOA)'
  ],
  'date_of_birth': [
    'DOB',
    'Date of Birth',
    'birthday',
    '200 Date of Birth'
  ],
  'ethnicity': [
    'Hispanic or Latino (CWP)',
    'Ethnicity',
    'Hispanic or Latino',
    '210 Ethnicity: Hispanic / Latino (WIOA)'
  ],
  'race/ethnicity': [
    'Race Ethnicity',
    '211 American Indian / Alaska Native\n(WIOA)',
    'Race1',
    'Race2',
    'Race3',
    'Race4',
    'Race (CWP)',
    'Race - Self-Identify',
    'What is your race? Select one or more:',
    'Race ',
    'Race',
    '212 Asian (WIOA)',
    '213 Black / African American (WIOA)',
    '214 Native Hawaiian / Other Pacific Islander\n(WIOA)',
    '215 White (WIOA)'
  ],
  'underemployed': [
    ' If you are currently employed, are you underemployed?',
    'If you are employed, are you currently underemployed?',
    'If you are currently employed, are you underemployed?',
    '2101 Underemployed Worker'
  ],
  'veteran_status': [
    'Are you a veteran?',
    'Veteran',
    'veteran_status',
    '300 Veteran Status'
  ],
  'employment_status_at_start': [
    'Are you currently employed?',
    'Employed at Enrollment',
    'Currently Working',
    'Employment Status at Intake',
    'employment_status',
    '400 Employment Status at Program Entry\n(WIOA)'
  ],
  'homeless': [
    'Are you currently homeless?',
    'Homeless',
    'Homeless at time of registration'
  ],
  'low_income': [
    'Does the participant qualify as low income?',
    'Low Income',
    'Meets Definition of Low Income',
    '802 Low Income Status at Program Entry\n(WIOA)'
  ],
  'english_language_learner': [
    'Are you an English language learner?',
    'English Language Learner',
    '803 English Language Learner at Program Entry\n(WIOA)'
  ],
  'basic_skills_deficient': [
    'Basic Skills Deficient',
    'Basic skills deficient',
    '804 Basic Skills Deficient/Low Levels of Literacy at Program Entry'
  ],
  'single_parent': [
    'Are you a single parent?',
    '806 Single Parent at Program Entry (WIOA)'
  ]
}


# ------------------------------------------------------------------------------
# Utility: normalization of header strings for matching
# ------------------------------------------------------------------------------
def _normalize_label(s: str) -> str:
    if s is None:
        return ""
    # Lower, strip, collapse whitespace/newlines to single space
    return " ".join(str(s).lower().strip().split())


def build_normalized_label_index() -> Dict[str, str]:
    """
    Build an index mapping normalized variant text -> canonical variable name.
    Includes the canonical name itself as a recognized variant.
    """
    idx = {}
    for canonical, variants in simple_format_pa25_119_data_labels.items():
        # add canonical itself as a recognized label
        idx[_normalize_label(canonical)] = canonical
        for v in variants:
            idx[_normalize_label(v)] = canonical
    return idx


# ------------------------------------------------------------------------------
# Core aggregation logic
# ------------------------------------------------------------------------------
class Aggregator:
    def __init__(
        self,
        db_path: str,
        run_id: str,
        output_dir: str,
        hl_vars: List[str],
        suppression_threshold: int,
        age_bands: List[str],
        as_of: str,  # 'run_timestamp' or 'YYYY-MM-DD'
        exclude_ll: Optional[Set[str]] = None,
    ):
        self.db_path = db_path
        self.run_id = run_id
        self.output_dir = output_dir
        self.hl_vars = hl_vars
        self.suppression_threshold = suppression_threshold
        self.age_bands = age_bands
        self.as_of = as_of
        self.exclude_ll = exclude_ll or set()

        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.conn.row_factory = sqlite3.Row

        os.makedirs(self.output_dir, exist_ok=True)

        # Precompute label index
        self.label_index = build_normalized_label_index()

    # --------------------- helpers ---------------------
    def _get_run_context(self) -> Tuple[str, str]:
        """
        Returns (dataset_name, run_timestamp_iso) for the given run_id.
        """
        cur = self.conn.execute(
            "SELECT dataset_name, run_timestamp FROM validation_run WHERE run_id = ?",
            (self.run_id,),
        )
        row = cur.fetchone()
        if not row:
            raise ValueError(f"Run ID '{self.run_id}' not found in validation_run.")
        dataset_name = row["dataset_name"]
        run_ts = row["run_timestamp"]
        # Normalize run_timestamp to YYYY-MM-DD if possible (SQLite often stores full timestamp)
        # We'll keep it as-is and rely on julianday() to parse.
        return dataset_name, run_ts

    def _check_linking_id_exists(self):
        """
        Ensure participant has linking_id column.
        """
        cur = self.conn.execute("PRAGMA table_info(participant);")
        cols = [r["name"] for r in cur.fetchall()]
        if "linking_id" not in cols:
            raise RuntimeError(
                "The 'participant' table does not have 'linking_id'. "
                "Please add it before running aggregation (and index it for performance)."
            )

    def _build_column_map_temp(self, dataset_name: str):
        """
        Create a TEMP table 'column_map' with (column_id TEXT PRIMARY KEY, canonical_var TEXT)
        by matching dataset_column.column_name to canonical variables via label_index.
        """
        self.conn.execute("DROP TABLE IF EXISTS column_map;")
        self.conn.execute(
            "CREATE TEMP TABLE column_map (column_id TEXT PRIMARY KEY, canonical_var TEXT);"
        )
        cur = self.conn.execute(
            "SELECT column_id, column_name FROM dataset_column WHERE dataset_name = ?",
            (dataset_name,),
        )
        to_insert = []
        for row in cur.fetchall():
            col_id = row["column_id"]
            raw = row["column_name"]
            norm = _normalize_label(raw)
            canon = self.label_index.get(norm)
            if canon:
                # Exclude HL and explicitly excluded LL variables if desired in mapping
                to_insert.append((col_id, canon))
        if not to_insert:
            print(
                "[WARN] No dataset_column names matched canonical labels; "
                "aggregation will have limited variables."
            )
        self.conn.executemany(
            "INSERT INTO column_map (column_id, canonical_var) VALUES (?, ?)",
            to_insert,
        )
        self.conn.commit()

    def _materialize_canonical_facts_latest(self):
        """
        Create TEMP tables:
          - cf_raw: (linking_id, column_id, value_normalized, timestamp)
          - canonical_facts_latest: (linking_id, canonical_var, value_normalized)
            --> latest timestamp per (linking_id, canonical_var)
        Scope restricted to this run_id.
        """
        self.conn.execute("DROP TABLE IF EXISTS cf_raw;")
        self.conn.execute(
            """
            CREATE TEMP TABLE cf_raw AS
            SELECT
              p.linking_id,
              ch.column_id,
              COALESCE(ch.value_normalized, ch.value_raw) AS value_normalized,
              ch.timestamp
            FROM cell_value_history ch
            JOIN participant p
              ON p.participant_id = ch.participant_id
            WHERE ch.run_id = ?
            """,
            (self.run_id,),
        )
        # Now join cf_raw with column_map to get canonical_var, then pick latest row by timestamp
        self.conn.execute("DROP TABLE IF EXISTS canonical_facts_latest;")
        # Use window function if available; fallback approach: choose max timestamp per group then join
        # SQLite >= 3.25 supports window functions; we'll use ROW_NUMBER.
        self.conn.execute(
            """
            CREATE TEMP TABLE canonical_facts_latest AS
            SELECT linking_id, canonical_var, value_normalized
            FROM (
              SELECT
                r.linking_id,
                m.canonical_var,
                r.value_normalized,
                r.timestamp,
                ROW_NUMBER() OVER (
                  PARTITION BY r.linking_id, m.canonical_var
                  ORDER BY r.timestamp DESC
                ) AS rn
              FROM cf_raw r
              JOIN column_map m
                ON m.column_id = r.column_id
            )
            WHERE rn = 1;
            """
        )
        self.conn.commit()

    def _materialize_hl_dims(self, dataset_name: str, run_ts: str):
        """
        Create TEMP table hl_dims(linking_id, gender, age_band, race_group)
        - gender from canonical_facts_latest('gender'), else 'Unknown'
        - age_band from person.dob vs as_of date (run_timestamp or explicit date)
        - race_group from canonical_facts_latest('race/ethnicity'):
            * If >1 distinct non-null values: 'Multi-Racial'
            * If exactly 1: that value
            * Else: 'Unknown'
        Scope: participants appearing in this run's canonical_facts_latest OR participants in cf_raw.
        """
        # As-of date
        if self.as_of == "run_timestamp":
            as_of_expr = "?"  # bind run_ts
            as_of_value = run_ts
        else:
            # user supplied date string; validate basic format
            try:
                _ = datetime.strptime(self.as_of, "%Y-%m-%d")
            except ValueError:
                raise ValueError(
                    f"--as-of must be 'run_timestamp' or 'YYYY-MM-DD'; got: {self.as_of}"
                )
            as_of_expr = "?"
            as_of_value = self.as_of

        # Build a base set of linking_ids in scope (distinct from cf_raw)
        self.conn.execute("DROP TABLE IF EXISTS _scope_linking_ids;")
        self.conn.execute(
            """
            CREATE TEMP TABLE _scope_linking_ids AS
            SELECT DISTINCT linking_id FROM cf_raw;
            """
        )

        # Gender per linking_id
        self.conn.execute("DROP TABLE IF EXISTS _hl_gender;")
        self.conn.execute(
            """
            CREATE TEMP TABLE _hl_gender AS
            SELECT
              s.linking_id,
              COALESCE(g.value_normalized, 'Unknown') AS gender
            FROM _scope_linking_ids s
            LEFT JOIN canonical_facts_latest g
              ON g.linking_id = s.linking_id
             AND g.canonical_var = 'gender';
            """
        )

        # Age band per linking_id
        # join participant -> person to get dob
        # Compute age (floor((julianday(as_of) - julianday(dob)) / 365.25))
        # If dob null or not parseable, age_band='Unknown'
        # Bucket to configured age bands (we'll build SQL CASE dynamically)
        # First, get dob per linking_id
        self.conn.execute("DROP TABLE IF EXISTS _dob;")
        self.conn.execute(
            """
            CREATE TEMP TABLE _dob AS
            SELECT
              s.linking_id,
              per.dob
            FROM _scope_linking_ids s
            JOIN participant p
              ON p.linking_id = s.linking_id
            JOIN person per
              ON per.person_id = p.person_id;
            """
        )
        # Build CASE statement for age bands
        # age_bands like ['16-24','25-34','35-44','45-54','55+']
        band_cases = []
        for band in self.age_bands:
            band = band.strip()
            if "-" in band:
                lo, hi = band.split("-", 1)
                band_cases.append(
                    f"WHEN age >= {int(lo)} AND age <= {int(hi)} THEN '{band}'"
                )
            elif band.endswith("+"):
                base = int(band[:-1])
                band_cases.append(f"WHEN age >= {base} THEN '{band}'")
            else:
                # single number bucket
                band_cases.append(f"WHEN age = {int(band)} THEN '{band}'")
        case_sql = " ".join(band_cases) if band_cases else "ELSE 'Unknown'"

        self.conn.execute("DROP TABLE IF EXISTS _hl_age;")
        self.conn.execute(
            f"""
            CREATE TEMP TABLE _hl_age AS
            WITH ages AS (
              SELECT
                d.linking_id,
                CASE
                  WHEN d.dob IS NOT NULL AND julianday(d.dob) IS NOT NULL AND julianday({as_of_expr}) IS NOT NULL
                  THEN CAST((julianday({as_of_expr}) - julianday(d.dob)) / 365.25 AS INTEGER)
                  ELSE NULL
                END AS age
              FROM _dob d
            )
            SELECT
              a.linking_id,
              CASE
                {" ".join(band_cases) if band_cases else ""}
                ELSE 'Unknown'
              END AS age_band
            FROM ages a;
            """,
            (as_of_value, as_of_value) if self.as_of == "run_timestamp" else (as_of_value, as_of_value),
        )

        # Race group per linking_id
        self.conn.execute("DROP TABLE IF EXISTS _hl_race;")
        self.conn.execute(
            """
            CREATE TEMP TABLE _hl_race AS
            WITH race_vals AS (
              SELECT linking_id, value_normalized AS val
              FROM canonical_facts_latest
              WHERE canonical_var = 'race/ethnicity'
            ),
            race_agg AS (
              SELECT linking_id,
                     COUNT(DISTINCT val) AS distinct_count,
                     MIN(val) AS only_value
              FROM race_vals
              GROUP BY linking_id
            )
            SELECT
              s.linking_id,
              CASE
                WHEN ra.distinct_count > 1 THEN 'Multi-Racial'
                WHEN ra.distinct_count = 1 THEN COALESCE(ra.only_value, 'Unknown')
                ELSE 'Unknown'
              END AS race_group
            FROM _scope_linking_ids s
            LEFT JOIN race_agg ra
              ON ra.linking_id = s.linking_id;
            """
        )

        # Combine into hl_dims
        self.conn.execute("DROP TABLE IF EXISTS hl_dims;")
        self.conn.execute(
            """
            CREATE TEMP TABLE hl_dims AS
            SELECT
              s.linking_id,
              g.gender,
              a.age_band,
              r.race_group
            FROM _scope_linking_ids s
            LEFT JOIN _hl_gender g ON g.linking_id = s.linking_id
            LEFT JOIN _hl_age a    ON a.linking_id = s.linking_id
            LEFT JOIN _hl_race r   ON r.linking_id = s.linking_id;
            """
        )
        self.conn.commit()

    def _get_ll_variables(self) -> List[str]:
        """
        LL variables = all canonical keys minus HL variables, minus explicit exclusions.
        Also remove clearly PII columns ('First Name', 'Last Name'), and HL sources ('date_of_birth', 'race/ethnicity').
        """
        all_vars = set(simple_format_pa25_119_data_labels.keys())
        # HLs include 'age' which isn't a column — remove its source variables
        pii = {"First Name", "Last Name"}
        hl_sources = {"date_of_birth", "race/ethnicity"}
        # HL "age" doesn't exist in canonical facts; skip it in LL list
        base_exclude = set(self.hl_vars) | self.exclude_ll | pii | hl_sources | {"age"}
        ll_vars = sorted([v for v in all_vars if v not in base_exclude])
        return ll_vars

    def _get_hl_categories(self, hl: str) -> List[str]:
        cur = self.conn.execute(f"SELECT DISTINCT {hl} AS hl_val FROM hl_dims;")
        cats = [r["hl_val"] if r["hl_val"] is not None else "Unknown" for r in cur.fetchall()]
        # Ensure 'Unknown' is present if any nulls
        if "Unknown" not in cats:
            # Check if any are null (already mapped earlier)
            pass
        return sorted(cats)

    def _query_ll_distribution(self, hl: str, ll: str) -> List[sqlite3.Row]:
        """
        Return rows: (hl_value, ll_value, cnt) for the given (hl, ll).
        Left join ensures null ll_value (Unknown) appears.
        """
        sql = f"""
        SELECT
          d.{hl} AS hl_value,
          f.value_normalized AS ll_value,
          COUNT(DISTINCT d.linking_id) AS cnt
        FROM hl_dims d
        LEFT JOIN canonical_facts_latest f
          ON f.linking_id = d.linking_id
         AND f.canonical_var = ?
        GROUP BY d.{hl}, f.value_normalized
        ORDER BY d.{hl};
        """
        cur = self.conn.execute(sql, (ll,))
        return cur.fetchall()

    def _build_pivot(
        self,
        hl: str,
        ll: str,
        rows: List[sqlite3.Row],
        suppression_threshold: int,
    ) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Build columns and data for pivoted wide table.
        Columns: ['hl_value', <each ll category>, 'Unknown', 'Total']
        Data: one dict per HL category row with counts.
        """
        # Collect categories present (excluding NULL which becomes 'Unknown')
        ll_categories: Set[str] = set()
        for r in rows:
            v = r["ll_value"]
            if v is not None:
                ll_categories.add(str(v))

        # Order columns deterministically
        ll_cols = sorted(ll_categories)

        # Initialize data structure
        data_by_hl: Dict[str, Dict[str, Any]] = {}
        for r in rows:
            hl_val = r["hl_value"] if r["hl_value"] is not None else "Unknown"
            ll_val = r["ll_value"]
            cnt = int(r["cnt"]) if r["cnt"] is not None else 0

            if hl_val not in data_by_hl:
                data_by_hl[hl_val] = {"hl_value": hl_val}
                for c in ll_cols:
                    data_by_hl[hl_val][c] = 0
                data_by_hl[hl_val]["Unknown"] = 0
                data_by_hl[hl_val]["Total"] = 0

            if ll_val is None:
                data_by_hl[hl_val]["Unknown"] += cnt
            else:
                data_by_hl[hl_val][str(ll_val)] += cnt

            # We'll recompute Total below to avoid double counting
        # Compute Totals per HL
        for hl_val, row in data_by_hl.items():
            total = row["Unknown"] + sum(row[c] for c in ll_cols)
            row["Total"] = total

        # Apply suppression
        def suppress(val: int) -> Optional[int]:
            if val is None:
                return None
            if val < suppression_threshold:
                return None  # blank cell in CSV
            return val

        for hl_val, row in data_by_hl.items():
            for c in ll_cols + ["Unknown"]:
                row[c] = suppress(row[c])
            # Typically, we keep Total visible; if you want to suppress totals too, uncomment:
            # row["Total"] = suppress(row["Total"])

        # Final columns order
        columns = ["hl_value"] + ll_cols + ["Unknown"] + ["Total"]
        # Sorted rows by hl_value
        final_rows = [data_by_hl[hlv] for hlv in sorted(data_by_hl.keys())]

        return columns, final_rows

    def _write_csv(self, table_name: str, columns: List[str], rows: List[Dict[str, Any]]):
        path = os.path.join(self.output_dir, f"{table_name}.csv")
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        print(f"  ✅ wrote {path}")

    # --------------------- main orchestrator ---------------------
    def run(self):
        print(f"🔌 Connecting to DB: {self.db_path}")
        dataset_name, run_ts = self._get_run_context()
        print(f"📦 Run ID: {self.run_id} | Dataset: {dataset_name} | Run timestamp: {run_ts}")

        self._check_linking_id_exists()
        print(f"🔗 Using distinct linking_id for aggregation")

        print("🗺️  Building column map from dataset_column → canonical variables …")
        self._build_column_map_temp(dataset_name)

        print("📚 Materializing canonical facts (latest per linking_id/var) …")
        self._materialize_canonical_facts_latest()

        print("🧱 Building high-level dimensions (gender, age_band, race_group) …")
        self._materialize_hl_dims(dataset_name, run_ts)

        # Validate HL vars exist in hl_dims columns
        cur = self.conn.execute("PRAGMA table_info(hl_dims);")
        hl_cols = {r["name"] for r in cur.fetchall()}
        for hl in self.hl_vars:
            if hl not in hl_cols:
                raise RuntimeError(f"HL variable '{hl}' not available in hl_dims.")

        # Low-level variables
        ll_vars = self._get_ll_variables()
        print(f"📄 Low-level variables to aggregate: {len(ll_vars)} found.")
        # For visibility, print a few
        print("   e.g.,", ", ".join(ll_vars[:10]), "… (truncated)")

        # For each HL × LL, produce aggregated table
        for hl in self.hl_vars:
            print(f"\n=== HL: {hl} ===")
            # Confirm HL categories present
            hl_cats = self._get_hl_categories(hl)
            print(f"   HL categories: {hl_cats}")

            for ll in ll_vars:
                table_name = f"hl_{hl}__ll_{ll}"
                print(f"   ➜ Aggregating {table_name} …")
                rows = self._query_ll_distribution(hl, ll)
                columns, data_rows = self._build_pivot(
                    hl=hl,
                    ll=ll,
                    rows=rows,
                    suppression_threshold=self.suppression_threshold,
                )
                self._write_csv(table_name, columns, data_rows)

        print("\n✅ Aggregation complete.")

        # Optional: write manifest
        manifest_path = os.path.join(self.output_dir, "manifest.txt")
        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write(f"run_id={self.run_id}\n")
            f.write(f"dataset_name={dataset_name}\n")
            f.write(f"run_timestamp={run_ts}\n")
            f.write(f"hl_vars={','.join(self.hl_vars)}\n")
            f.write(f"suppression_threshold={self.suppression_threshold}\n")
            f.write(f"age_bands={','.join(self.age_bands)}\n")
            f.write(f"as_of={self.as_of}\n")
            f.write(f"output_dir={self.output_dir}\n")
        print(f"📝 Manifest written: {manifest_path}")


# ------------------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------------------
def parse_args():
    parser = argparse.ArgumentParser(
        description="Aggregate long-form SQLite data into wide tables for Power BI."
    )
    parser.add_argument("--db", required=True, help="Path to SQLite DB (validation_dev.db)")
    parser.add_argument("--run-id", required=True, help="Run ID to aggregate (validation_run.run_id)")
    parser.add_argument("--output-dir", required=True, help="Directory to write CSV outputs")
    parser.add_argument("--hl", nargs="+", default=["gender", "age", "race"],
                        help="High-level variables to group by (columns in hl_dims): default ['gender','age','race']")
    parser.add_argument("--suppression-threshold", type=int, default=5,
                        help="Minimum cell size; counts below are blanked (default: 5)")
    parser.add_argument("--age-bands", nargs="+", default=["16-24", "25-34", "35-44", "45-54", "55+"],
                        help="Age bands for bucketing (default: WIOA-like bands)")
    parser.add_argument("--as-of", default="run_timestamp",
                        help="Age as-of date: 'run_timestamp' or 'YYYY-MM-DD' (default: run_timestamp)")
    parser.add_argument("--exclude-ll", nargs="*", default=[],
                        help="Optional extra LL variables to exclude by canonical name")
    return parser.parse_args()


def main():
    args = parse_args()
    agg = Aggregator(
        db_path=args.db,
        run_id=args.run_id,
        output_dir=args.output_dir,
        hl_vars=args.hl,
        suppression_threshold=args.suppression_threshold,
        age_bands=args.age_bands,
        as_of=args.as_of,
        exclude_ll=set(args.exclude_ll),
    )
    agg.run()


if __name__ == "__main__":

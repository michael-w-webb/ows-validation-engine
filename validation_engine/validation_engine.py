"""
cc_validation_engine.py
=======================

Core validation engine for schema-based normalization, cross-sheet rule
evaluation, and optional SQL-backed audit logging. This module defines the
`ValidationEngine` class, which orchestrates end-to-end validation of
workbooks submitted by external organizations (e.g., CareerConneCT,
Good Jobs Challenge).

Overview
--------
The engine performs the following high-level steps:

1. **Sheet-by-sheet column-type normalization**
   Uses column-type classes (e.g., `categoricalColumn`, `dateTimeColumn`,
   `identifierColumn`) to coerce raw spreadsheet values into a consistent,
   validated format. Column-type classes also generate column-level errors.

2. **Identity resolution and participant tracking (optional)**
   When `logging=True`, the engine:
   - creates multiple spreadsheet-specific key variants via `KeyCreator`,
   - resolves or creates global `person_id` values based on keys,
   - assigns `participant_id` values for each dataset instance, and
   - logs normalized cell values and participant presence to the database.

3. **Cross-sheet rule evaluation**
   Delegates rule execution to `CrossRuleEngine`, applying rule sets such as
   connected presence, conditional blanks, conditional requirements, and
   date-based conditional requirements.

4. **Error aggregation**
   All normalization errors and cross-sheet violations are collected into
   DataFrames, accessible via `engine.errors` or `engine.get_all_errors()`.

Inputs
------
The engine requires:
    - ``workbook_definitions`` (dict):
        Schema describing sheets, expected columns, column types, and
        accepted responses.
    - ``cross_rules`` (list[tuple], optional):
        Rule sets to apply during cross-sheet validation. If not provided,
        the caller is expected to supply rule sets externally.
    - ``logging`` (bool):
        Enables write-back to the SQL logging database via
        ``ValidationDBLogger``.

Within `validate_workbook`, the caller must supply:
    - ``file`` (str):
        Identifier in ``org|period`` format.
    - ``workbook_type`` (str):
        Dataset name (e.g., "training data").
    - ``workbook_format`` (str):
        Workbook layout ("simple format" or "four sheet format").
    - ``dfs_by_sheet`` (dict[str, pandas.DataFrame]):
        Raw data from each sheet after loading.
    - ``keycreators`` (list of (KeyCreator, str)):
        Pairs of key generators and output column names for identity matching.

Outputs
-------
Attributes populated during validation:
    - ``normalized_data`` (dict[str → DataFrame]):
        Cleaned, normalized DataFrames for each sheet.
    - ``errors`` (list[DataFrame]):
        Column-level and cross-sheet validation error frames.
    - ``column_error_index`` (dict[(sheet, column) → set[int]]):
        Tracks row indices associated with column-level errors.

Methods:
    - ``validate_workbook``:
        Main entry point for executing the full validation workflow.
    - ``get_all_errors``:
        Returns a single concatenated DataFrame of all errors.
    - ``make_entry_key``:
        Generates a deterministic hashed ID for record tracking.

Assumptions and Constraints
---------------------------
- ``workbook_definitions`` fully describe all sheets and expected columns.
- Each sheet includes a ``row_number`` column corresponding to the original
  Excel row numbers.
- ``identity_sheet`` must exist ("Report" for simple format, "Personal
  Information" for multi-sheet format).
- Column normalization must precede cross-sheet rule evaluation.
- KeyCreator fields must match post-normalization column names.
- Database schema must be initialized before enabling logging.

Side Effects
------------
- When ``logging=True``, this module writes:
    - run metadata,
    - normalized cell values,
    - person/participant resolution events,
    - presence logs,
    - validation rule violations
  to the SQL logging database via ``ValidationDBLogger``.

Security / PII Notes
--------------------
- This engine processes sensitive PII including names, DOB, ZIP code, and
  state ID values.
- Identity keys are generated using SHA-256, but raw PII exists in memory
  during normalization and logging.
- Database logs may contain raw and normalized values; appropriate access
  controls must be enforced externally.

This module is intended to be imported by higher-level orchestration scripts
(e.g., `cc_validation_main.py`) and is not designed for direct command-line
execution.
"""

import pandas as pd
from validation_engine.validation_column_types import *
from validation_engine.cross_rule_engine import CrossRuleEngine

### SQL Logging Related Imports 
from validation_engine.db_logger import ValidationDBLogger
from hashlib import sha256
from datetime import datetime
import warnings

COLUMN_CLASS_MAP = {
    "categorical": categoricalColumn,
    "fileSpecificCategorical":fileSpecificCategoricalColumn,
    "identifier": identifierColumn,
    "boolean": booleanColumn,
    "dateTime": dateTimeColumn,
    "zipCode": zipCodeColumn,
    "stateID7": stateID7Column,
    "ONETCode": ONETCodeColumn,
    "CIPCode": CIPCodeColumn,
    "hourlyWage": hourlyWageColumn,
    "hoursWorked": hoursWorkedColumn,
    "NAICSCode": NAICSCodeColumn
}

class ValidationEngine:
    """
    Core orchestrator for sheet-level column validation in CareerConneCT /
    workforce-data workbooks.

    The engine applies:
       • column-type normalization (dates, categorical, integers, Booleans, ZIPs, etc.)
       • file-specific categorical validation (for org-dependent fields)
       • error generation with row-level metadata
       • row-dropping rules for entirely blank participant records
       • construction of `column_error_index` for downstream cross-sheet checks

    This class handles validation for **one workbook at a time**.  
    Multi-sheet and cross-sheet coordination occurs in the calling
    `validate_workbook()` method (not included in this snippet).

    Attributes:
        workbook_definitions (dict):
            Schema describing expected columns, column types, and accepted responses
            for each sheet in the workbook.
        cross_rules (dict):
            Optional override for cross-sheet validation rules.
        logging (bool):
            If True, downstream caller logs to SQLite via `ValidationDBLogger`.
        normalized_data (dict[str, DataFrame]):
            Resulting normalized sheets after validation.
        errors (list[DataFrame]):
            List of error DataFrames produced per sheet.
        column_error_index (dict[(sheet, column) → set[int]]):
            Fast lookup for cross-rule engine; identifies failed rows per column.
        file (str or None):
            Identifier used when generating error reports (“org|quarter|filename”).
    """
    def __init__(self, workbook_definitions, cross_rules=None, logging = False, log_description = None, mismatch_check = True):
        
        ## file meta data navigation 
        self.workbook_definitions = workbook_definitions
        self.workbook_type = None
        self.workbook_format = None
        self.workbook_definitions_location = None
        
        self.cross_rules = cross_rules or {}
        self.normalized_data = {}   # {sheet_name: DataFrame}
        self.errors = []            # list of DataFrames
        self._validated = False
        self._cross_checked = False
        self.file = None 
        self.logging = logging 
        self.log_description = log_description
        self.mismatch_check = mismatch_check
        self.mismatches = []
        self.single_sheet = []
        self.db_logger = None
        self.run_id = None

        if self.logging:

            if not self.log_description:

                raise ValueError("Engine call must include a log_description argument if Logging is True")

            self.db_logger = ValidationDBLogger()
            

    def _validate_sheet(self, df, sheet_name, accepted_responses, row_offset=1):
        
        """
        Validate and normalize all columns for a single sheet.

        This method applies the column-type classes defined in
        `COLUMN_CLASS_MAP` to each column described in `accepted_responses`,
        producing both a normalized DataFrame and a structured error DataFrame.

        Args:
            df (pd.DataFrame):
                Raw sheet data as loaded by the WorkbookLoader.
            sheet_name (str):
                Name of the sheet being validated. Used for error metadata.
            accepted_responses (dict):
                Column-level schema for this sheet, e.g.:

                    {
                        "Date Entered Training": {"type": "date", "required": True},
                        "County": {
                            "type": "categorical",
                            "accepted_responses": ["Hartford", "New Haven", ...]
                        },
                        ...
                    }

            file (str, optional):
                Full workbook identifier (`"org|quarterd"`). Propagated
                into error logs for data lineage.
            row_offset (int, optional):
                Excel row offset used when translating DataFrame indices
                back into user-visible spreadsheet row numbers.

        Returns:
            tuple:
                (normalized_df, errors_df)

                • normalized_df (pd.DataFrame):
                    All columns normalized, reindexed (after dropping fully blank rows),
                    and containing `id_key`/`row_number` if present.
                
                • errors_df (pd.DataFrame):
                    Structured validation errors with columns:
                    ["file","sheet","row_number","column","rule","raw_value","normalized"]

                    Empty if no errors detected.

        Behavior:
            • Applies type-specific normalizers (date, integer, categorical, ZIP, etc.).
            • Handles file-specific categorical fields (e.g., responses vary by CBO).
            • Records per-column errors via each validator’s `errors_df()` method.
            • Drops rows that are blank for all non-identity columns.
            • Preserves `id_key` and `row_number`.
            • Updates `self.column_error_index` for cross-sheet rules.

        Side Effects:
            • Mutates `self.column_error_index` (used later by cross-rule engine).
            • Sets `self._validated = True`.
            • Prints warnings for missing/undefined columns.

        Notes:
            • Validation order is column-by-column; errors do not prevent processing.
            • Validators may coerce values (string normalization, padding, casefolding).
            • Row removal logic ensures that blank spreadsheet rows do not generate
              false positive validation errors.

        """
        normalized_cols = {}
        all_errors = []

        if "id_key" in df.columns:
            normalized_cols["id_key"] = df["id_key"]

        if f"row_number_{sheet_name}" in df.columns:
            normalized_cols[f"row_number_{sheet_name}"] = df[f"row_number_{sheet_name}"]
            
        if "source_file" in df.columns:
            normalized_cols["source_file"] = df["source_file"]

        for col, spec in accepted_responses.items():
            if col not in df.columns:
                print(f"skip {col}")
                continue

            col_type = spec.get("type")
            if not col_type:
                continue

            ### categorical responses require extra information passed by workbook_definitions
            cls = COLUMN_CLASS_MAP[col_type]
            if col_type == "categorical":
                accepted = spec.get("accepted_responses", [])
                validator = cls(accepted_responses=accepted,
                required=spec.get("required", False), 
                row_numbers = df[f"row_number_{sheet_name}"])
            elif col_type == "fileSpecificCategorical":
                accepted = spec.get("accepted_responses",[])
                validator = cls(accepted_responses = accepted, 
                required = spec.get("required", False),
                file = self.file.split("|")[0],
                row_numbers = df[f"row_number_{sheet_name}"]
                )
            elif col_type == "hourlyWage":
                max_wage = spec.get("max_wage", 45)
                min_wage = spec.get("min_wage", 0)
                validator = cls(max_wage=max_wage, min_wage=min_wage, required=spec.get("required", False), row_numbers = df[f"row_number_{sheet_name}"])
            else:
                validator = cls(required=spec.get("required", False), row_numbers = df[f"row_number_{sheet_name}"])

            raw = df[col]
            s_norm = validator.normalize(raw)
            s_fmt = validator.format(s_norm)

            errs = validator.errors_df(col, raw, s_norm, file=self.file, sheet=sheet_name, row_offset=row_offset)    

            if not errs.empty:

                if "id_key" in df.columns:
            
                    errs["id_key"] = df.loc[errs.index, "id_key"].values
            
                all_errors.append(errs)

            normalized_cols[col] = raw
            normalized_cols[f"{col}_normalized"] = s_fmt

        normalized_df = pd.DataFrame(normalized_cols, index=df.index)

        errors_df = pd.concat(all_errors) if all_errors else pd.DataFrame(
            columns=["file","sheet",f"row_number_{sheet_name}","column","rule","raw_value","normalized"]
        )

        #         ### Moved this to the column type classes, inappropriate for the engine to be normalizing, leaving here for reference in case changes broke stuff 
        # normalized_df = normalized_df.replace(r"^\s*$", pd.NA, regex=True)    # empty or whitespace-only
        # normalized_df = normalized_df.replace(r"^0+$", pd.NA, regex=True)     # "0", "00", etc.
        # normalized_df = normalized_df.replace(
        #     to_replace=[
        #         "#VALUE!", "#REF!", "#DIV/0!", "#NAME?", "#NULL!", "#NUM!",
        #         "#N/A", "nan", "<NA>", "NaN"
        #     ],
        #     value=pd.NA
        # )

        # Drop rows that are all blank except id_key/row_number
        cols_to_check = [c for c in normalized_df.columns if c not in ["id_key", f"row_number_{sheet_name}"]]
        drop_mask = normalized_df[cols_to_check].isna().all(axis=1)
        dropped_row_numbers = normalized_df.loc[drop_mask, f"row_number_{sheet_name}"].tolist()
        normalized_df = normalized_df.loc[~drop_mask].copy()
        # ✅ Reindex to keep positional alignment with masks
        normalized_df.reset_index(drop=True, inplace=True)

        # Build column_error_index from the combined errors_df
        self.column_error_index = getattr(self, "column_error_index", {})
        if not errors_df.empty:
            for col in errors_df["column"].unique():
                bad_idx = errors_df.loc[errors_df["column"] == col].index
                if len(bad_idx):
                    self.column_error_index[(sheet_name, col)] = set(bad_idx)

        # --- Remove any errors that belong to fully blank rows ---
        if dropped_row_numbers:
            errors_df = errors_df[~errors_df["row_number"].isin(dropped_row_numbers)]

        self._validated = True
        return normalized_df, errors_df
    
    def _set_org(self): 

        if isinstance(self.file, str):
            parts = self.file.split("|")

            if len(parts) == 2:
                self.org = parts[0] 
                if(len(parts[0])==0):
                    warnings.warn("Potential Problem - Org is empty string.")
        else:
            raise ValueError("Cannot set org: file must be a string structured as {org}|{quarter}")

    def _set_quarter(self): 

        if isinstance(self.file, str):
            parts = self.file.split("|")

            if len(parts) == 2:
                self.quarter = parts[1] 
                if(len(parts[1])==0):
                    warnings.warn("Potential Problem - Quarter is empty string.")
        else:
            raise ValueError("Cannot set quarter: file must be a string structured as {org}|{quarter}")

    def set_file(self, file):
        
        self.file = file
        self._set_org()
        self._set_quarter()

    def _assert_file_context_ready(self) -> None:
        if self.file is None:
            raise RuntimeError("Engine is not ready: file/org/quarter have not been set. Call set_file().")
        if self.org is None:
            raise RuntimeError("Engine is not ready: file/org/quarter have not been set. Call set_file().")
        if self.quarter is None: 
            raise RuntimeError("Engine is not ready: file/org/quarter have not been set. Call set_file().")
        
    def _set_workbook_format(self, workbook_format):
        
        if workbook_format not in self.workbook_definitions[self.workbook_type]:
            raise ValueError(f"Workbook format '{workbook_format}' is not defined for workbook type '{self.workbook_type}'.")
        self.workbook_format = workbook_format
        
    def _set_workbook_definitions_context(self, workbook_type, workbook_format):

        if workbook_type not in self.workbook_definitions:
            raise ValueError(f"Workbook type '{workbook_type}' is not defined.")
        self.workbook_type = workbook_type

        self._set_workbook_format(workbook_format)

    def _set_workbook_definitions_location(self, sheet_name):

        working_location = self.workbook_definitions[self.workbook_type][self.workbook_format]

        if sheet_name not in working_location:
            raise ValueError(f"Sheet name '{sheet_name}' is not defined for workbook type '{self.workbook_type}' and format '{self.workbook_format}'.")
        
        self.workbook_definitions_location = self.workbook_definitions[self.workbook_type][self.workbook_format][sheet_name]

    def _get_file_metadata(self, item:str):

        if self.workbook_definitions_location is None: 
            raise ValueError("workbook_definitions_location is not set. Call set_workbook_definitions_location first.")
        
        return self.workbook_definitions_location[item]

    ## normalize_data
    def normalize_data(self, workbook_type, workbook_format, dfs_by_sheet):

        ### confirm that the file, org, and quarter values have been set correctly.
        self._assert_file_context_ready()

        ### make sure the provided workbook type and format vavlues are valid and pass them to the engine's self.values
        self._set_workbook_definitions_context(workbook_type, workbook_format)

        ### declare the run level column_error_index value that is going to be used across validate_sheet calls 
        self.column_error_index = {}

        ### if logging is enabled, create a new run entry in the database and pass the run id to the engine for later use
        if self.logging and self.run_id is None:
            ## create a unique id connected to the information passed in the run table 
            self.run_id =  self.db_logger.start_run(self.workbook_type, self.org, self.quarter, triggered_by="mwebb", run_desription = self.run_description)

        # ============================================================
        # 1️⃣ Sheet-by-sheet validation
        # ============================================================
        
        ### using the dfs_by_sheet dictionary generated by the workbook loader loop through validate_sheet calls and generate a normalized data dictionary and an errors list
        for sheet_name, df in dfs_by_sheet.items():

            ### using the workbook type and format values set earlier, set the workbook definitions location for the current sheet
            self._set_workbook_definitions_location(sheet_name)

            ### grab the accepted response dictionary for the current sheet
            accepted_responses = self._get_file_metadata("accepted_responses")

            norm_df, errs = self._validate_sheet(df, sheet_name, accepted_responses)

            cols_to_check = [c for c in norm_df.columns if c not in ["id_key", f"row_number_{sheet_name}"]]
            norm_df = norm_df.dropna(subset=cols_to_check, how="all")

            ### pass the cleaned data to the engine attribute for normalized data
            self.normalized_data[sheet_name] = norm_df

            ### pass the errors to the existing engine level error list 
            if not errs.empty:
                self.errors.append(errs)

    #### identify canonical entries and log to the databse if logging 

    def ensure_normalized_data(self, normalized_data: dict) -> None:
        if normalized_data is None:
            raise ValueError("normalized_data is None")

        if not isinstance(normalized_data, dict) or not normalized_data:
            raise ValueError("normalized_data must be a non-empty dict")  

    def build_id_key(self,
        df: pd.DataFrame,
        columns: list[str],
        *,
        normalize: bool = True,
        sep: str = "|",
        null_token: str = ""
    ) -> pd.Series:
        """
        Build a deterministic ID key from an arbitrary list of columns.
        """

        if not columns:
            raise ValueError("columns must contain at least one column name")

        missing = [c for c in columns if c not in df.columns]
        if missing:
            raise KeyError(f"Missing columns for id_key: {missing}")

        parts = []

        for col in columns:
            s = df[col].astype(str)

            if normalize:
                s = (
                    s.str.strip()
                    .str.lower()
                    .replace({"nan": null_token, "none": null_token})
                )

            parts.append(s.fillna(null_token))

        return pd.Series(
            sep.join(values) for values in zip(*parts)
        )

    def attach_identity_key(self,
        normalized_data: dict,
        identity_sheet: str,
        id_columns: list[str],
        id_col_name: str = "id_key"
    ) -> None:
        
        self.ensure_normalized_data(normalized_data)

        if identity_sheet not in normalized_data:
            raise KeyError(f"Identity sheet '{identity_sheet}' not found")

        df = normalized_data[identity_sheet]

        df[id_col_name] = self.build_id_key(
            df,
            id_columns,
            normalize=True
        )

        normalized_data[identity_sheet] = df

    ## main function, the one implementing the other functions 
    def validate_workbook(self, file, workbook_type, workbook_format, dfs_by_sheet, passed_identity_sheet, keycreators = None):
        """
        Validate an entire workbook, generate normalized per-sheet data, resolve
        participant identity, apply cross-sheet rules, and optionally log all
        results to the validation database.

        This method orchestrates the entire validation lifecycle:

        1. **Sheet-level validation**
           • Each sheet listed in `dfs_by_sheet` is validated using column-type
             validators defined in `workbook_definitions`.
           • Invalid values generate row-level error records.
           • Blank records (all-NA except id_key/row_number) are removed.
           • Normalized DataFrames are stored in `self.normalized_data`.

        2. **Identity resolution**
           • Determines the canonical identity sheet:
               - `"Report"` for simple-format workbooks
               - `"Personal Information"` for four-sheet format
           • Ensures `id_key` exists (auto-generated for simple format).
           • If database logging is enabled:
               - Applies all configured `KeyCreator` instances.
               - Resolves or creates `person` records in the `person` table.
               - Creates or updates `participant` records for the dataset.

        3. **Logging normalized cell values**
           • When logging is enabled, all normalized values for all sheets
             are written to the database via `ValidationDBLogger`.

        4. **Participant presence tracking**
           • Marks participants as `"present"` or `"missing"` for the run,
             enabling longitudinal participant tracking across reporting cycles.

        5. **Cross-sheet rule enforcement**
           • Delegates to `_apply_cross_rules()` which uses `CrossRuleEngine`
             to evaluate rules such as:
               - connected presence
               - conditional required fields
               - conditional blank-unless
               - date comparison rules
           • Any violations are appended to the error collection.

        6. **Violation persistence**
           • If logging is enabled, attaches `participant_id` to each error row
             using `id_key` matching.
           • Persists each rule violation into the `validation_violation` table.

        Args:
            file (str):
                Identifier for the workbook, typically of the form
                `"org|quarter|filename"`. Used for logging and lineage.
            workbook_type (str):
                Dataset category (e.g., `"CareerConneCT"`).
            workbook_format (str):
                Layout style defined in `workbook_definitions`
                (e.g., `"simple format"`, `"four sheet format"`).
            dfs_by_sheet (dict[str, pandas.DataFrame]):
                Raw DataFrames produced by the loader, keyed by sheet name.
            keycreators (list[tuple], optional):
                List of `(KeyCreator, column_name)` pairs used to generate
                additional hashed or unhashed identity keys.

        Returns:
            None
                All normalized data, errors, and logging output are stored in:
                • `self.normalized_data`
                • `self.errors`
                • database tables (if logging enabled)

        Raises:
            ValueError:
                If the required identity sheet is missing.
            KeyError:
                If workbook definitions are incomplete for the given
                workbook type or format.

        Notes:
            • This method must be called before any cross-rule checks or data export.
            • `self.errors` collects sheet-level and cross-sheet violations.
            • Calling code may retrieve all errors via `get_all_errors()`.
        """
        self.file = file
        self.column_error_index = {}

        self.org = file.split("|")[0] if isinstance(file, str) else ""
        self.quarter = file.split("|")[1] if isinstance(file, str) else ""

        if self.logging:
            ## create a unique id connected to the information passed in the run table 
            self.run_id =  self.db_logger.start_run(workbook_type, self.org, self.quarter, triggered_by="mwebb", run_description = self.log_description)
            self.db_logger.raw_data_points = dfs_by_sheet
    
        # ============================================================
        # 1️⃣ Sheet-by-sheet validation
        # ============================================================
        print(f"{self.org} {workbook_type} - Starting Normalization @ {datetime.now()}")

        for sheet_name, df in dfs_by_sheet.items():

            accepted_responses = self.workbook_definitions[workbook_type][workbook_format][sheet_name]["accepted_responses"]

            norm_df, errs = self._validate_sheet(df, sheet_name, accepted_responses)

            cols_to_check = [c for c in norm_df.columns if c not in ["id_key", f"row_number_{sheet_name}"]]
            norm_df = norm_df.dropna(subset=cols_to_check, how="all")

            self.normalized_data[sheet_name] = norm_df
            if not errs.empty:
                self.errors.append(errs)

        # ============================================================
        # 2️⃣ Identify canonical participants (from identity sheet)
        # ============================================================
        
        if(workbook_format == "simple format"):
            identity_sheet = sheet_name
            id_df = self.normalized_data.get(identity_sheet)
            id_df["id_key"] = (id_df["First Name"].fillna("") + "|" + id_df["Last Name"].fillna(""))
             
            raw_data = dfs_by_sheet.get(identity_sheet)
            if raw_data is None:
                raise KeyError(f"Identity sheet '{identity_sheet}' not found")

            raw_data["id_key"] = (raw_data["First Name"].fillna("") + "|" + raw_data["Last Name"].fillna(""))
        else: 
            identity_sheet = passed_identity_sheet
            id_df = self.normalized_data.get(identity_sheet)
        if id_df is None:
            raise ValueError(f"Identity sheet '{identity_sheet}' not found in workbook.")
        
        # Generate spreadsheet specific keys that can be used to map back to a universal person ID


        print(f"{self.org} {workbook_type} - Recording Mismatches @ {datetime.now()}")

        def record_mismatches(keys, org, quarter, sheet, issue):
            for k in keys:
                self.mismatches.append({
                    "org": org,
                    "period": quarter,
                    "sheet": sheet,
                    "id_key": k,
                    "issue": issue
                })
        # --- Step 1: find all globally duplicated id_keys ---
        all_dup_keys = set()
        for sheet_name, df in self.normalized_data.items():
            if "id_key" in df.columns:
                dup_keys = df.loc[df["id_key"].duplicated(), "id_key"].unique()
                if len(dup_keys) > 0:
                    record_mismatches(dup_keys, self.org, self.quarter, sheet_name, "duplicate_in_sheet")
                    all_dup_keys.update(dup_keys)

        # --- Step 2: drop those keys from every sheet before comparing/merging ---
        cleaned_dfs = []
        for sheet_name, df in self.normalized_data.items():
            if "id_key" in df.columns:
                df = df[~df["id_key"].isin(all_dup_keys)].copy()
            cleaned_dfs.append((sheet_name, df))

        # --- Step 3: do matching/missing/extra on the cleaned data ---
        base_name, base_df = cleaned_dfs[0]
        base_df = base_df.rename(columns=lambda c: f"{c}_|_|_{base_name}" if c != "id_key" else c)

        merged = base_df.copy()

        for sheet_name, df in cleaned_dfs[1:]:
            if "id_key" not in df.columns:
                continue

            base_keys = set(merged["id_key"])
            sheet_keys = set(df["id_key"])

            missing_in_sheet = base_keys - sheet_keys
            extra_in_sheet   = sheet_keys - base_keys

            if missing_in_sheet:
                record_mismatches(missing_in_sheet, self.org, self.quarter, sheet_name, "missing_in_sheet")
            if extra_in_sheet:
                record_mismatches(extra_in_sheet, self.org, self.quarter, sheet_name, "extra_in_sheet")

            df = df.rename(columns=lambda c: f"{c}_|_|_{sheet_name}" if c != "id_key" else c)

            ### inner merge is catching any stray single participant entries and removing from the dataset that will be processed
            merged = merged.merge(df, on="id_key", how="inner", suffixes=("", f"_|_|_{sheet_name}"))

        
        DELIM = "_|_|_"

        def split_col(col):
            col = col.replace("_normalized", "")
            
            if DELIM in col:
                base, sheet = col.split(DELIM, 1)
            else:
                base, sheet = col, "combined"

            return base, sheet


        valid_id_keys = set(merged["id_key"])

        id_df_valid = id_df[id_df["id_key"].isin(valid_id_keys)].copy()

        # else: 

        #     # All ids remain valid when mismatch checking is disabled
        #     id_df_valid = id_df.copy()

        #     cleaned_dfs = list(self.normalized_data.items())

        #     if not cleaned_dfs:
        #         merged = pd.DataFrame()
        #     else:
        #         base_name, base_df = cleaned_dfs[0]
        #         merged = base_df.copy()

        #         for sheet_name, df in cleaned_dfs[1:]:

        #             if "id_key" not in df.columns:
        #                 continue

        #             merged = merged.merge(
        #                 df,
        #                 on="id_key",
        #                 how="inner",
        #                 suffixes=("", f"_{sheet_name}")
        #             )

        print(f"{self.org} {workbook_type} - Starting Logging @ {datetime.now()}")

        normalized_combined = merged

        dedup_cols = ["id_key", "First Name", "Last Name", "source_file"]
        mask = normalized_combined.columns.duplicated() & normalized_combined.columns.isin(dedup_cols)
        normalized_combined = normalized_combined.loc[:, ~mask]

        normalized_combined["org"] = self.org
        normalized_combined["period"] = self.quarter
        self.single_sheet = normalized_combined

        if self.logging:

            for kc, colname in keycreators:
                self.single_sheet[colname] = self.single_sheet.apply(kc.create_key_from_row, axis=1)

            person_ids = []

            self.db_logger.load_person_maps()

            for _, row in self.single_sheet.iterrows():
                
                pid = self.db_logger.resolve_person(row) ### checks keys, and resolves match or creates new person as needed
                person_ids.append(pid) ## create list of recognized person ids to be added to participant table 

            self.db_logger.flush_new_people_buffer()

            self.single_sheet["person_id"] = person_ids

            # Create or update dataset entries in the DB

            participant_ids = []

            self.db_logger.load_participant_map(workbook_type, self.org)

            for _, row in self.single_sheet.iterrows():
                pid = row["person_id"]

                participant_id = self.db_logger.get_or_create_participant(
                    person_id=pid,
                    dataset_name=workbook_type,
                    org=self.org
                )

                participant_ids.append(participant_id)
            
            self.db_logger.flush_new_participants()

            self.single_sheet["participant_id"] = participant_ids
            
            self.db_logger.log_all_normalized_cell_values(
                run_id=self.run_id,
                dataset_name=workbook_type,
                df=self.single_sheet
            )

            ### if this is the first run for a given dataset, mark all participants as present. 
            cur = self.db_logger.conn.execute(
                """
                SELECT COUNT(*) 
                FROM participant 
                WHERE dataset_name=? AND org=?
                """,
                (workbook_type, self.org)
            )
            prior_count = cur.fetchone()[0]
            is_first_run = prior_count == 0
            
            row_col = f"row_number_{identity_sheet}_|_|_{identity_sheet}"

            pid_to_row = (
                self.single_sheet
                .set_index("participant_id")[row_col]
                .to_dict()
            )

            seen = set(pid_to_row.keys())

            if is_first_run:
                for pid, row_number in pid_to_row.items():
                    self.db_logger.mark_presence_participant(
                        run_id= self.run_id,
                        participant_id=pid,
                        status="present",
                        row_number=row_number,
                        sheet_name = identity_sheet,
                        quarter = self.quarter
                    )

                self.db_logger.flush_participant_presence()

            else:
                cur = self.db_logger.conn.execute(
                    "SELECT participant_id FROM participant WHERE dataset_name=? AND org=?",
                    (workbook_type, self.org)
                )
                all_ids = [r[0] for r in cur.fetchall()]

                #print(f"There are {len(all_ids)} participant IDs to check presence for.")

                for pid in all_ids:
                    status = "present" if pid in pid_to_row else "missing"
                    row_number = pid_to_row.get(pid)  # None if missing
                    self.db_logger.mark_presence_participant(
                        run_id=self.run_id,
                        participant_id=pid,
                        status=status,
                        row_number=row_number,
                        sheet_name=identity_sheet,
                        quarter=self.quarter
                    )

                self.db_logger.flush_participant_presence()

        if self.mismatches:
            filtered = [
                m for m in self.mismatches
                if m.get("id_key") is not None
            ]

            if filtered and self.logging:
                self.db_logger.log_key_mismatches(
                    run_id= self.run_id,
                    mismatches=filtered
                )

        # normalized_combined = merged

        # dedup_cols = ["id_key", "First Name", "Last Name", "source_file"]
        # mask = normalized_combined.columns.duplicated() & normalized_combined.columns.isin(dedup_cols)
        # normalized_combined = normalized_combined.loc[:, ~mask]

        # normalized_combined["org"] = self.org
        # normalized_combined["period"] = self.quarter
        # self.single_sheet = normalized_combined

        # ============================================================
        # 4️⃣ Apply cross-sheet rules
        # ============================================================
        cross_errs = self._apply_cross_rules(workbook_type=workbook_type, workbook_format=workbook_format, file=file)
        if not cross_errs.empty:
            self.errors.append(cross_errs)
        
        if self.logging and self.errors:

            # Combine all sheet-level + cross-sheet errors into one DF
            err_df = pd.concat(self.errors, ignore_index=True)

            # --------------------------------------------------------
            # Attach participant_id to each error row using id_key
            # --------------------------------------------------------
            if "id_key" in err_df.columns:

                # Build lookup: id_key → participant_id
                id_lookup = (
                    self.single_sheet
                    .dropna(subset=["id_key"])
                    .drop_duplicates(subset=["id_key"], keep="first")
                    .set_index("id_key")["participant_id"]
                )

                # Map onto errors
                err_df["participant_id"] = err_df["id_key"].map(id_lookup)

            else:
                # If id_key missing, participant_id cannot be resolved
                err_df["participant_id"] = None

            # --------------------------------------------------------
            # Persist each violation
            # --------------------------------------------------------
            #print(f"There are {len(err_df)} to log in this run.")
            
            for idx, row in err_df.iterrows():

                rule_name = row.get("rule", "")
                col = row.get("column", "")
                normalized = row.get("normalized", "")
                raw_value = row.get("raw_value", "")
                participant_id = row.get("participant_id")

                severity = "error"   # or dynamic based on rule definition

                column_id = self.db_logger.get_or_create_column(
                    dataset_name = workbook_type, 
                    sheet_name = row.get("sheet"),
                    column_name = col 
                )

                if self.logging: 
                    self.db_logger.log_violation(
                        run_id=self.run_id,
                        rule_id=rule_name,                # optionally: map rule → rule_id
                        participant_id=participant_id,
                        column_id= column_id,               # or your internal column_id
                        normalized=normalized,
                        raw_value=raw_value,
                        severity=severity
                    )

                #print(f"Logging an error for {participant_id} at {col}.")

            self.db_logger.flush_violations()

        if self.logging:

            self.db_logger.complete_run(self.run_id)

    def _apply_cross_rules(self, workbook_type, workbook_format, file=None, row_offset=1):
        
        """
        Apply all configured cross-sheet and cross-column validation rules.

        This method delegates enforcement to `CrossRuleEngine`, which evaluates
        rule objects defined in `self.cross_rules`. Cross-sheet rules compare
        values across multiple sheets (e.g., connected presence, conditional
        requirements, date comparisons, etc.) and generate violations when
        inconsistencies or unmet conditions are detected.

        Args:
            workbook_type (str):
                Dataset family (e.g., "CareerConneCT", "Participant Data").
            workbook_format (str):
                Layout format (e.g., "simple format", "four sheet format").
            file (str, optional):
                Workbook identifier ("org|quarter|filename") used for error lineage.
            row_offset (int, optional):
                Offset applied when converting DataFrame indices to Excel row numbers.
                Passed to the rule engine but typically remains at the default.

        Returns:
            pd.DataFrame:
                Combined DataFrame of all cross-sheet rule violations with columns:
                ["file", "sheet", "row_number", "column", "rule", "raw_value", "normalized"].
                Returns an empty DataFrame with the same schema if no violations occur.

        Behavior:
            • Initializes a `CrossRuleEngine` using the already-normalized sheet data.
            • Iterates through each rule group in `self.cross_rules`
              (e.g., connected presence, conditional blank, conditional required).
            • Executes each rule set and collects all violation DataFrames.
            • Concatenates all violations into a single DataFrame.
            • Marks the engine state as `_cross_checked = True`.

        Notes:
            • Cross rules depend on `self.normalized_data`, which must already be
              produced by `_validate_sheet()` calls in `validate_workbook()`.
            • Missing or empty rule sets are silently skipped.
            • Downstream code (e.g., the logger) attaches `participant_id` after this step.
        """

        # 1️⃣ Initialize the engine
        engine = CrossRuleEngine(
            workbook_type = workbook_type,
            workbook_format = workbook_format,
            normalized_single_sheet= self.single_sheet,
            normalization_schema=self.workbook_definitions,
            file = self.file
        )

        # 2️⃣ Run each rule category through the engine
        all_violations = []

        rule_sets = self.cross_rules

        for label, ruleset in rule_sets:
            if not ruleset:
                continue

            violations = engine.run_all_rules(ruleset)

            if violations is not None and not violations.empty:
                all_violations.append(violations)

        # 3️⃣ Combine all violation DataFrames
        if all_violations:
            combined = pd.concat(all_violations, ignore_index=True)
        
        else:
            combined = pd.DataFrame(
                columns=["file", "sheet", "row_number", "column", "rule", "raw_value", "normalized"]
            )

        self._cross_checked = True
        return combined

    

    def get_all_errors(self):
        """
        Return a single DataFrame containing all accumulated validation errors.

        This method aggregates:
        - Sheet-level column-type validation errors generated during
          `_validate_sheet()`
        - Any cross-sheet rule violations produced by `_apply_cross_rules()`

        Errors are returned in a consistent, flat structure suitable for:
        - Export to Excel/CSV
        - Display in UI dashboards
        - Insertion into logging or auditing pipelines
        - Downstream analytics (e.g., error frequency reports)

        Returns:
            pandas.DataFrame:
                A DataFrame with the standardized columns:
                ["file", "sheet", "row_number", "column", "rule",
                 "raw_value", "normalized"]

                If no errors have been recorded, an empty DataFrame with
                the correct schema is returned.

        Notes:
            • This does *not* modify internal state.
            • Errors remain stored in `self.errors`.
            • Calling this multiple times is inexpensive and safe.
        """
        if not self.errors:
            return pd.DataFrame(columns=["file","sheet","row_number","column","rule","raw_value","normalized"])
        return pd.concat(self.errors, ignore_index=True)

import pandas as pd
from cc_validation_column_types import *
from cc_validation_cross_rules import connected_presence, conditionally_blank_unless, conditionally_required, conditionally_required_by_date_comparison
# from cc_validation_cross_rule_sets import CONNECTED_PRESENCE_RULES, CONDITIONALLY_BLANK_UNLESS_RULES, CONDITIONALLY_ALLOWED_RULES, CONDITIONALLY_REQUIRED_RULES 
from cc_cross_rule_engine import CrossRuleEngine
from cc_validation_cross_rule_sets import CONNECTED_PRESENCE_RULES, CONDITIONALLY_BLANK_UNLESS_RULES, CONDITIONALLY_ALLOWED_RULES, CONDITIONALLY_REQUIRED_RULES , CONDITIONALLY_REQUIRED_BY_DATE_COMPARISON_RULES
## this is a bad way to handle this, should come up with a better way of switching between rule sets, possibly passing them as an argument in main, maybe just consolidating the JSON that captures the tables? 
# from gjc_validation_cross_rule_sets import CONDITIONALLY_REQUIRED_RULES, CONDITIONALLY_REQUIRED_BY_DATE_COMPARISON_RULES, CONNECTED_PRESENCE_RULES, CONDITIONALLY_ALLOWED_RULES, CONDITIONALLY_BLANK_RULES

### SQL Logging Related Imports 
from validation_db_logger import ValidationDBLogger
from hashlib import sha256
import uuid

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

    def __init__(self, workbook_definitions, cross_rules=None, logging = False):
        self.workbook_definitions = workbook_definitions
        self.cross_rules = cross_rules or {}
        self.normalized_data = {}   # {sheet_name: DataFrame}
        self.errors = []            # list of DataFrames
        self._validated = False
        self._cross_checked = False
        self.file = None 
        self.logging = logging 

    def _validate_sheet(self, df, sheet_name, accepted_responses, file=None, row_offset=1):
        
        """
        Run column-type validation on a single sheet.
        Returns normalized DataFrame and error DataFrame.

        """
        normalized_cols = {}
        all_errors = []

        if "id_key" in df.columns:
            normalized_cols["id_key"] = df["id_key"]

        if "row_number" in df.columns:
            normalized_cols["row_number"] = df["row_number"]

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
                row_numbers = df["row_number"])
            elif col_type == "fileSpecificCategorical":
                accepted = spec.get("accepted_responses",[])
                validator = cls(accepted_responses = accepted, 
                required = spec.get("required", False),
                file = self.file.split("|")[0],
                row_numbers = df["row_number"]
                )
            else:
                validator = cls(required=spec.get("required", False), row_numbers = df["row_number"])

            raw = df[col]
            s_norm = validator.normalize(raw)
            s_fmt = validator.format(s_norm)

            errs = validator.errors_df(col, raw, s_norm, file=file, sheet=sheet_name, row_offset=row_offset)    

            if not errs.empty:

                if "id_key" in df.columns:
            
                    errs["id_key"] = df.loc[errs.index, "id_key"].values
            
                all_errors.append(errs)

            normalized_cols[col] = s_fmt

        normalized_df = pd.DataFrame(normalized_cols, index=df.index)

        errors_df = pd.concat(all_errors) if all_errors else pd.DataFrame(
            columns=["file","sheet","row_number","column","rule","raw_value","normalized"]
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
        cols_to_check = [c for c in normalized_df.columns if c not in ["id_key", "row_number"]]
        drop_mask = normalized_df[cols_to_check].isna().all(axis=1)
        dropped_row_numbers = normalized_df.loc[drop_mask, "row_number"].tolist()
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

    ## main function, the one implementing the other functions 
    def validate_workbook(self, file, workbook_type, workbook_format, dfs_by_sheet, keycreators = None):
        """
        Validate all sheets, record entries in database, and apply cross-sheet rules.
        """
        self.file = file
        self.column_error_index = {}

        org = file.split("|")[0] if isinstance(file, str) else ""
        quarter = file.split("|")[1] if isinstance(file, str) else ""

        if self.logging:

            logger = ValidationDBLogger()
            ## create a unique id connected to the information passed in the run table 
            run_id = logger.start_run(workbook_type, org, quarter, triggered_by="mwebb")

        # ============================================================
        # 1️⃣ Sheet-by-sheet validation
        # ============================================================
        for sheet_name, df in dfs_by_sheet.items():
            accepted_responses = self.workbook_definitions[workbook_type][workbook_format][sheet_name]["accepted_responses"]

            norm_df, errs = self._validate_sheet(df, sheet_name, accepted_responses, file=file)

            cols_to_check = [c for c in norm_df.columns if c not in ["id_key", "row_number"]]
            norm_df = norm_df.dropna(subset=cols_to_check, how="all")

            self.normalized_data[sheet_name] = norm_df
            if not errs.empty:
                self.errors.append(errs)

        # ============================================================
        # 2️⃣ Identify canonical participants (from identity sheet)
        # ============================================================
        
        if(workbook_format == "simple format"):
            identity_sheet = "Report"
            id_df = self.normalized_data.get(identity_sheet)
            id_df["id_key"] = (id_df["First Name"].fillna("") + "|" + id_df["Last Name"].fillna(""))
        else: 
            identity_sheet = "Personal Information"
            id_df = self.normalized_data.get(identity_sheet)
        if id_df is None:
            raise ValueError(f"Identity sheet '{identity_sheet}' not found in workbook.")
        
        # Generate spreadsheet specific keys that can be used to map back to a universal person ID

        if self.logging:

            for kc, colname in keycreators:
                id_df[colname] = id_df.apply(kc.create_key_from_row, axis=1)

            person_ids = []

            for idx, row in id_df.iterrows():
                
                pid = logger.resolve_person(row) ### checks keys, and resolves match or creates new person as needed
                person_ids.append(pid) ## create list of recognized person ids to be added to participant table 

            id_df["person_id"] = person_ids

            # Create or update dataset entries in the DB

            participant_ids = []

            for idx, row in id_df.iterrows():
                pid = row["person_id"]

                participant_id = logger.get_or_create_participant(
                    person_id=pid,
                    dataset_name=workbook_type,
                    sheet_name=identity_sheet,
                    org=org,
                    quarter=quarter
                )

                participant_ids.append(participant_id)

            id_df["participant_id"] = participant_ids
            
            logger.log_all_normalized_cell_values(
                run_id=run_id,
                dataset_name=workbook_type,
                normalized_data=self.normalized_data,
                id_df=id_df
            )

            seen = set(id_df["participant_id"].tolist())

            cur = logger.conn.execute(
                "SELECT participant_id FROM participant WHERE dataset_name=? AND org=?",
                (workbook_type, org)
            )

            all_ids = [r[0] for r in cur.fetchall()]

            for pid in all_ids:
                status = "present" if pid in seen else "missing"
                logger.mark_presence_participant(run_id, pid, status)

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
                    id_df
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
            for idx, row in err_df.iterrows():

                rule_name = row.get("rule", "")
                col = row.get("column", "")
                normalized = row.get("normalized", "")
                raw_value = row.get("raw_value", "")
                participant_id = row.get("participant_id")

                severity = "error"   # or dynamic based on rule definition

                logger.log_violation(
                    run_id=run_id,
                    rule_id=rule_name,                # optionally: map rule → rule_id
                    participant_id=participant_id,
                    column_id=col,               # or your internal column_id
                    normalized=normalized,
                    raw_value=raw_value,
                    severity=severity
                )


    def _apply_cross_rules(self, workbook_type, workbook_format, file=None, row_offset=1):
        
        """
        Apply cross-sheet and cross-column validation rules.
        Delegates execution to CrossRuleEngine for consistency.
        """

        # 1️⃣ Initialize the engine
        engine = CrossRuleEngine(
            workbook_type = workbook_type,
            workbook_format = workbook_format,
            dfs_by_sheet=self.normalized_data,
            normalization_schema=self.workbook_definitions,
            file = self.file
        )

        # 2️⃣ Run each rule category through the engine
        all_violations = []

        rule_sets = [
            ("Connected Presence", CONNECTED_PRESENCE_RULES),
            ("Conditionally Blank", CONDITIONALLY_BLANK_UNLESS_RULES),
            ("Conditionally Allowed", CONDITIONALLY_ALLOWED_RULES),
            ("Conditionally Required", CONDITIONALLY_REQUIRED_RULES),
            ("Conditionally Required by Date", CONDITIONALLY_REQUIRED_BY_DATE_COMPARISON_RULES),
        ]

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
        """Return one combined DataFrame of all errors so far."""
        if not self.errors:
            return pd.DataFrame(columns=["file","sheet","row_number","column","rule","raw_value","normalized"])
        return pd.concat(self.errors, ignore_index=True)

    @staticmethod
    def make_entry_key(row):
        """
        Create a stable, deterministic hash ID for a dataset entry based on
        identifying columns. Adjust as needed per workbook type.
        """
        parts = [
            str(row.get("Client Date of Birth") or "").strip(),
            str(row.get("First Name") or "").strip().lower(),
            str(row.get("Last Name") or "").strip().lower(),
        ]
        base = "||".join(parts)
        return sha256(base.encode()).hexdigest()
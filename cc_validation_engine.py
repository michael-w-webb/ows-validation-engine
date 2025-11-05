import pandas as pd
from cc_validation_column_types import *
from cc_validation_cross_rules import connected_presence, conditionally_blank, conditionally_allowed, conditionally_required, conditionally_required_by_date_comparison
from cc_validation_cross_rule_sets import CONNECTED_PRESENCE_RULES, CONDITIONALLY_BLANK_RULES, CONDITIONALLY_ALLOWED_RULES, CONDITIONALLY_REQUIRED_RULES 
## this is a bad way to handle this, should come up with a better way of switching between rule sets, possibly passing them as an argument in main 
# from gjc_validation_cross_rule_sets import CONDITIONALLY_REQUIRED_RULES, CONDITIONALLY_REQUIRED_BY_DATE_COMPARISON_RULES, CONNECTED_PRESENCE_RULES, CONDITIONALLY_ALLOWED_RULES, CONDITIONALLY_BLANK_RULES

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

    def __init__(self, workbook_definitions, cross_rules=None):
        self.workbook_definitions = workbook_definitions
        self.cross_rules = cross_rules or {}
        self.normalized_data = {}   # {sheet_name: DataFrame}
        self.errors = []            # list of DataFrames
        self._validated = False
        self._cross_checked = False
        self.file = None 

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
                all_errors.append(errs)

            normalized_cols[col] = s_fmt

        normalized_df = pd.DataFrame(normalized_cols, index=df.index)
        errors_df = pd.concat(all_errors) if all_errors else pd.DataFrame(
            columns=["file","sheet","row_number","column","rule","raw_value","normalized"]
        )

                # --- 🧹 Clean normalized data before returning ---
        normalized_df = normalized_df.replace(r"^\s*$", pd.NA, regex=True)    # empty or whitespace-only
        normalized_df = normalized_df.replace(r"^0+$", pd.NA, regex=True)     # "0", "00", etc.
        normalized_df = normalized_df.replace(
            to_replace=[
                "#VALUE!", "#REF!", "#DIV/0!", "#NAME?", "#NULL!", "#NUM!",
                "#N/A", "nan", "<NA>", "NaN"
            ],
            value=pd.NA
        )

        # Drop rows that are all blank except id_key/row_number
        cols_to_check = [c for c in normalized_df.columns if c not in ["id_key", "row_number"]]
        drop_mask = normalized_df[cols_to_check].isna().all(axis=1)
        dropped_row_numbers = normalized_df.loc[drop_mask, "row_number"].tolist()
        normalized_df = normalized_df.loc[~drop_mask].copy()

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
    def validate_workbook(self, file, workbook_type, workbook_format, dfs_by_sheet):
        """
        Validate all sheets in a workbook (dict: {sheet_name: df}).
        Stores normalized data and errors, then applies cross-rules.
        """
        self.file = file 
        self.column_error_index = {}

        for sheet_name, df in dfs_by_sheet.items():

            accepted_responses = self.workbook_definitions[workbook_type][workbook_format][sheet_name]["accepted_responses"]

            norm_df, errs = self._validate_sheet(
                df, sheet_name, accepted_responses, file=file
            )

            norm_df = norm_df.replace(r"^\s*$", pd.NA, regex=True)    # empty or whitespace-only cells
            norm_df = norm_df.replace(r"^0+$", pd.NA, regex=True)     # "0", "00", "000"
            norm_df = norm_df.replace(
                to_replace=[
                    "#VALUE!", "#REF!", "#DIV/0!", "#NAME?", "#NULL!", "#NUM!", "#N/A","nan", "<NA>","NaN"
                ],
                value=pd.NA
            )
            cols_to_check = [c for c in norm_df.columns if c not in ["id_key", "row_number"]]
            norm_df = norm_df.dropna(subset=cols_to_check, how="all")   


            self.normalized_data[sheet_name] = norm_df
            if not errs.empty:
                self.errors.append(errs)

            # 🔹 After sheet-level validation, apply cross rules
        cross_errs = self._apply_cross_rules(file=file)
        if not cross_errs.empty:
            self.errors.append(cross_errs)

    def _apply_cross_rules(self, file=None, row_offset=1):
        """
        Apply cross-rules. Each rule specifies sheet_x/sheet_y and col_x/col_y.
        """
        errors = []

        # Connected Presence
        for rule in CONNECTED_PRESENCE_RULES:
            df_x = self.normalized_data.get(rule["sheet_x"])
            df_y = self.normalized_data.get(rule["sheet_y"])
            if df_x is None or df_y is None:
                continue

            errs = connected_presence(
                {rule["sheet_x"]: df_x, rule["sheet_y"]: df_y},
                sheet_x=rule["sheet_x"], col_x=rule["col_x"],
                sheet_y=rule["sheet_y"], col_y=rule["col_y"],
                file=file, row_offset=row_offset, column_error_index= getattr(self, "column_error_index", None)
            )
            if not errs.empty:
                errors.append(errs)

        # Conditionally Blank
        for rule in CONDITIONALLY_BLANK_RULES:
            df_x = self.normalized_data.get(rule["sheet_x"])
            df_y = self.normalized_data.get(rule["sheet_y"])
            if df_x is None or df_y is None:
                continue

            errs = conditionally_blank(
                {rule["sheet_x"]: df_x, rule["sheet_y"]: df_y},
                sheet_x=rule["sheet_x"], col_x=rule["col_x"],
                sheet_y=rule["sheet_y"], col_y=rule["col_y"],
                file=file, row_offset=row_offset, column_error_index= getattr(self, "column_error_index", None)
            )
            if not errs.empty:
                errors.append(errs)

        # Conditionally Allowed
        for rule in CONDITIONALLY_ALLOWED_RULES:
            df_x = self.normalized_data.get(rule["sheet_x"])
            df_y = self.normalized_data.get(rule["sheet_y"])
            if df_x is None or df_y is None:
                continue

            errs = conditionally_allowed(
                {rule["sheet_x"]: df_x, rule["sheet_y"]: df_y},
                sheet_x=rule["sheet_x"], col_x=rule["col_x"],
                sheet_y=rule["sheet_y"], col_y=rule["col_y"],
                trigger_values=rule["trigger_values"],
                file=file, row_offset=row_offset, column_error_index= getattr(self, "column_error_index", None)
            )
            if not errs.empty:
                errors.append(errs)

        # --- Conditionally Required (Value-, Trigger-, or Presence-based) ---
        for rule in CONDITIONALLY_REQUIRED_RULES:
            # Collect all sheets mentioned in the rule
            needed_sheets = {s for s, _ in (rule["if_pairs"] + rule["then_pairs"])}

            # Pull them from normalized_data
            dfs_subset = {s: self.normalized_data.get(s) for s in needed_sheets}
            if any(df is None for df in dfs_subset.values()):
                continue  # skip if any required sheet not available

            errs = conditionally_required(
                dfs_by_sheet=dfs_subset,
                if_pairs=rule["if_pairs"],
                then_pairs=rule["then_pairs"],
                trigger_values=rule.get("trigger_values"),  # ✅ handles both global or per-column triggers
                file=file,
                row_offset=row_offset,
                column_error_index=getattr(self, "column_error_index", None),
            )
            if not errs.empty:
                errors.append(errs)

            # --- Conditionally Required by Date Comparison ---
        for rule in CONDITIONALLY_REQUIRED_BY_DATE_COMPARISON_RULES:
            # Collect all sheets mentioned in the rule
            needed_sheets = {s for s, _ in (rule["if_pairs"] + rule["then_pairs"])}

            # Pull them from normalized_data
            dfs_subset = {s: self.normalized_data.get(s) for s in needed_sheets}
            if any(df is None for df in dfs_subset.values()):
                continue  # skip if any required sheet not available

            errs = conditionally_required_by_date_comparison(
                dfs_by_sheet=dfs_subset,
                if_pairs=rule["if_pairs"],
                then_pairs=rule["then_pairs"],
                relation=rule.get("relation", "after"),        # "before" or "after"
                reference_date=rule.get("reference_date"),     # optional static date (e.g. quarter end)
                file=file,
                row_offset=row_offset,
                column_error_index=getattr(self, "column_error_index", None),
            )

            if not errs.empty:
                errors.append(errs)


        self._cross_checked = True

        return pd.concat(errors) if errors else pd.DataFrame(
            columns=["file", "sheet", "row_number", "column", "rule", "raw_value", "normalized"]
        )
    
    

    def get_all_errors(self):
        """Return one combined DataFrame of all errors so far."""
        if not self.errors:
            return pd.DataFrame(columns=["file","sheet","row_number","column","rule","raw_value","normalized"])
        return pd.concat(self.errors, ignore_index=True)

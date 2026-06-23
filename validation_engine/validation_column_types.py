"""
Column validation and normalization framework.

This module defines reusable column-validator classes used to standardize,
validate, and format structured tabular data originating from Excel-based
workforce and training-provider reporting systems.

The validators are designed for high-variability real-world datasets where
values may contain:
    • inconsistent formatting
    • spreadsheet export artifacts
    • mixed data types
    • malformed categorical responses
    • placeholder or junk values
    • organization-specific conventions

Core Responsibilities
---------------------
Each validator is responsible for some combination of:

    • normalization
        Converting messy raw values into canonical internal representations.

    • validation
        Applying type- and domain-specific validation rules.

    • formatting
        Converting normalized values into standardized output forms.

    • error reporting
        Producing structured row-level validation metadata suitable for
        QA workflows, audit reporting, and downstream review interfaces.

Validation Workflow
-------------------
Most validators follow a common lifecycle:

    1. base_clean()
        Shared low-level preprocessing such as whitespace cleanup and
        normalization of spreadsheet error tokens.

    2. normalize()
        Type-specific parsing and canonicalization logic.

    3. format()
        Optional output formatting or presentation normalization.

    4. errors_df()
        Structured validation-error generation.

Validator Types
---------------
Included validators support a range of common workforce-reporting fields,
including:

    • categorical responses
    • booleans
    • dates
    • ZIP codes
    • State IDs
    • O*NET occupation codes
    • NAICS industry codes
    • hourly wages
    • hours-worked values

Design Notes
------------
The framework prioritizes:
    • deterministic normalization behavior
    • explicit handling of malformed data
    • transparent validation logic
    • spreadsheet-oriented reporting compatibility
    • vectorized pandas operations where practical

These validators are primarily intended for structured reporting pipelines
rather than permissive end-user form validation systems.
"""

import pandas as pd 
from rapidfuzz import process, fuzz
import re
import unicodedata 

class BaseColumn:

    """
    Base class for all column-type validators.

    Provides shared cleaning logic used across specific column types
    (categorical, identifier, numeric, etc.). The cleaning step normalizes
    whitespace, converts common Excel error tokens to `pd.NA`, and ensures
    column values are handled as pandas `"string"` dtype.

    Attributes:
        ERROR_TOKENS (set[str]):
            Common spreadsheet error literals and representations of null
            that should be treated as missing values.
    """
    
    ERROR_TOKENS =  {"#VALUE!","#REF!","#DIV/0!","#NAME?","#NULL!","#NUM!","#N/A",
        "nan","<NA>","NaN","null"}
    
    def base_clean(self, s: pd.Series) -> pd.Series:
        """
        Apply shared low-level cleaning used by all column validators.

        This method standardizes missing-value handling and performs lightweight
        string normalization before type-specific parsing or validation logic is
        applied.

        Cleaning steps:
            1. Convert values to pandas `"string"` dtype
            2. Strip leading and trailing whitespace
            3. Replace empty or whitespace-only values with `pd.NA`
            4. Replace known spreadsheet error tokens and null-like literals
            (e.g. "#VALUE!", "NaN", "<NA>") with `pd.NA`

        Args:
            s (pd.Series):
                Raw column values.

        Returns:
            pd.Series:
                Cleaned Series with standardized missing-value representation.
        """
        s = s.astype("string")
        s = s.str.strip().replace("", pd.NA)
        s = s.replace(r"^\s*$", pd.NA, regex=True)
        s = s.replace(self.ERROR_TOKENS, pd.NA)
        return s
    
    def errors_df(self):
        """
        Construct a standardized validation-error DataFrame.

        Subclasses implement column-specific validation logic and return
        row-level error metadata using a consistent schema.

        Expected output columns:
            [
                "file",
                "sheet",
                "row_number",
                "column",
                "rule",
                "raw_value",
                "normalized"
            ]

        Returns:
            pd.DataFrame:
                Validation errors for the column. Implementations should return
                an empty DataFrame with the standard schema when no errors exist.
        """

    def _clean(self):
        """
        Normalize a raw value into a canonical representation suitable for
        comparison and downstream validation logic.

        Subclasses implement type-specific cleaning behavior. Typical operations
        may include whitespace normalization, case normalization, formatting
        cleanup, or conversion of placeholder values to missing representations.

        Args:
            text:
                Raw input value.

        Returns:
            str:
                Cleaned canonical representation of the value.
        """
    
    def normalize(self, s: pd.Series) -> pd.Series:
        """
        Normalize raw column values into a standardized representation suitable
        for validation and downstream processing.

        Subclasses implement type-specific normalization behavior. Implementations
        typically apply shared base cleaning followed by transformations such as
        parsing, coercion, canonical mapping, or formatting standardization.

        Args:
            s (pd.Series):
                Raw column values as read from the source file.

        Returns:
            pd.Series:
                Normalized column values. Values that cannot be meaningfully
                interpreted should generally be represented as `pd.NA`.
        """
class categoricalColumn(BaseColumn):

    """
    Validator for constrained categorical fields.

    This column type normalizes free-text categorical responses into
    canonical accepted values using exact and optional fuzzy matching.

    Accepted responses may be provided as:
        • list[str]:
            Literal accepted values.
        • dict[str, list[str]]:
            Canonical value mapped to alternative spellings or variants.

    Behavior:
        • Applies shared base cleaning from `BaseColumn`
        • Normalizes whitespace and casing
        • Maps cleaned values to canonical accepted responses
        • Optionally applies fuzzy matching for near matches
        • Produces standardized row-level validation errors

    Attributes:
        required (bool):
            Whether missing values should be treated as validation errors.
        fuzzy (bool):
            Whether fuzzy matching is enabled for unmatched values.
        min_score (int):
            Minimum fuzzy-match score required for acceptance.
        accepted (dict[str, str]):
            Mapping of cleaned input values to canonical labels.
        row_numbers (pd.Series | None):
            Row references used in validation error reporting.
    """


    def __init__(self, accepted_responses: list[str], required: bool = False,
                 fuzzy: bool = True, min_score: int = 90, row_numbers = None):
        """
        Initialize a categorical column validator.

        Args:
            accepted_responses (list[str] or dict[str, list[str]]):
                Allowed categorical values. Dictionaries allow grouping variants
                under a canonical label.
            required (bool):
                Whether missing or blank values should trigger a validation error.
            fuzzy (bool):
                Enable fuzzy matching for values that do not match accepted responses.
            min_score (int):
                Minimum fuzzy match threshold (0–100) for accepting a match.
            row_numbers (pd.Series or None):
                Row numbers for error reporting; typically derived from the workbook loader.
        """

        self.required = required
        # retiring this to add flexibility for dict or list 
        # self.accepted = {r.casefold().strip(): r for r in accepted_responses}
        self.fuzzy = fuzzy
        self.min_score = min_score
        self._whitespace = re.compile(r"\s+")
        self.row_numbers = row_numbers

        self.accepted = {}
        if isinstance(accepted_responses, dict):
            for canonical, variants in accepted_responses.items():
                all_forms = [canonical] + variants
                for v in all_forms:
                    self.accepted[self._clean(v)] = canonical
        else:
            self.accepted = {self._clean(r): r for r in accepted_responses}

    def _clean(self, text):

        """
        Apply categorical-specific text normalization used for value matching.

        This helper standardizes categorical values into a canonical comparison
        form after shared preprocessing from `base_clean()`.

        Cleaning behavior includes:
            • stripping leading/trailing whitespace
            • collapsing repeated internal whitespace
            • converting numeric float strings such as "1.0" to "1"
            • treating sequences of zeros as missing
            • case-insensitive normalization via `casefold()`

        Args:
            text:
                Raw categorical value.

        Returns:
            str:
                Canonical comparison value used for exact and fuzzy matching.
                Missing values are returned as an empty string.
        """

        if text is None or pd.isna(text):
            return ""

        text = str(text).strip()

        # If numeric float like 1.0 → convert to integer string
        if re.fullmatch(r"\d+\.0+", text):
            text = text.split(".")[0]

        # Treat sequences of zeros as missing
        if re.fullmatch(r"0+", text):
            return ""

        return self._whitespace.sub(" ", text).strip().casefold()
    
    # --- normalize ---
    def normalize(self, s: pd.Series) -> pd.Series:
        
        """
        Normalize categorical values into canonical accepted responses.

        Processing steps:
            1. Apply shared preprocessing via `base_clean()`
            2. Apply categorical-specific normalization via `_clean()`
            3. Perform exact matching against accepted responses
            4. Optionally apply fuzzy matching for unmatched values

        Args:
            s (pd.Series):
                Raw categorical values.

        Returns:
            pd.Series:
                Canonical categorical values or `pd.NA` for values that
                cannot be matched or interpreted.
        """

        s = s.astype("string")     
        raw = s
        ### handle excel errors / explicit nans sent to string 
        cleaned = self.base_clean(s)
        # Apply cleaning to each value
        cleaned = cleaned.map(self._clean)

        # Direct matches first (cleaned to canonical)
        mapped = cleaned.map(self.accepted)

        # Fuzzy match for unmapped values
        if self.fuzzy:
            missing = mapped.isna() & raw.notna()
            uniq_missing = raw[missing].unique()
            for val in uniq_missing:
                clean_val = self._clean(val)
                match = process.extractOne(
                    clean_val,
                    list(self.accepted.keys()),
                    scorer=fuzz.token_sort_ratio
                )
                if match and match[1] >= self.min_score:
                    mapped.loc[cleaned == clean_val] = match[0]

        return mapped


    # --- format (just return canonical string) ---
    def format(self, s_norm: pd.Series) -> pd.Series:
        """Return canonical categorical values unchanged."""
        return s_norm

    # --- errors ---
    def errors_df(self, col: str, raw: pd.Series, s_norm: pd.Series,
                  file=None, sheet=None, row_offset: int = 1) -> pd.DataFrame:

        """
        Construct validation errors for categorical values.

        Error rules:
            • "Required but missing"
                Missing value in a required field.
            • "Invalid Value, not in accepted responses"
                Value could not be mapped to an accepted categorical response.

        Args:
            col (str):
                Column name being validated.
            raw (pd.Series):
                Original unnormalized values.
            s_norm (pd.Series):
                Normalized categorical values.
            file (str | None):
                Optional source file identifier.
            sheet (str | None):
                Optional sheet or dataset section name.
            row_offset (int):
                Offset used when deriving row numbers from the index.

        Returns:
            pd.DataFrame:
                Structured categorical validation errors.
        """

        masks = {
            "Required but missing": (
                s_norm.isna() if self.required else pd.Series(False, index=s_norm.index)
            ),
            "Invalid Value, not in accepted responses": (
                raw.notna() & s_norm.isna()
            ),
        }

        frames = []
        for rule, mask in masks.items():
            idx = raw.index[mask.fillna(False)]
            if len(idx) == 0:
                continue
            frames.append(pd.DataFrame({
                "file": file,
                "sheet": sheet,
                "row_number": (
                self.row_numbers.loc[idx].values   # <-- use self.row_numbers
                if self.row_numbers is not None
                else idx.to_series().add(row_offset).values
            ),
                "column": col,
                "rule": rule,
                "raw_value": raw.loc[idx].astype("string").values,
                "normalized": s_norm.loc[idx].astype("string").values,
            }, index=idx))

        return pd.concat(frames) if frames else pd.DataFrame(
            columns=["file","sheet","row_number","column","rule","raw_value","normalized"]
        )

class fileSpecificCategoricalColumn(BaseColumn):
    """
    Validator for categorical fields whose accepted responses vary by file
    or source organization.

    This column type selects a file-specific accepted-response mapping and
    normalizes raw categorical values into canonical labels using exact and
    optional fuzzy matching.

    Expected accepted-response structure:
        {
            "FILE_A": {
                "Canonical Value": ["variant1", "variant2"]
            }
        }

    Behavior:
        • Applies shared preprocessing via `base_clean()`
        • Applies categorical-specific normalization via `_clean()`
        • Selects accepted responses using `self.file`
        • Performs exact and optional fuzzy matching
        • Produces standardized validation errors

    Attributes:
        accepted_responses (dict):
            File-specific accepted categorical mappings.
        required (bool):
            Whether missing values should generate validation errors.
        fuzzy (bool):
            Whether fuzzy matching is enabled.
        min_score (int):
            Minimum fuzzy-match score required for acceptance.
        row_numbers (pd.Series | None):
            Row references used in validation reporting.
        file (str | None):
            File identifier used to select the accepted-response mapping.
    """
    def __init__(self, accepted_responses: dict, required: bool = False,
                 fuzzy: bool = True, min_score: int = 90, row_numbers=None, file = None):
        self.accepted_responses = accepted_responses
        self.required = required
        self.fuzzy = fuzzy
        self.min_score = min_score
        self.row_numbers = row_numbers
        self._whitespace = re.compile(r"\s+")
        self.file = file

    def _clean(self, text: str) -> str:
        """
        Normalize categorical values into a canonical comparison form.

        Cleaning behavior includes whitespace normalization, case normalization,
        and treatment of zero-only values as missing.

        Args:
            text (str):
                Raw categorical value.

        Returns:
            str:
                Canonical comparison value used for matching.
        """
        if pd.isna(text):
            return ""
        if re.fullmatch(r"0+", text):
            return ""
        return self._whitespace.sub(" ", str(text)).strip().casefold()

    def normalize(self, s: pd.Series) -> pd.Series:
        """
        Normalize categorical values using file-specific accepted responses.

        Processing steps:
            1. Select the accepted-response mapping for `self.file`
            2. Apply shared preprocessing via `base_clean()`
            3. Apply categorical-specific normalization via `_clean()`
            4. Perform exact matching
            5. Optionally apply fuzzy matching for unmatched values

        Args:
            s (pd.Series):
                Raw categorical values.

        Returns:
            pd.Series:
                Canonical categorical values or `pd.NA` for unmatched values.

        Raises:
            ValueError:
                If `self.file` does not exist in `accepted_responses`.
        """

        if self.file not in self.accepted_responses:
            raise ValueError(f"❌ file_id '{self.file}' not found in accepted_responses")

        # Build reverse lookup: variant -> canonical
        file_map = self.accepted_responses[self.file]
        reverse_map = {}
        for canonical, variants in file_map.items():
            for v in variants:
                reverse_map[self._clean(v)] = canonical

        raw = s.astype("string")
        ## handle excel errors / explicit nans sent to string
        cleaned = self.base_clean(s)
        cleaned = raw.map(self._clean)
        mapped = cleaned.map(reverse_map)

        # Fuzzy matching (optional)
        if self.fuzzy:
            missing = mapped.isna() & raw.notna()
            uniq_missing = raw[missing].dropna().unique()
            for val in uniq_missing:
                clean_val = self._clean(val)
                match = process.extractOne(
                    clean_val, list(reverse_map.keys()), scorer=fuzz.token_sort_ratio
                )
                if match and match[1] >= self.min_score:
                    mapped.loc[cleaned == clean_val] = reverse_map[match[0]]

        return mapped

    def format(self, s_norm: pd.Series) -> pd.Series:
        """Return canonical string (no formatting change)."""
        return s_norm

    def errors_df(self, col: str, raw: pd.Series, s_norm: pd.Series,
                  file=None, sheet=None, row_offset: int = 1) -> pd.DataFrame:
        """
        Construct validation errors for file-specific categorical values.

        Error rules:
            • "Required but missing"
                Missing value in a required field.
            • "Invalid Value, not in accepted responses"
                Value could not be matched to a valid file-specific response.

        Returns:
            pd.DataFrame:
                Structured categorical validation errors.
        """
        masks = {
            "Required but missing": (
                s_norm.isna() if self.required else pd.Series(False, index=s_norm.index)
            ),
            "Invalid Value, not in accepted responses": (
                raw.notna() & s_norm.isna()
            ),
        }

        frames = []
        for rule, mask in masks.items():
            idx = raw.index[mask.fillna(False)]
            if len(idx) == 0:
                continue
            frames.append(pd.DataFrame({
                "file": file,
                "sheet": sheet,
                "row_number": (
                    self.row_numbers.loc[idx].values
                    if self.row_numbers is not None
                    else idx.to_series().add(row_offset).values
                ),
                "column": col,
                "rule": rule,
                "raw_value": raw.loc[idx].astype("string").values,
                "normalized": s_norm.loc[idx].astype("string").values,
            }, index=idx))

        return pd.concat(frames) if frames else pd.DataFrame(
            columns=["file", "sheet", "row_number", "column", "rule", "raw_value", "normalized"]
        )
 
class identifierColumn(BaseColumn):
    """
    Column type for free-text identifiers such as student IDs, intake IDs,
    or internal tracking numbers.

    This validator performs minimal structural cleaning—primarily whitespace
    normalization and basic sanity checks—while preserving the original content
    as much as possible. Identifiers differ from categorical values in that
    they are not validated against an allowed set, but may still be required
    or rejected if malformed.

    Behavior:
        • Applies BaseColumn cleaning to remove Excel error tokens and convert
          blank/whitespace-only entries into `pd.NA`.
        • Lowercases text (`casefold`) for consistent internal representation.
        • Collapses internal whitespace into a single space.
        • Treats digit-only strings such as "0", "00", "000" as missing.
        • Produces two classes of errors:
            - "Required but missing"
            - "Formatting Issue, identifier rejected" (non-missing raw → NA after normalization)

    Args:
        required (bool, optional):
            If True, missing or empty identifiers generate a validation error.
        row_numbers (pd.Series, optional):
            Excel-based row references used in error reporting.

    Returns:
        This class does not return directly; its methods produce either normalized
        Series or structured error DataFrames (see below).

    normalize(s):
        • Input:
            s (pd.Series): Raw identifier values from the sheet.
        • Output:
            pd.Series of cleaned identifier strings or `pd.NA`.

    format(s_norm):
        • Identifiers require no additional formatting; returned unchanged.

    errors_df(col, raw, s_norm, file, sheet, row_offset):
        • Constructs a structured error DataFrame with columns:
            ["file", "sheet", "row_number", "column",
             "rule", "raw_value", "normalized"]
        • Includes row-level metadata via `row_numbers` or `row_offset`.

    Side Effects:
        • None, except the use of `row_numbers` for error positioning.

    Notes:
        • identifierColumn performs lightweight, non-destructive cleaning.
        • No fuzzy matching or cross-reference validation is applied.
        • Ideal for fields where exact text is meaningful but basic sanitation
          is still required.
    """

    name: str = "identifier"

    def __init__(self, required: bool = False, row_numbers=None):
        self.required = required
        self._whitespace = re.compile(r"\s+")
        self.row_numbers = row_numbers

    # --- normalize ---
    def normalize(self, s: pd.Series) -> pd.Series:
        
        s = self.base_clean(s)
        s = s.astype("string").str.strip()
        s = s.str.casefold().str.replace(self._whitespace, " ", regex=True)
        s = s.mask(s.str.fullmatch(r"0+"), pd.NA)
        # Treat empty or whitespace-only as missing
        return s.replace("", pd.NA)

    # --- format (normalized is final) ---
    def format(self, s_norm: pd.Series) -> pd.Series:
        return s_norm

    # --- errors ---
    def errors_df(self, col: str, raw: pd.Series, s_norm: pd.Series,
                  file=None, sheet=None, row_offset: int = 1) -> pd.DataFrame:

        # Define missing in raw input (after stripping)
        raw_missing = raw.astype("string").str.strip().replace("", pd.NA).isna()

        # Build masks
        masks = {
            # If required and missing → flag as required missing
            "Required but missing": (
                self.required & s_norm.isna()
            ),
            # If normalized NA but not due to missing raw → formatting problem
            "Formatting Issue, identifier rejected": (
                s_norm.isna() & ~raw_missing & ~self.required  # exclude blanks and required-missing
            ),
        }

        frames = []
        for rule, mask in masks.items():
            idx = raw.index[mask.fillna(False)]
            if len(idx) == 0:
                continue

            frames.append(pd.DataFrame({
                "file": file,
                "sheet": sheet,
                "row_number": (
                    self.row_numbers.loc[idx].values
                    if self.row_numbers is not None
                    else idx.to_series().add(row_offset).values
                ),
                "column": col,
                "rule": rule,
                "raw_value": raw.loc[idx].astype("string").values,
                "normalized": s_norm.loc[idx].astype("string").values,
            }, index=idx))

        return pd.concat(frames) if frames else pd.DataFrame(
            columns=["file", "sheet", "row_number", "column", "rule", "raw_value", "normalized"]
        )

class booleanColumn(BaseColumn): 

    """
    Validator for boolean-like categorical fields.

    This column type normalizes common yes/no representations into canonical
    boolean categories.

    Accepted representations include:
        • yes / no
        • y / n
        • true / false
        • 1 / 0
        • numeric float equivalents such as 1.0 / 0.0

    Behavior:
        • Applies shared preprocessing via `base_clean()`
        • Normalizes numeric-like values before string conversion
        • Maps accepted variants to canonical "Yes" / "No" values
        • Produces standardized validation errors for invalid entries

    Attributes:
        required (bool):
            Whether missing values should generate validation errors.
        accepted (dict[str, str]):
            Mapping of accepted boolean variants to canonical values.
        row_numbers (pd.Series | None):
            Row references used in validation reporting.
    """

    name: str = "boolean"

    def __init__(self, 
                 required: bool = False, row_numbers = None):
        
        self.required = required
        self.accepted = {
            "yes": "Yes", "y": "Yes", "true": "Yes", "1": "Yes", "1.0" : "Yes",
            "no": "No", "n": "No", "false": "No", "0": "No", "0.0" : "No"
        }
        self.row_numbers = row_numbers

    def normalize(self, s: pd.Series) -> pd.Series:

        """
        Normalize boolean-like values into canonical "Yes" / "No" labels.

        Processing steps:
            1. Apply shared preprocessing via `base_clean()`
            2. Normalize numeric values such as `1.0` → `1`
            3. Standardize casing and whitespace
            4. Map accepted variants to canonical boolean labels

        Args:
            s (pd.Series):
                Raw boolean-like values.

        Returns:
            pd.Series:
                Canonical "Yes" / "No" values or `pd.NA` for invalid
                or unrecognized entries.
        """

        s = self.base_clean(s)

        # --- NEW: normalize numeric-like values ---
        def clean_numeric(x):
            if pd.isna(x):
                return x
            if isinstance(x, (int, float)):
                return int(x)  # 1.0 -> 1
            return x

        s = s.map(clean_numeric)

        # now proceed as before
        s = s.astype("string").str.strip().str.lower()

        mapped = s.map(self.accepted)

        return mapped
    
    def format(self, s_norm: pd.Series) -> pd.Series:
        """
        Format canonical boolean values as nullable integer indicators.

        Canonical values are converted as follows:
            • "Yes" → 1
            • "No"  → 0

        Missing values are preserved using pandas nullable integer dtype
        (`Int64`).

        Args:
            s_norm (pd.Series):
                Normalized boolean values.

        Returns:
            pd.Series:
                Nullable integer representation of boolean values.
        """
        return(
            s_norm.map({"Yes":1, "No":0}).astype("Int64")
        )
    
    def errors_df(self, col: str, raw: pd.Series, s_norm: pd.Series,
                  file=None, sheet=None, row_offset: int = 1) -> pd.DataFrame:
        """
        Construct validation errors for boolean-like values.

        Error rules:
            • "Required but missing"
                Missing value in a required field.
            • "Invalid Value, must be Yes/No"
                Value could not be interpreted as a recognized boolean variant.

        Args:
            col (str):
                Column name being validated.
            raw (pd.Series):
                Original unnormalized values.
            s_norm (pd.Series):
                Normalized boolean values.
            file (str | None):
                Optional source file identifier.
            sheet (str | None):
                Optional sheet or dataset section name.
            row_offset (int):
                Offset used when deriving row numbers from the index.

        Returns:
            pd.DataFrame:
                Structured boolean validation errors.
        """

        masks = {
            "Required but missing": (
                s_norm.isna() if self.required else pd.Series(False, index=s_norm.index)
            ),
            "Invalid Value, must be Yes/No": (
                raw.notna() & s_norm.isna()  # had a value but it didn’t map
            ),
        }

        frames = []
        for rule, mask in masks.items():
            idx = raw.index[mask.fillna(False)]
            if len(idx) == 0:
                continue
            frames.append(pd.DataFrame({
                "file": file,
                "sheet": sheet,
                "row_number": (
                self.row_numbers.loc[idx].values   # <-- use self.row_numbers
                if self.row_numbers is not None
                else idx.to_series().add(row_offset).values
            ),
                "column": col,
                "rule": rule,
                "raw_value": raw.loc[idx].astype("string").values,
                "normalized": s_norm.loc[idx].astype("string").values,
            }, index=idx))

        return pd.concat(frames) if frames else pd.DataFrame(
            columns=["file","sheet","row_number","column","rule","raw_value","normalized"]
        )
    
class dateTimeColumn(BaseColumn): 

    """
    Validator for date and datetime fields.

    This column type normalizes a wide variety of real-world date formats
    into pandas datetime values and validates them against optional minimum
    and maximum bounds.

    Supported behaviors include:
        • normalization of inconsistent separators and unicode characters
        • handling of month names and mixed formatting styles
        • recovery from partially malformed date strings
        • coercion of invalid or placeholder values to missing values
        • validation against configurable date ranges

    Behavior:
        • Applies shared preprocessing via `base_clean()`
        • Applies date-specific text normalization via `_clean_text()`
        • Parses cleaned values using `pd.to_datetime()`
        • Produces standardized validation errors for:
            - missing required values
            - invalid dates
            - out-of-range dates

    Attributes:
        required (bool):
            Whether missing values should generate validation errors.
        min_date (pd.Timestamp | None):
            Minimum allowed date.
        max_date (pd.Timestamp | None):
            Maximum allowed date.
        row_numbers (pd.Series | None):
            Row references used in validation reporting.
    """

    name: str = "date_time"
    
    def __init__(self, 
                 required: bool = False, 
                 min_date: str| None = "1900-01-01", 
                 max_date: str|None = "2100-12-31",
                 row_numbers = None):

        self.required = required 
        self.min_date = pd.to_datetime(min_date) if min_date else None
        self.max_date = pd.to_datetime(max_date) if max_date else None
        self.row_numbers = row_numbers

        # Allowed month names/abbreviations
        self.month_pattern = re.compile(
            r"\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
            r"jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|"
            r"nov(?:ember)?|dec(?:ember)?)\b",
            flags=re.IGNORECASE
        )

    
    def _clean_text(self, val: str):
        """
        Normalize irregular date text into a parseable date representation.

        Cleaning behavior includes:
            • unicode normalization
            • separator normalization
            • removal of invisible/control characters
            • preservation of recognized month names
            • extraction of common ISO and U.S. date patterns

        The method attempts to recover usable date strings from malformed
        or inconsistently formatted inputs prior to datetime parsing.

        Args:
            val (str):
                Raw date value.

        Returns:
            str | pd.NA:
                Cleaned date string suitable for parsing, or `pd.NA`
                if no valid date structure can be identified.
        """
        if pd.isna(val):
            return pd.NA

        val = str(val).strip()

        # Normalize any funky unicode (smart dashes, fraction slash, NBSP, etc.)
        val = unicodedata.normalize("NFKC", val)

        # Quick exit for junk placeholders
        if re.fullmatch(r"[\.\-_/ ]*", val):
            return pd.NA

        # 1) insert space between ANY letter and a following digit (Unicode-safe)
        val = re.sub(r"(?<=[^\W\d_])(?=\d)", " ", val)

        # 2) replace non-ASCII dashes and fraction slash as you already do...
        val = re.sub(r"[\u2012\u2013\u2014\u2212\uf02d\u2044\-]+", "/", val)
        val = re.sub(r"[\.•·]+", "/", val)

        val = val.replace("\xa0", " ")
        val = re.sub(r"[\u200B-\u200D\uFEFF]", "", val)

        # 3) strip letter runs unless they are month names (use Unicode letters)
        def replacer(m):
            text = m.group(0)
            return text if self.month_pattern.fullmatch(text) else ""

        # BEFORE: r"[A-Za-z]+"
        cleaned = re.sub(r"[^\W\d_]+", replacer, val, flags=re.UNICODE)

        # whitespace collapse
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        # 4) remove invisible format/control chars that \s doesn't catch
        cleaned = re.sub(r"[\u200B-\u200D\uFEFF]", "", cleaned)

        # 5) collapse repeated separators, strip stray ends
        cleaned = re.sub(r"[\/\-\.]{2,}", "/", cleaned).strip(" /-.,")

        cleaned = re.sub(r"^[^\d]+(?=\d)", "", cleaned)

        # 6) ISO first (no \b anchors)
        m = re.search(r"(\d{4})\s*[-/]\s*(\d{1,2})\s*[-/]\s*(\d{1,2})", cleaned)
        if m:
            y, mo, da = int(m.group(1)), int(m.group(2)), int(m.group(3))
            return f"{y:04d}-{mo:02d}-{da:02d}"

        # 7) US style next (no \b anchors)
        m = re.search(r"(\d{1,2})\s*[-/]\s*(\d{1,2})\s*[-/]\s*(\d{2,4})", cleaned)
        if m:
            mo, da, y = m.group(1), m.group(2), m.group(3)
            if len(y) == 2:
                y = int("20" + y)
            else:
                y = int(y)
            mo, da, y = int(mo), int(da), int(y)
            return f"{y:04d}-{mo:02d}-{da:02d}" 

        # 8) last resort: any non-digit separators
        m = re.search(r"(\d{1,2})\D+(\d{1,2})\D+(\d{2,4})", cleaned)
        if m:
            mo, da, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
            return f"{y:04d}-{mo:02d}-{da:02d}" 

        return pd.NA
    
    # ---- normalize ----
    
    def normalize(self, s: pd.Series) -> pd.Series:

        """
        Normalize raw date values into pandas datetime objects.

        Processing steps:
            1. Apply shared preprocessing via `base_clean()`
            2. Replace common invalid tokens with missing values
            3. Apply date-specific normalization via `_clean_text()`
            4. Parse cleaned values using `pd.to_datetime()`

        Args:
            s (pd.Series):
                Raw date values.

        Returns:
            pd.Series:
                Parsed datetime values or `NaT` where parsing fails.
        """
        
        s = self.base_clean(s)
        
        s = s.astype("string").str.strip()

        invalid_tokens = {"","n/a", "na", "none", "null", "nan", "<NA>","NaT"}
        s = s.mask(s.str.lower().isin(invalid_tokens), pd.NA)

        # Apply cleaning
        cleaned = s.map(self._clean_text)

        # Serial dates may already be datetime; only coerce the rest
        parsed = pd.to_datetime(cleaned, errors="coerce", dayfirst=False, utc=False)

        return parsed
    # ---- format ----

    def format(self, s_norm: pd.Series) -> pd.Series: 

        """
        Format datetime values as ISO date strings.

        Args:
            s_norm (pd.Series):
                Normalized datetime values.

        Returns:
            pd.Series:
                ISO-formatted date strings (`YYYY-MM-DD`). Missing
                values are returned as empty strings.
        """

        out = s_norm.dt.strftime("%Y-%m-%d")
        return out.fillna("")
    
    # ---- cchecks ----

    def errors_df(self, col: str, raw: pd.Series, s_norm: pd.Series,
                  file=None, sheet=None, row_offset: int = 1) -> pd.DataFrame:
        """
        Construct validation errors for date values.

        Error rules:
            • "Required but missing"
                Missing value in a required field.
            • "Invalid Value, not a valid date"
                Value could not be parsed as a valid date.
            • "Invalid Value, date before minimum allowed"
                Parsed date is earlier than the configured minimum.
            • "Invalid Value, date after maximum allowed"
                Parsed date is later than the configured maximum.

        Returns:
            pd.DataFrame:
                Structured date validation errors.
        """
        

        raw = raw.replace({"<NA>": pd.NA, "NaT": pd.NA, "nan": pd.NA})

        masks = {}
        masks["Required but missing"] = (
            s_norm.isna() & raw.isna() if self.required else pd.Series(False, index=s_norm.index)
        )

        masks["Invalid Value, not a valid date"] = (
            raw.notna() & raw.astype("string").str.strip().ne("") & s_norm.isna()
        )

        # add range checks
        if self.min_date is not None:
            masks["Invalid Value, date before minimum allowed"] = (
                s_norm.notna() & (s_norm < self.min_date)
            )
        if self.max_date is not None:
            masks["Invalid Value, date after maximum allowed"] = (
                s_norm.notna() & (s_norm > self.max_date)
            )

        frames = []
        for rule, mask in masks.items():
            idx = raw.index[mask.fillna(False)]
            if len(idx) == 0:
                continue
            frames.append(pd.DataFrame({
                "file": file,
                "sheet": sheet,
                "row_number": (
                self.row_numbers.loc[idx].values   # <-- use self.row_numbers
                if self.row_numbers is not None
                else idx.to_series().add(row_offset).values
            ),
                "column": col,
                "rule": rule,
                "raw_value": raw.loc[idx].astype("string").values,
                "normalized": s_norm.loc[idx].astype("string").values,
            }, index=idx))

        return pd.concat(frames) if frames else pd.DataFrame(
            columns=["file", "sheet", "row_number", "column", "rule", "raw_value", "normalized"]
        )
    
class zipCodeColumn(BaseColumn):

    """
    Validator for U.S. ZIP code fields.

    This column type normalizes ZIP code values into canonical 5-digit
    representations and validates basic ZIP formatting rules.

    Supported behaviors include:
        • removal of formatting characters
        • preservation of leading zeros
        • normalization of 4-digit ZIPs via left-padding
        • handling of malformed or placeholder values

    Behavior:
        • Applies shared preprocessing via `base_clean()`
        • Optionally strips non-digit formatting characters
        • Normalizes ZIP values into canonical digit strings
        • Produces standardized validation errors for invalid ZIP codes

    Attributes:
        required (bool):
            Whether missing values should generate validation errors.
        strip_formatting (bool):
            Whether non-digit formatting characters should be removed.
        row_numbers (pd.Series | None):
            Row references used in validation reporting.
    """

    name = "zip_code"
    _non_digits = re.compile(r"\D+")

    def __init__(self, 
                 required: bool = False, 
                 strip_formatting: bool = True,
                 row_numbers = None):
        
        self.required = required
        self.strip_formatting = strip_formatting
        self.row_numbers = row_numbers
        """
        required = True -> blank after cleaning counts as an error 
        strip_formatting -> remove hyphens/spaces/etc. before validating
        """
        
    # ---- Step 1: normalize (vectorized) ----

    def normalize(self, s: pd.Series) -> pd.Series:

        """
        Normalize raw ZIP code values.

        Processing steps:
            1. Apply shared preprocessing via `base_clean()`
            2. Normalize whitespace
            3. Optionally remove non-digit formatting characters
            4. Convert empty values to `pd.NA`

        Args:
            s (pd.Series):
                Raw ZIP code values.

        Returns:
            pd.Series:
                Cleaned ZIP code strings or `pd.NA`.
        """

        s = self.base_clean(s)

        s = (
            s.astype("string")
            .str.replace(r"\.0$", "", regex=True)
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
        )

        if self.strip_formatting:
            s = s.fillna("").str.replace(self._non_digits, "", regex=True)
            s = s.replace("", pd.NA)

        return s
    
    # ---- Step 2: validate (vectorized) ----

    def validate(self, 
                 s_norm: pd.Series) -> pd.Series:

        ##  confirm the pattern is 7 digits (or blank if not required)
        ok_pattern = s_norm.str.fullmatch(r"\d{5}", na=False)
        ok_required = ok_pattern & (~s_norm.isna() if self.required else True)
        return ok_required
    
    def format(self, 
               s_norm: pd.Series) -> pd.Series: 
        """
        Convert normalized ZIP values into canonical 5-digit ZIP codes.

        Formatting behavior includes:
            • left-padding 4-digit ZIP codes
            • correcting certain misplaced trailing-zero patterns
            • invalidating malformed ZIP values

        Args:
            s_norm (pd.Series):
                Normalized ZIP code values.

        Returns:
            pd.Series:
                Canonical 5-digit ZIP codes or `pd.NA` for invalid values.
        """

        out = s_norm.copy()

        # ---- CASE 1: 4-digit → pad left with 0 ----
        four_digit_mask = out.str.fullmatch(r"\d{4}")
        out.loc[four_digit_mask] = "0" + out.loc[four_digit_mask]

        # ---- CASE 2: 5-digit but with misplaced leading zero
        # Example: 68770 → 06877
        wrong_zero_mask = (
            out.str.fullmatch(r"\d{5}") &
            out.str.endswith("0") &
            ~out.str.startswith("0")
        )

        # Rotate last digit → front
        out.loc[wrong_zero_mask] = (
            "0" + out.loc[wrong_zero_mask].str[:-1]
        )

        # ---- Final: keep only valid 5-digit ZIPs ----
        valid_mask = out.str.fullmatch(r"\d{5}")
        out = out.where(valid_mask, pd.NA)

        return out 
    
    def errors_df(self, 
                  col: str, 
                  raw: pd.Series, 
                  s_norm: pd.Series, 
                  file = None, 
                  sheet = None, 
                  row_offset: int = 1) -> pd.DataFrame:

        """
        Construct validation errors for ZIP code values.

        Error rules:
            • "Required but missing"
                Missing value in a required field.
            • "Invalid Value, zipcode must 5 digits (e.g. 06543) or 4 digits (6434)"
                ZIP value could not be interpreted as a valid ZIP code.

        Returns:
            pd.DataFrame:
                Structured ZIP code validation errors.
        """

        masks = {
            "Required but missing": s_norm.isna() & raw.isna() if self.required else pd.Series(False, index = s_norm.index),
            "Invalid Value, zipcode must 5 digits (e.g. 06543) or 4 digits (6434)": (
                (s_norm.notna() & ~s_norm.str.fullmatch(r"\d{4,5}")) |
                (s_norm.isna() & raw.notna())
            )
        }

        frames = []

        for rule, mask in masks.items():

            idx = raw.index[mask.fillna(False)]
            if len(idx) == 0: 
                continue
            frames.append(pd.DataFrame({
                "file": file,
                "sheet": sheet, 
                "row_number": (
                self.row_numbers.loc[idx].values   # <-- use self.row_numbers
                if self.row_numbers is not None
                else idx.to_series().add(row_offset).values
            ),
                "column": col,
                "rule": rule,
                "raw_value": raw.loc[idx].astype("string").values,
                "normalized": s_norm.loc[idx].astype("string").values,
            }, index  = idx))

        return pd.concat(frames) if frames else pd.DataFrame(
            columns = ["file","sheet","row_number","column","rule","raw_value","normalized"]
        )
    
class stateID7Column(BaseColumn):

    """
    Validator for State ID identifier fields.

    This column type validates and normalizes numeric State ID values used
    in workforce and education datasets.

    Supported identifier formats include:
        • legacy 6-digit identifiers
        • modern 7-digit identifiers

    Supported behaviors include:
        • removal of formatting characters
        • preservation of leading zeros
        • removal of Excel float artifacts such as ".0"

    Behavior:
        • Applies shared preprocessing via `base_clean()`
        • Optionally strips non-digit formatting characters
        • Normalizes identifiers into canonical digit strings
        • Produces standardized validation errors for invalid identifiers

    Attributes:
        required (bool):
            Whether missing values should generate validation errors.
        strip_formatting (bool):
            Whether formatting characters should be removed.
        row_numbers (pd.Series | None):
            Row references used in validation reporting.
    """

    name = "state_id_7"
    _non_digits = re.compile(r"\D+")

    def __init__(self, 
                 required: bool = False, 
                 strip_formatting: bool = True, 
                 row_numbers = None):

        """
        strip_formatting -> remove hyphens/spaces/etc. before validating
        """

        self.required = required
        self.strip_formatting = strip_formatting
        self.row_numbers = row_numbers

    # ---- Step 1: normalize (vectorized) ----

    def normalize(self, s: pd.Series) -> pd.Series:

        """
        Normalize raw State ID values.

        Processing steps:
            1. Apply shared preprocessing via `base_clean()`
            2. Remove formatting artifacts and non-digit characters
            3. Remove Excel float suffixes such as ".0"
            4. Convert empty values to `pd.NA`

        Args:
            s (pd.Series):
                Raw State ID values.

        Returns:
            pd.Series:
                Normalized 6-digit or 7-digit State ID values, or `pd.NA`.
        """

        s = s.astype("string")
        s = self.base_clean(s)
        s = s.str.strip()
        if self.strip_formatting:
            s = s.str.replace(r"\.0$", "", regex=True)
            s = s.fillna("").str.replace(self._non_digits, "", regex = True)
            s = s.replace("", pd.NA)
        return s 
    
    # ---- Step 2: validate (vectorized) ----

    def validate(self, s_norm: pd.Series) -> pd.Series:
        ## confirm the pattern is 7 digits (or blank if not required)
        ok_pattern = s_norm.str.fullmatch(r"\d{6,7}", na=False)
        ok_required = ok_pattern & (~s_norm.isna() if self.required else True)
        return ok_required
    
    def format(self, s_norm: pd.Series) -> pd.Series:
        """Return canonical State ID values unchanged."""
        return s_norm
    
    def errors_df(self, col: str, raw: pd.Series, s_norm: pd.Series, file = None, sheet = None, row_offset: int=1) -> pd.DataFrame:
   
        """
        Construct validation errors for State ID values.

        Error rules:
            • "Required but missing"
                Missing value in a required field.
            • "Invalid Value, State ID must be 6 or 7 digits"
                Value could not be interpreted as a valid State ID.

        Returns:
            pd.DataFrame:
                Structured State ID validation errors.
        """
        
        invalid_mask = (
            (s_norm.notna() & ~s_norm.str.fullmatch(r"\d{6,7}")) |
            (s_norm.isna() & raw.notna())
        )

        masks = {
            "Required but missing": (
                s_norm.isna() & raw.isna()
                if self.required
                else pd.Series(False, index=s_norm.index)
            ),
            "Invalid Value, State ID must be 6 or 7 digits (e.g. '123456' or '0123456')":
                invalid_mask
        }

        frames = []

        for rule, mask in masks.items():

            idx = raw.index[mask.fillna(False)]
            if len(idx) == 0:
                continue
            frames.append(pd.DataFrame({
                "file": file, 
                "sheet": sheet, 
                "row_number": (
                self.row_numbers.loc[idx].values   # <-- use self.row_numbers
                if self.row_numbers is not None
                else idx.to_series().add(row_offset).values
            ),
                "column": col,
                "rule": rule,
                "raw_value": raw.loc[idx].astype("string").values,
                "normalized": s_norm.loc[idx].astype("string").values,
            }, index = idx ))

        return pd.concat(frames) if frames else pd.DataFrame(
            columns = ["file","sheet","row_number","column","rule","raw_value","normalized"]
        )

class ONETCodeColumn(BaseColumn):
    """
    Column type for validating and normalizing O*NET-SOC occupation codes.

    This validator handles the wide variety of formats in which O*NET codes
    commonly appear in workforce development datasets. It cleans, normalizes,
    and validates codes to the canonical ``DD-DDDD.DD`` structure
    (e.g., ``"15-2051.00"``), and supports multiple codes per cell
    separated by commas, semicolons, or whitespace.

    Behavior Overview:
        • Applies BaseColumn cleaning (strip whitespace, remove Excel errors).
        • Accepts multi-valued cells and splits them into individual codes.
        • Removes extraneous characters and punctuation.
        • Auto-recognizes several common malformed forms, e.g.:

              - ``"15-2051"``       → ``"15-2051.00"``
              - ``"15205100"``      → ``"15-2051.00"``
              - ``"15.2051"``       → ``"15-2051.00"``
              - ``"15.2051.00"``    → ``"15-2051.00"``

        • Re-combines multiple codes using semicolon delimiters.
        • Validates that *every* code in the cell matches the O*NET pattern.

    Args:
        required (bool, optional):
            If True, missing values after normalization generate a
            ``"Required but missing"`` error.
        row_numbers (pd.Series, optional):
            Excel row numbers aligned to Series indices, used to populate the
            ``row_number`` field in error logs.

    normalize(s):
        Normalize raw O*NET codes.

        Steps:
            1. Apply BaseColumn cleaning and strip floating-point artifacts.
            2. Split multi-valued cells on commas, semicolons, or whitespace.
            3. Remove illegal characters and punctuation.
            4. Reconstruct codes into canonical ``DD-DDDD.DD`` format
               where possible.
            5. Return a semicolon-joined string of codes or ``pd.NA``.

        Returns:
            pd.Series of canonicalized O*NET codes (strings) or ``pd.NA``.

    format(s_norm):
        Formatting step for the validator. Returns normalized values unchanged,
        as normalization already produces the canonical representation.

    errors_df(col, raw, s_norm, file, sheet, row_offset):
        Construct a structured DataFrame describing validation errors.

        Error types recorded:
            • ``"Required but missing"`` — value is missing when required.
            • ``"Invalid Value, must match ONET format (e.g. '15-2051.00')"`` —
              triggered when:
                  – raw data is present but cannot be normalized, or
                  – normalized data is present but contains one or more
                    invalid O*NET codes.

        For multi-code cells:
            All codes must match the canonical pattern; otherwise the entire
            cell is flagged as invalid.

        Output columns:
            ["file", "sheet", "row_number", "column",
             "rule", "raw_value", "normalized"]

        Row number handling:
            • Use ``row_numbers`` if provided,
            • Otherwise, fall back to ``index + row_offset``.

    Notes:
        • This validator does not attempt to verify that O*NET codes exist
          in the official taxonomy—only that they match the syntactic format.
        • The semicolon-delimited output allows downstream systems to
          easily split and explode multi-code rows.
        • Leading zeros in O*NET codes are always preserved.
    """

    name: str = "onet_code"

    def __init__(self, required: bool = False, row_numbers = None):
        self.required = required
        self.pattern = re.compile(r"^\d{2}-\d{4}\.\d{2}$")
        self.row_numbers = row_numbers

    def fix_format(self, val):
        if pd.isna(val) or val == "":
            return pd.NA
        val = str(val)

        # Split on commas, semicolons, spaces
        codes = re.split(r"[;, ]+", val.strip())
        formatted_codes = []

        for code in codes:

            # 🔹 Sanitize: keep only digits, dash, and period
            code = re.sub(r"[^0-9\.\-]", "", code)

            if code == "":
                continue

            # Case 1: already correct
            if self.pattern.fullmatch(code):
                formatted_codes.append(code)
                continue

            # Case 2: "15-2051"
            if re.fullmatch(r"\d{2}-\d{4}", code):
                formatted_codes.append(code + ".00")
                continue

            # Case 3: "15205100"
            if re.fullmatch(r"\d{8}", code):
                formatted_codes.append(f"{code[:2]}-{code[2:6]}.{code[6:]}")
                continue

            # Case 4: "15205100" but as 6 digits + "00"
            if re.fullmatch(r"\d{6}00", code):
                formatted_codes.append(f"{code[:2]}-{code[2:6]}.00")
                continue

            # Case 5: "15.2051"
            if re.fullmatch(r"\d{2}\.\d{4}", code):
                code = code.replace(".","-")
                formatted_codes.append(code + ".00")
                continue

            # Case 6: "15.2051.00"
            if re.fullmatch(r"\d{2}\.\d{4}\.\d{2}", code):
                formatted_codes.append(f"{code[:2]}-{code[3:7]}.00")
                continue

            formatted_codes.append(code)

        return ";".join(formatted_codes) if formatted_codes else pd.NA

    def normalize(self, s: pd.Series) -> pd.Series:

        s = s.astype("string")
        s = self.base_clean(s)
        s = s.str.replace(r"\.0$", "", regex=True)
        s = s.str.strip()

        def _apply(val):
            return self.fix_format(val)

        return s.map(_apply)

    def format(self, s_norm: pd.Series) -> pd.Series:
        return s_norm

    def errors_df(self, col: str, raw: pd.Series, s_norm: pd.Series,
                  file=None, sheet=None, row_offset: int = 1) -> pd.DataFrame:
        
        def all_valid_codes(val: str) -> bool:
            if pd.isna(val) or val == "":
                return False if self.required else True
            codes = val.split(";")
            return all(re.fullmatch(r"\d{2}-\d{4}\.\d{2}$", c) for c in codes)

        mask_valid = s_norm.fillna("").map(all_valid_codes)

        masks = {
            "Required but missing": (
                s_norm.isna() & raw.isna() if self.required else pd.Series(False, index=s_norm.index)
            ),
            "Invalid Value, must match ONET format (e.g. '15-2051.00')": (
                s_norm.isna() & raw.notna()
            ),
            "Invalid Value, must match ONET format (e.g. '15-2051.00')": (
                s_norm.notna() & ~mask_valid
            ),
        }

        frames = []
        for rule, mask in masks.items():
            idx = raw.index[mask.fillna(False)]
            if len(idx) == 0:
                continue
            frames.append(pd.DataFrame({
                "file": file,
                "sheet": sheet,
                "row_number": (
                self.row_numbers.loc[idx].values   # <-- use self.row_numbers
                if self.row_numbers is not None
                else idx.to_series().add(row_offset).values
            ),
                "column": col,
                "rule": rule,
                "raw_value": raw.loc[idx].astype("string").values,
                "normalized": s_norm.loc[idx].astype("string").values,
            }, index=idx))

        return pd.concat(frames) if frames else pd.DataFrame(
            columns=["file","sheet","row_number","column","rule","raw_value","normalized"]
        )

class CIPCodeColumn(BaseColumn):
    """
    Validator for O*NET-SOC occupation code fields.

    This column type normalizes and validates O*NET occupation codes into
    canonical `DD-DDDD.DD` format.

    Supported behaviors include:
        • normalization of common malformed O*NET formats
        • handling of multi-code cells
        • removal of formatting noise and invalid characters
        • canonicalization of codes into semicolon-delimited output

    Behavior:
        • Applies shared preprocessing via `base_clean()`
        • Normalizes codes into canonical O*NET format
        • Supports multiple codes per cell
        • Produces standardized validation errors for invalid codes

    Attributes:
        required (bool):
            Whether missing values should generate validation errors.
        pattern (Pattern):
            Regular expression defining canonical O*NET format.
        row_numbers (pd.Series | None):
            Row references used in validation reporting.
    """
     
    name: str = "cip_code"

    def __init__(self, required: bool = False, row_numbers = None):
        self.required = required
        # Acceptable final patterns
        self.patterns = [
            re.compile(r"^\d{2}$"),        # 2-digit
            re.compile(r"^\d{2}\.\d{2}$"), # 4-digit with dot
            re.compile(r"^\d{2}\.\d{4}$"), # 6-digit with dot
        ]
        self.row_numbers = row_numbers

    # --- normalize ---
    def normalize(self, s: pd.Series) -> pd.Series:

        """
        Normalize raw O*NET code values.

        Processing steps:
            1. Apply shared preprocessing via `base_clean()`
            2. Remove Excel float artifacts such as ".0"
            3. Apply O*NET-specific canonicalization logic
            4. Return canonical semicolon-delimited code strings

        Args:
            s (pd.Series):
                Raw O*NET code values.

        Returns:
            pd.Series:
                Canonical O*NET code values or `pd.NA`.
        """
        
        s = s.astype("string").str.strip()
        s = self.base_clean(s)
        s = s.str.replace(r"\.0$", "", regex=True)

        def fix_format(val):
            if pd.isna(val) or val == "":
                return pd.NA
            val = str(val)

            # Split into multiple codes
            codes = re.split(r"[;, ]+", val.strip())
            formatted_codes = []

            for code in codes:
                if not code:
                    continue

                # 🔹 Sanitize: keep only digits and dot
                code = re.sub(r"[^0-9\.]", "", code)
                if not code:
                    continue

                # Case: already valid
                if any(p.fullmatch(code) for p in self.patterns):
                    formatted_codes.append(code)
                    continue

                # Case: 6 digits, no dot: "151201" → "15.1201"
                if re.fullmatch(r"\d{6}", code):
                    formatted_codes.append(f"{code[:2]}.{code[2:]}")
                    continue

                # Case: 4 digits, no dot: "1512" → "15.12"
                if re.fullmatch(r"\d{4}", code):
                    formatted_codes.append(f"{code[:2]}.{code[2:]}")
                    continue

                # Case: 2 digits only
                if re.fullmatch(r"\d{2}", code):
                    formatted_codes.append(code)
                    continue

                # Case: 8 digits ending in 00: "15120100" → "15.1201"
                if re.fullmatch(r"\d{8}", code) and code.endswith("00"):
                    formatted_codes.append(f"{code[:2]}.{code[2:6]}")
                    continue

                # Otherwise skip junk
                continue

            return ";".join([c for c in formatted_codes if c]) if formatted_codes else pd.NA

        return s.map(fix_format)


    # --- format ---
    def format(self, s_norm: pd.Series) -> pd.Series:
        """Return canonical O*NET codes unchanged."""
        return s_norm

    # --- errors ---
    def errors_df(self, col: str, raw: pd.Series, s_norm: pd.Series,
                  file=None, sheet=None, row_offset: int = 1) -> pd.DataFrame:
        
        """
        Construct validation errors for O*NET code values.

        Error rules:
            • "Required but missing"
                Missing value in a required field.
            • "Invalid Value, must match ONET format (e.g. '15-2051.00')"
                Value could not be interpreted as a valid O*NET code.

        Multi-code cells are considered invalid if any contained code
        fails validation.

        Returns:
            pd.DataFrame:
                Structured O*NET validation errors.
        """

        def all_valid_codes(val: str) -> bool:
            if pd.isna(val) or val == "":
                return False if self.required else True
            codes = val.split(";")
            return all(any(p.fullmatch(c) for p in self.patterns) for c in codes if c)

        mask_valid = s_norm.fillna("").map(all_valid_codes)

        masks = {
            "Required but missing": (
                s_norm.isna() & raw.isna() if self.required else pd.Series(False, index=s_norm.index)
            ),
            "Invalid Value, must match CIP format (e.g. '15', '15.12', '15.1201')": (
                s_norm.isna() & raw.notna()
            ) | (
                s_norm.notna() & ~mask_valid
            ),
        }
        frames = []
        for rule, mask in masks.items():
            idx = raw.index[mask.fillna(False)]
            if len(idx) == 0:
                continue
            frames.append(pd.DataFrame({
                "file": file,
                "sheet": sheet,
                "row_number": (
                self.row_numbers.loc[idx].values   # <-- use self.row_numbers
                if self.row_numbers is not None
                else idx.to_series().add(row_offset).values
            ),
                "column": col,
                "rule": rule,
                "raw_value": raw.loc[idx].astype("string").values,
                "normalized": s_norm.loc[idx].astype("string").values,
            }, index=idx))

        return pd.concat(frames) if frames else pd.DataFrame(
            columns=["file","sheet","row_number","column","rule","raw_value","normalized"]
        )

class hourlyWageColumn(BaseColumn):
    """
    Validator for hourly wage fields.

    This column type extracts and validates hourly wage values from
    free-text input and normalizes them into numeric wage values.

    Supported behaviors include:
        • removal of currency symbols and wage-related text
        • parsing of numeric wage values from free text
        • detection of ambiguous wage ranges
        • configurable minimum and maximum wage thresholds

    Wage ranges (e.g. "15-20", "10 to 12") are intentionally treated
    as invalid because they represent non-atomic wage entries.

    Behavior:
        • Applies shared preprocessing via `base_clean()`
        • Detects wage ranges before numeric parsing
        • Removes formatting and currency artifacts
        • Converts valid values into numeric hourly wages
        • Produces standardized validation errors and confirmation warnings

    Attributes:
        required (bool):
            Whether missing values should generate validation errors.
        min_wage (float):
            Minimum allowed hourly wage.
        max_wage (float):
            Threshold above which confirmation warnings are generated.
        row_numbers (pd.Series | None):
            Row references used in validation reporting.
    """

    name: str = "hourly_wage"

    def __init__(self, required: bool = False, min_wage: float = 5.0, max_wage: float = 45.0, row_numbers = None):
        self.required = required
        self.min_wage = min_wage
        self.max_wage = max_wage
        self._pattern_strip = re.compile(r"[^0-9\.]")  # strip everything except digits and dot
        self._range_pattern = re.compile(r"\d+\s*[-/]\s*\d+|\d+\s+to\s+\d+", re.IGNORECASE)
        self.row_numbers = row_numbers

    # --- normalize ---
    def normalize(self, s: pd.Series) -> pd.Series:

        """
        Normalize free-text wage values into numeric hourly wages.

        Processing steps:
            1. Normalize casing and whitespace
            2. Detect wage ranges
            3. Remove currency and unit formatting
            4. Strip non-numeric characters
            5. Parse numeric wage values

        Values equal to zero are treated as missing values.

        Args:
            s (pd.Series):
                Raw wage values.

        Returns:
            pd.Series:
                Numeric hourly wage values or `pd.NA`.
        """

        s = s.astype("string").str.strip().str.lower()

        def clean(val):
            if pd.isna(val) or val == "":
                return pd.NA
            # Ranges are left untouched so we can detect them later
            if self._range_pattern.search(val):
                return val
            # Remove symbols/words
            val = val.replace("per hr", "").replace("hourly", "").replace("hr", "")
            val = self._pattern_strip.sub("", val)
            try:
                num = float(val)
                return pd.NA if num == 0 else num             
            except ValueError:
                return pd.NA

        return s.map(clean)

    # --- format ---
    def format(self, s_norm: pd.Series) -> pd.Series:
        """
        Format numeric wage values as currency strings.

        Args:
            s_norm (pd.Series):
                Normalized hourly wage values.

        Returns:
            pd.Series:
                Currency-formatted wage strings (e.g. "$17.00").
        """
        return s_norm.map(lambda x: f"${x:.2f}" if isinstance(x, float) else pd.NA)

    # --- errors ---
    def errors_df(self, col: str, raw: pd.Series, s_norm: pd.Series,
                  file=None, sheet=None, row_offset: int = 1) -> pd.DataFrame:
        """
        Construct validation errors for hourly wage values.

        Error rules:
            • "Required but missing"
                Missing value in a required field.
            • "Invalid Value, must be >= $X.XX"
                Wage falls below the configured minimum threshold.
            • "Confirmation required, unusually high (> $X.XX)"
                Wage exceeds the configured confirmation threshold.
            • "Invalid Value, must be a number indicating hourly wage"
                Value could not be interpreted as a valid atomic wage.

        Wage ranges are treated as invalid values.

        Returns:
            pd.DataFrame:
                Structured hourly wage validation errors.
        """

        # Identify ranges directly from raw values
        range_mask = raw.astype("string").str.lower().str.contains(self._range_pattern)

        masks = {
            "Required but missing": (
                s_norm.isna() & raw.isna() & ~range_mask if self.required else pd.Series(False, index=s_norm.index)
            ),
            f"Invalid Value, must be >= ${self.min_wage:.2f}": (
                s_norm.notna() & s_norm.apply(lambda v: isinstance(v, float) and v < self.min_wage)
            ),
            f"Confirmation required, unusually high (> ${self.max_wage:.2f})": (
                s_norm.notna() & s_norm.apply(lambda v: isinstance(v, float) and v > self.max_wage)
            ),
            "Invalid Value, must be a number indicating hourly wage (ideal format: '$17.00')": (
                s_norm.isna() & raw.notna()
            ),
        }

        frames = []
        for rule, mask in masks.items():
            idx = raw.index[mask.fillna(False)]
            if len(idx) == 0:
                continue
            frames.append(pd.DataFrame({
                "file": file,
                "sheet": sheet,
                "row_number": (
                self.row_numbers.loc[idx].values   # <-- use self.row_numbers
                if self.row_numbers is not None
                else idx.to_series().add(row_offset).values
            ),
                "column": col,
                "rule": rule,
                "raw_value": raw.loc[idx].astype("string").values,
                "normalized": s_norm.loc[idx].astype("string").values,
            }, index=idx))

        return pd.concat(frames) if frames else pd.DataFrame(
            columns=["file","sheet","row_number","column","rule","raw_value","normalized"]
        )

class hoursWorkedColumn(BaseColumn):
    """
    Validator for hours-worked fields.

    This column type normalizes and validates numeric hour values from
    free-text input.

    Supported behaviors include:
        • parsing numeric hour values from text
        • coercion of invalid or blank values to missing values
        • validation against configurable minimum and maximum thresholds
        • normalization of whole-number floats for cleaner output

    Behavior:
        • Applies shared preprocessing via `base_clean()`
        • Converts valid numeric values into floats
        • Produces standardized validation errors for:
            - missing required values
            - negative hour values
            - excessively large hour values
            - non-numeric inputs

    Attributes:
        required (bool):
            Whether missing values should generate validation errors.
        max_hours (int | float):
            Maximum allowed hour value.
        row_numbers (pd.Series | None):
            Row references used in validation reporting.
    """
    name: str = "hours_worked"

    def __init__(self, required: bool = False, max_hours: int = 80, row_numbers = None):
        self.required = required
        self.max_hours = max_hours
        self.row_numbers = row_numbers

    # --- normalize ---
    def normalize(self, s: pd.Series) -> pd.Series:
        """
        Normalize raw hour values into numeric hour values.

        Processing steps:
            1. Apply shared preprocessing via `base_clean()`
            2. Strip whitespace and coerce values to numeric form
            3. Convert invalid values to `pd.NA`

        Args:
            s (pd.Series):
                Raw hour values.

        Returns:
            pd.Series:
                Numeric hour values or `pd.NA`.
        """
        s = s.astype("string").str.strip()
        s = self.base_clean(s)   

        def to_number(val):
            if pd.isna(val) or val == "":
                return pd.NA
            try:
                return float(val)
            except ValueError:
                return pd.NA

        return s.map(to_number)

    # --- format ---
    def format(self, s_norm: pd.Series) -> pd.Series:
        """
        Format normalized hour values for output.

        Whole-number floats are converted to integers while fractional
        values are preserved.

        Args:
            s_norm (pd.Series):
                Normalized hour values.

        Returns:
            pd.Series:
                Cleaned numeric hour values.
        """
        return s_norm.map(lambda x: int(x) if pd.notna(x) and float(x).is_integer() else x)

    # --- errors ---
    def errors_df(self, col: str, raw: pd.Series, s_norm: pd.Series,
                  file=None, sheet=None, row_offset: int = 1) -> pd.DataFrame:
        """
        Construct validation errors for hour values.

        Error rules:
            • "Required but missing"
                Missing value in a required field.
            • "Invalid Value, must be non-negative"
                Hour value is negative.
            • "Invalid Value, cannot exceed X hours"
                Hour value exceeds the configured maximum.
            • "Invalid Value, must be a number indicating typical weekly hours"
                Value could not be interpreted as a numeric hour value.

        Returns:
            pd.DataFrame:
                Structured hour validation errors.
        """

        masks = {
            "Required but missing": (
                s_norm.isna() & raw.isna() if self.required else pd.Series(False, index=s_norm.index)
            ),
            "Invalid Value, must be non-negative": (
                s_norm.notna() & (s_norm < 0)
            ),
            f"Invalid Value, cannot exceed {self.max_hours} hours": (
                s_norm.notna() & (s_norm > self.max_hours)
            ),
            "Invalid Value, must be a number indicating typical weekly hours (ideal format: '25')": (
                s_norm.isna() & raw.notna()
            ),
        }

        frames = []
        for rule, mask in masks.items():
            idx = raw.index[mask.fillna(False)]
            if len(idx) == 0:
                continue
            frames.append(pd.DataFrame({
                "file": file,
                "sheet": sheet,
                "row_number": (
                self.row_numbers.loc[idx].values   # <-- use self.row_numbers
                if self.row_numbers is not None
                else idx.to_series().add(row_offset).values
            ),
                "column": col,
                "rule": rule,
                "raw_value": raw.loc[idx].astype("string").values,
                "normalized": s_norm.loc[idx].astype("string").values,
            }, index=idx))

        return pd.concat(frames) if frames else pd.DataFrame(
            columns=["file","sheet","row_number","column","rule","raw_value","normalized"]
        )

class NAICSCodeColumn(BaseColumn):
    """
    Validator for NAICS (North American Industry Classification System)
    code fields.

    This column type normalizes and validates NAICS codes represented as
    2–6 digit numeric identifiers.

    Supported behaviors include:
        • normalization of malformed numeric formats
        • removal of formatting artifacts and decimal suffixes
        • handling of multi-code cells
        • canonicalization of semicolon-delimited code lists

    Behavior:
        • Applies shared preprocessing via `base_clean()`
        • Extracts valid 2–6 digit NAICS codes
        • Supports multiple codes per cell
        • Produces standardized validation errors for invalid codes

    Attributes:
        required (bool):
            Whether missing values should generate validation errors.
        patterns (list[Pattern]):
            Regular expressions defining valid NAICS code lengths.
        row_numbers (pd.Series | None):
            Row references used in validation reporting.
    """
    name: str = "naics_code"

    def __init__(self, required: bool = False, row_numbers=None):
        self.required = required
        self.row_numbers = row_numbers

        # Acceptable NAICS lengths: 2–6 digits
        self.patterns = [
            re.compile(r"^\d{2}$"),
            re.compile(r"^\d{3}$"),
            re.compile(r"^\d{4}$"),
            re.compile(r"^\d{5}$"),
            re.compile(r"^\d{6}$"),
        ]

    # --- normalize ---
    def normalize(self, s: pd.Series) -> pd.Series:
        """
        Normalize raw NAICS values into canonical code strings.

        Processing steps:
            1. Apply shared preprocessing via `base_clean()`
            2. Remove Excel float artifacts such as ".0"
            3. Split multi-code entries on common delimiters
            4. Remove invalid formatting characters
            5. Extract valid 2–6 digit NAICS codes

        Args:
            s (pd.Series):
                Raw NAICS values.

        Returns:
            pd.Series:
                Semicolon-delimited NAICS code strings or `pd.NA`.
        """
        s = s.astype("string").str.strip()
        s = self.base_clean(s)
        s = s.str.replace(r"\.0$", "", regex=True)

        def fix_format(val):
            if pd.isna(val) or val == "":
                return pd.NA
            val = val.strip()

            # Split into multiple possible codes
            codes = re.split(r"[;,/ ]+", val)
            formatted_codes = []

            for code in codes:
                if not code:
                    continue

                # 🔹 Remove decimal portions (e.g., "561320.0" → "561320")
                if "." in code:
                    code = code.split(".")[0]

                # Sanitize: keep only digits
                code = re.sub(r"[^0-9]", "", code)
                if not code:
                    continue

                # If it's 2–6 digits, keep it
                if any(p.fullmatch(code) for p in self.patterns):
                    formatted_codes.append(code)
                    continue

                # Handle common bad formats (e.g., too long with trailing zeros)
                if re.fullmatch(r"\d{8}", code) and code.endswith("00"):
                    formatted_codes.append(code[:6])
                    continue

                # Skip anything else
                continue

            return ";".join([c for c in formatted_codes if c]) if formatted_codes else pd.NA

        return s.map(fix_format)
    # --- format ---
    def format(self, s_norm: pd.Series) -> pd.Series:
        """Return canonical NAICS codes unchanged."""
        return s_norm

    # --- errors ---
    def errors_df(self, col: str, raw: pd.Series, s_norm: pd.Series,
                  file=None, sheet=None, row_offset: int = 1) -> pd.DataFrame:
        """
        Construct validation errors for NAICS code values.

        Error rules:
            • "Required but missing"
                Missing value in a required field.
            • "Invalid Value, must match NAICS format"
                Value could not be interpreted as a valid NAICS code.

        Multi-code cells are considered invalid if any contained code
        fails validation.

        Returns:
            pd.DataFrame:
                Structured NAICS validation errors.
        """

        def all_valid_codes(val: str) -> bool:
            if pd.isna(val) or val == "":
                return False if self.required else True
            codes = val.split(";")
            return all(any(p.fullmatch(c) for p in self.patterns) for c in codes if c)

        mask_valid = s_norm.fillna("").map(all_valid_codes)

        masks = {
            "Required but missing": (
                s_norm.isna() & raw.isna() if self.required else pd.Series(False, index=s_norm.index)
            ),
            "Invalid Value, must match NAICS format (e.g. '31', '311', '31151', '311513')": (
                (s_norm.isna() & raw.notna()) | (s_norm.notna() & ~mask_valid)
            ),
        }

        frames = []
        for rule, mask in masks.items():
            idx = raw.index[mask.fillna(False)]
            if len(idx) == 0:
                continue
            frames.append(pd.DataFrame({
                "file": file,
                "sheet": sheet,
                "row_number": (
                    self.row_numbers.loc[idx].values
                    if self.row_numbers is not None
                    else idx.to_series().add(row_offset).values
                ),
                "column": col,
                "rule": rule,
                "raw_value": raw.loc[idx].astype("string").values,
                "normalized": s_norm.loc[idx].astype("string").values,
            }, index=idx))

        return pd.concat(frames) if frames else pd.DataFrame(
            columns=["file","sheet","row_number","column","rule","raw_value","normalized"]
        )


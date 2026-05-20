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
        Perform low-level normalization of a column before type-specific validation.

        Operations performed:
        - Convert to pandas `"string"` dtype
        - Strip leading/trailing whitespace
        - Replace empty strings or whitespace-only strings with `pd.NA`
        - Replace common Excel/CSV error tokens (e.g. "#VALUE!", "NaN") with `pd.NA`

        Args:
            s (pd.Series):
                Raw column values.

        Returns:
            pd.Series:
                Cleaned series with standardized missing-value representation.
        """
        s = s.astype("string")
        s = s.str.strip().replace("", pd.NA)
        s = s.replace(r"^\s*$", pd.NA, regex=True)
        s = s.replace(self.ERROR_TOKENS, pd.NA)
        return s
    def errors_df(self):
        """
        This is a function shell in the base column class, each sublcass implements its own
        version. 

        Construct a standardized DataFrame describing validation errors for this
        column type.

        Each subclass defines its own validation rules (e.g., required values,
        type constraints, range checks, format rules), but all error reports
        returned from column validators share the same structure.

        Typical error conditions include (depending on subclass logic):
            - Missing required values
            - Values that cannot be normalized or parsed
            - Values that violate type- or format-specific constraints
            - Values that fall outside allowed or expected ranges

        Args:
            col (str):
                Name of the column being validated.
            raw (pd.Series):
                Original unnormalized values as read from the dataset.
            s_norm (pd.Series):
                Normalized or canonicalized values produced by `normalize()`.
            file (str or None):
                Optional identifier of the source file, included for reporting.
            sheet (str or None):
                Sheet name or dataset section used for contextual error reporting.
            row_offset (int):
                Offset applied when converting DataFrame index positions to
                Excel-style row numbers.

        Returns:
            pd.DataFrame:
                A structured validation error table with columns:
                [
                    "file",
                    "sheet",
                    "row_number",
                    "column",
                    "rule",
                    "raw_value",
                    "normalized"
                ]

                If no errors are found, returns an empty DataFrame with this schema.
    
        """

    def _clean(self):
        """

        This is a function shell in the base column class, each sublcass implements its own
        version. 

        Normalize a raw value into a standardized string representation suitable
        for comparison and downstream validation logic.

        This helper performs lightweight canonicalization to ensure consistent
        matching across different input formats.

        Typical cleaning steps:
            - Convert value to string if needed
            - Convert to lowercase for case-insensitive comparison
            - Collapse excessive internal whitespace
            - Strip leading/trailing whitespace
            - Treat sequences of zeros ("0", "00", etc.) or empty strings as missing

        Args:
            text (str or any):
                Raw input value.

        Returns:
            str:
                A normalized string representation, or an empty string if the value
                is considered missing.
        """
    
    def normalize(self, s: pd.Series) -> pd.Series:
        """
        This is a function shell in the base column class, each sublcass implements its own
        version. 

        Normalize a column's raw values into a standardized representation suitable
        for validation and downstream processing.

        Normalization typically includes:
            1. Applying the shared base cleaning (string coercion, trimming,
            whitespace collapsing, and removal of known error tokens)
            2. Performing type-specific transformations (e.g., parsing dates,
            numeric coercion, mapping to canonical labels)
            3. Producing a clean, consistent output that downstream validators
            can rely on

        Args:
            s (pd.Series):
                Raw column values as read from the source file.

        Returns:
            pd.Series:
                A normalized representation of the column. The specific form depends
                on the column subtype (e.g., strings, codes, dates, booleans). Values
                that cannot be meaningfully interpreted should be represented as
                `pd.NA`.
        """

class multiCategoricalColumn(BaseColumn):
    """
    Validator for multi-select categorical fields (e.g., Race/Ethnicity).

    Improvements over baseline:
      • Vectorized one‑hot via str.get_dummies(sep=';')
      • Token-level fuzzy cache to avoid repeated RapidFuzz calls

    New built-in conveniences:
      • normalize_to_indicators(...) -> DataFrame of binary columns
      • to_indicators(...) -> participant_id + binary columns
      • to_sql_indicators(...) -> write one-hot to SQL directly

    New behavior:
      • If multi_label is set (e.g., "Multi-Racial"), normalized cells with
        more than one canonical selection are collapsed to that single label.
    """

    name: str = "multiCategorical"

    def __init__(self,
                 accepted_responses,
                 required: bool = False,
                 fuzzy: bool = True,
                 min_score: int = 90,
                 delimiters: str = r",",
                 row_numbers=None,
                 protected_phrases: list[str] | None = None,
                 multi_label: str | None = "Multi-Racial",
                 unknown_label: str | None = "Unknown"):  # <-- todo: make multi_label default more flexible or optional. Ex: Make default Unknown only IF required = False, otherwise default should be pd.NA for required col logic
        self.required = required
        self.fuzzy = fuzzy
        self.min_score = min_score
        self._splitter = re.compile(delimiters)
        self._whitespace = re.compile(r"\s+")
        self.row_numbers = row_numbers
        self.multi_label = multi_label  # <-- todo: see above comment
        self.unknown_label = unknown_label # todo: add this default to blank cells ONLY if the col is not marked as required. 

        # Build normalized variant → canonical lookup and canonical set
        self.accepted: dict[str, str] = {}
        self.canonicals: set[str] = set()

        
        if self.unknown_label:
            # ensure Unknown is a canonical option too
            self.canonicals.add(self.unknown_label)
            self.accepted[self._clean(self.unknown_label)] = self.unknown_label


        if isinstance(accepted_responses, dict):
            for canonical, variants in accepted_responses.items():
                self.canonicals.add(canonical)
                for v in [canonical] + list(variants):
                    self.accepted[self._clean(v)] = canonical
        else:
            for r in accepted_responses:
                self.canonicals.add(r)
                self.accepted[self._clean(r)] = r

        # Ensure the multi_label itself is part of the canonical set so
        # indicators include a column for it even if no variants are provided.
        if self.multi_label:
            self.canonicals.add(self.multi_label)
            self.accepted[self._clean(self.multi_label)] = self.multi_label

        # Cache keys for fuzzy
        self._keys = list(self.accepted.keys())

        # Optional protected phrases handled pre-split
        self.protected_phrases = set()
        if protected_phrases:
            self.protected_phrases = {self._clean(p) for p in protected_phrases}

        # Fuzzy cache: cleaned token -> canonical or None
        self._fuzzy_cache: dict[str, str | None] = {}

    # --- internals ------------------------------------------------------------

    def _clean(self, text: str) -> str:
        if text is None or pd.isna(text):
            return ""
        if re.fullmatch(r"0+", str(text)):
            return ""
        return self._whitespace.sub(" ", str(text)).strip().casefold()

    def _protected_hits(self, cleaned_cell: str) -> set[str]:
        hits = set()
        for phrase in self.protected_phrases:
            if phrase and phrase in cleaned_cell:
                canon = self.accepted.get(phrase)
                if canon:
                    hits.add(canon)
        return hits

    def _fuzzy_resolve(self, key: str) -> str | None:
        if key in self._fuzzy_cache:
            return self._fuzzy_cache[key]
        match = process.extractOne(key, self._keys, scorer=fuzz.token_sort_ratio)
        if match and match[1] >= self.min_score:
            canon = self.accepted.get(match[0])
        else:
            canon = None
        self._fuzzy_cache[key] = canon
        return canon

    # --- normalize ------------------------------------------------------------

    def normalize(self, s: pd.Series) -> pd.Series:
        """
        Normalize a multi-select categorical column.

        Returns:
          • a single canonical (e.g., "Black"), or
          • the multi_label (e.g., "Multi-Racial") if >1 canonicals found, or
          • pd.NA if nothing valid was found.
        """
        s = self.base_clean(s).astype("string").str.strip()

        def norm_cell(val: str):
            # if pd.isna(val) or val == "":
            #     return pd.NA
            if pd.isna(val) or val == "":
                if not self.required and self.unknown_label:
                    return self.unknown_label
                return pd.NA


            cleaned_cell = self._clean(val)
            found: list[str] = []

            # 1) Protected phrases before splitting (optional)
            if self.protected_phrases:
                found.extend(self._protected_hits(cleaned_cell))

            # 2) Split tokens
            tokens = [t.strip() for t in self._splitter.split(val) if t.strip()]

            for tok in tokens:
                key = self._clean(tok)
                if not key:
                    continue

                # exact
                canon = self.accepted.get(key)

                # fuzzy fallback (if enabled)
                if canon is None and self.fuzzy:
                    canon = self._fuzzy_resolve(key)

                if canon:
                    found.append(canon)

            # Dedup preserving order
            seen = set()
            unique = [c for c in found if not (c in seen or seen.add(c))]

            if not unique:
                return pd.NA
            if self.multi_label and len(unique) > 1:
                # Collapse any multi-selection to the aggregate label
                return self.multi_label
            # Single canonical selection
            return unique[0]

        return s.map(norm_cell)

    # --- format ---------------------------------------------------------------

    def format(self, s_norm: pd.Series) -> pd.Series:
        # Now simply returns a single label (or Multi-Racial) per cell
        return s_norm

    # --- indicator expansion --------------------------------------------------

    def indicators(self, s_fmt: pd.Series, dtype: str = "Int64") -> pd.DataFrame:
        """
        Create a one‑hot DataFrame with one column per canonical.

        Because normalize() collapses multi-selections to `multi_label`,
        vectorized get_dummies produces 1-of-N indicators.
        """
        prefix = s_fmt.name
        dummies = s_fmt.fillna("").str.get_dummies(sep=";").astype(dtype)

        # Ensure all canonicals (including multi_label) are present
        canon_sorted = sorted(self.canonicals)
        indicators = dummies.reindex(columns=canon_sorted, fill_value=0)
        indicators.columns = [f"{prefix}_{c}" for c in canon_sorted]
        return indicators
    
    # --- errors ---------------------------------------------------------------

    def errors_df(self, col: str, raw: pd.Series, s_norm: pd.Series,
                  file=None, sheet=None, row_offset: int = 1) -> pd.DataFrame:

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
            columns=["file","sheet","row_number","column","rule","raw_value","normalized"]
        )
    
class categoricalColumn(BaseColumn):

    """
    Validator for limited-response categorical fields.

    Responsibilities:
    - Normalize raw text (case, whitespace, Excel error tokens)
    - Map cleaned text to a canonical accepted value
    - Optionally perform fuzzy matching for near-misses or typos
    - Produce per-row error diagnostics

    Supports two accepted-response formats:
        • list[str] — literal accepted values
        • dict[str, list[str]] — canonical value → alternative spellings/variants

    Attributes:
        required (bool):
            Whether blank values should be treated as validation errors.
        fuzzy (bool):
            Whether to fuzzy-match unmatched responses.
        min_score (int):
            Minimum fuzzy match ratio (0–100) required to accept a match.
        accepted (dict[str, str]):
            Lookup from normalized input → canonical value.
        row_numbers (pd.Series | None):
            Sheet row numbers used to report error locations.
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
        Normalize a categorical column.

        Workflow:
            1. Apply base cleaning (from BaseColumn)
            2. Convert cleaned text into canonical category labels
            3. For unmatched values, attempt fuzzy matching (if enabled)

        Args:
            s (pd.Series):
                Raw column values.

        Returns:
            pd.Series:
                Normalized categorical values (canonical form), or `pd.NA` where
                no acceptable value can be determined.
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
        return s_norm

    # --- errors ---
    def errors_df(self, col: str, raw: pd.Series, s_norm: pd.Series,
                  file=None, sheet=None, row_offset: int = 1) -> pd.DataFrame:

        """
        Construct a DataFrame describing validation errors for this categorical column.

        Error types recorded:
            - "Required but missing": value is missing but field is required
            - "Invalid Value, not in accepted responses": raw value was present
                but could not be mapped (even via fuzzy matching)

        Args:
            col (str):
                Column name being validated.
            raw (pd.Series):
                Original unnormalized values.
            s_norm (pd.Series):
                Normalized categorical values.
            file (str or None):
                Optional file identifier used in reporting.
            sheet (str or None):
                Sheet name for context in error reporting.
            row_offset (int):
                Offset applied when raw indices do not match Excel row numbers.

        Returns:
            pd.DataFrame:
                Structured error report with columns:
                ["file", "sheet", "row_number", "column",
                 "rule", "raw_value", "normalized"]
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
    Column type for categorical fields whose valid responses depend on the
    originating file (e.g., different CBOs use different program names).

    This validator selects the appropriate canonical-to-variant mapping based on
    the provided `file` identifier, normalizes raw text values, and applies
    both exact and optional fuzzy matching to produce consistent categorical
    outputs.

    Expected Structure of accepted_responses:
        {
            "FILE_ID_A": {
                "Canonical Label 1": ["variant1", "v1", ...],
                "Canonical Label 2": ["variant2", "v2", ...],
            },
            "FILE_ID_B": {
                "Canonical Label X": [...],
                ...
            }
        }

    Args:
        accepted_responses (dict):
            Nested dictionary mapping file IDs to canonical labels and their
            allowable variants.
        required (bool, optional):
            If True, missing values are treated as validation errors.
        fuzzy (bool, optional):
            Whether to attempt fuzzy matching for values not in `accepted_responses`.
        min_score (int, optional):
            Minimum fuzzy-match score (0–100) required to accept a near match.
        row_numbers (pd.Series, optional):
            Spreadsheet-aware row references used when constructing error logs.
        file (str, optional):
            File identifier (e.g., "CWP", "BRBC") selecting which accepted-response
            mapping to use.

    Returns:
        This class does not return directly; its methods return normalized Series
        or structured error DataFrames (see below).

    Behavior:
        • Builds a reverse mapping (variant → canonical) for the active file.
        • Cleans raw values (casefold, whitespace collapsing, handling "0"/Excel tokens).
        • Performs exact matches first, then fuzzy matching (if enabled).
        • Returns canonical category labels or `pd.NA` for invalid/unmatched values.
        • Generates structured error reports for:
            - required but missing values
            - invalid or file-incompatible categorical entries

    Side Effects:
        • May raise `ValueError` if `self.file` does not exist in accepted_responses.
        • Uses `row_numbers` to produce precise Excel-style row metadata.

    Notes:
        • File-specific categorical validation is essential when partners use
          distinct naming conventions or inconsistent capitalization/spelling.
        • Fuzzy matching should be used cautiously for fields where misclassification
          has high cost (e.g., credentials, program names).
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
        """Normalize text for lookup."""
        if pd.isna(text):
            return ""
        if re.fullmatch(r"0+", text):
            return ""
        return self._whitespace.sub(" ", str(text)).strip().casefold()

    def normalize(self, s: pd.Series) -> pd.Series:
        """
        Normalize categorical text values based on file-specific accepted responses.
        file_id must match a key in accepted_responses.
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
        """Report missing or invalid categorical entries."""
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
    Column type for Yes/No fields. 
    Accepts common yes/no variants, noramlizes and casts to 1/0.
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
        return(
            s_norm.map({"Yes":1, "No":0}).astype("Int64")
        )
    
    def errors_df(self, col: str, raw: pd.Series, s_norm: pd.Series,
                  file=None, sheet=None, row_offset: int = 1) -> pd.DataFrame:

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
    Column type for parsing, normalizing, and validating date values.

    This validator handles a wide variety of messy real-world date formats,
    including embedded month names, Unicode separators, Excel-style shorthand,
    and inconsistent spacing. It attempts to extract a canonical date in
    ISO format (YYYY-MM-DD), enforcing optional minimum and maximum bounds.

    Behavior Overview:
        • Applies BaseColumn cleaning to remove whitespace, Excel error tokens,
          and placeholder junk.
        • Normalizes text using `_clean_text`, which:
            - Removes invisible unicode characters
            - Converts non-ASCII dashes and separators to "/"
            - Preserves month names (Jan, February, etc.)
            - Extracts ISO (YYYY-MM-DD), US (MM/DD/YYYY), or fallback numeric patterns
        • Converts cleaned strings into pandas datetime objects via
          `pd.to_datetime(..., errors="coerce")`.
        • Flags dates outside the configured allowable range.
        • Supports explicit invalid tokens ("n/a", "null", "NaT", etc.).

    Args:
        required (bool, optional):
            If True, missing values after cleaning generate "Required but missing"
            validation errors.
        min_date (str or None, optional):
            Earliest permissible date (inclusive). If None, no lower bound is applied.
        max_date (str or None, optional):
            Latest permissible date (inclusive). If None, no upper bound is applied.
        row_numbers (pd.Series, optional):
            Excel-style row numbers used when creating error reports. If omitted,
            DataFrame index + `row_offset` is used instead.

    normalize(s):
        • Input:
            s (pd.Series): Raw date values (strings, numerics, mixed).
        • Output:
            pd.Series of pandas datetime64 values or `NaT` where coercion fails.

        Steps:
            1. Base cleaning.
            2. Replace common invalid tokens with NA.
            3. Apply `_clean_text` to extract a date-like pattern.
            4. Parse via `pd.to_datetime`.

    format(s_norm):
        • Formats parsed datetime objects as ISO strings ("YYYY-MM-DD").
        • Missing values are emitted as empty strings.

    errors_df(col, raw, s_norm, file, sheet, row_offset):
        • Constructs a structured DataFrame describing date validation errors.
        • Error categories include:
            - "Required but missing"
            - "Invalid Value, not a valid date"
            - "Invalid Value, date before minimum allowed"
            - "Invalid Value, date after maximum allowed"
        • Output columns:
            ["file", "sheet", "row_number", "column",
             "rule", "raw_value", "normalized"]

        Row numbers use:
            • self.row_numbers (if provided), otherwise
            • DataFrame index + `row_offset`.

    Returns:
        The class does not return values directly, but its methods produce:
            • normalized datetime Series
            • formatted ISO date strings
            • structured validation error DataFrames

    Notes:
        • `_clean_text` attempts to recover dates from extremely irregular input.
        • The validator avoids interpreting 2-digit years heuristically unless
          clearly part of a recognizable MM/DD/YY pattern.
        • Inputs like ".", "---", "/", empty strings, or placeholder artifacts
          are treated as missing.
        • Date ranges allow you to prevent absurd historical values (e.g. 1/1/1895)
          or future dates beyond expected operational windows.
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

        # 5b) handle compact 8-digit numbers without separators
        # Only consider if the entire cleaned string is exactly 8 digits,
        # to avoid matching arbitrary 8-digit chunks within other text.
        m8 = re.fullmatch(r"(\d{8})", cleaned)
        if m8:
            digits = m8.group(1)

            def is_valid_date(y, mo, da):
                try:
                    pd.Timestamp(year=y, month=mo, day=da)
                    return True
                except (ValueError, TypeError):
                    return False

            # first check if MMDDYYYY is plausible
            mo_us = int(digits[0:2])
            da_us = int(digits[2:4])
            y_us  = int(digits[4:8])

            if is_valid_date(y_us, mo_us, da_us):
                return f"{y_us:04d}-{mo_us:02d}-{da_us:02d}"

            # Fallback: try YYYYMMDD if MMDDYYYY isn't valid
            y_iso  = int(digits[0:4])
            mo_iso = int(digits[4:6])
            da_iso = int(digits[6:8])

            if is_valid_date(y_iso, mo_iso, da_iso):
                return f"{y_iso:04d}-{mo_iso:02d}-{da_iso:02d}"

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

        out = s_norm.dt.strftime("%Y-%m-%d")
        return out.fillna("")
    
    # ---- cchecks ----

    def errors_df(self, col: str, raw: pd.Series, s_norm: pd.Series,
                  file=None, sheet=None, row_offset: int = 1) -> pd.DataFrame:
        

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
    Column type for validating and normalizing U.S. ZIP codes.

    This validator supports the two most common ZIP formats used in workforce
    datasets:
        • Standard 5-digit ZIPs (e.g., "06511")
        • 4-digit values that should be left-padded to five digits (e.g., "6877" → "06877")

    Behavior Overview:
        • Applies BaseColumn cleaning (removing whitespace, Excel error tokens, etc.).
        • Optionally strips all non-digit characters (hyphens, spaces) before processing.
        • Normalizes values to string digits or `pd.NA` if unusable.
        • Formats values by:
            - Padding 4-digit ZIPs to 5 digits.
            - Correcting misplaced trailing zeros in some user-entered patterns.
            - Ensuring only valid 5-digit ZIP codes remain in the output.

        • Provides structured validation errors for:
            - Missing required values
            - Non-numeric or improperly formatted ZIP entries

    Args:
        required (bool, optional):
            If True, missing values (after cleaning) generate
            "Required but missing" validation errors.
        strip_formatting (bool, optional):
            If True, remove non-digit characters prior to validation
            (recommended for handling "06-511", "06511 ", "06511-1234", etc.).
        row_numbers (pd.Series, optional):
            Excel row numbers to attach to error output. If omitted,
            DataFrame index + `row_offset` is used.

    normalize(s):
        Normalize raw ZIP values.

        Input:
            s (pd.Series): Raw ZIP values.

        Output:
            pd.Series of cleaned string values (digits only), or `pd.NA` where
            the value cannot be interpreted as a ZIP code.

        Steps:
            1. Base cleaning
            2. Strip formatting (if enabled)
            3. Remove empty strings → set to NA

    validate(s_norm):
        Vectorized boolean test evaluating whether each normalized value is:
            • 5 digits, or
            • NA (if not required)

        Returns:
            pd.Series of bool values indicating validity.

    format(s_norm):
        Convert normalized string digits into final 5-digit ZIPs.

        Logic:
            • 4-digit → left-pad with "0"
            • Overlong patterns ending with unnecessary zeros → corrected
            • Invalid patterns → replaced with `pd.NA`

        Returns:
            pd.Series containing canonical ZIP strings.

    errors_df(col, raw, s_norm, file, sheet, row_offset):
        Produce a structured DataFrame describing ZIP-code validation errors.

        Error types recorded:
            • "Required but missing"
            • "Invalid Value, zipcode must 5 digits (e.g. 06543) or 4 digits (6434)"
              (raised for non-numeric, malformed, or incorrectly sized values)

        Output columns:
            ["file", "sheet", "row_number", "column",
             "rule", "raw_value", "normalized"]

        Row numbers use:
            • `self.row_numbers` if supplied, otherwise
            • DataFrame index + `row_offset`

    Notes:
        • This validator does *not* process ZIP+4 formats (e.g., "06511-1234"),
          but can strip them down if `strip_formatting=True`.
        • ZIP codes beginning with "0" (common in New England) are preserved correctly.
        • Ensures downstream systems receive clean, canonical 5-digit ZIP codes.
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

        s = self.base_clean(s)

        s = (
            s.astype("string")
            .str.replace(r"\s+", " ", regex=True)  # normalize whitespace
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
    Column type for validating and normalizing 7-digit State ID numbers.

    This validator enforces the Connecticut-style “State ID #” format used in
    workforce and education datasets, where each identifier must be exactly
    seven digits (e.g., ``"0123456"``). The column may contain formatting noise
    such as whitespace, decimal artifacts (``"0123456.0"``), or hyphens, all of
    which can be removed prior to validation.

    Behavior Overview:
        • Applies BaseColumn cleaning (strip whitespace, remove Excel error tokens).
        • Optionally removes all non-digit characters (``strip_formatting=True``).
        • Converts values to canonical digit-only strings or `pd.NA`.
        • Validates that final normalized values contain exactly 7 digits.
        • Returns structured error metadata for missing/invalid identifiers.

    Args:
        required (bool, optional):
            If True, missing values (after cleaning and normalization)
            generate a ``"Required but missing"`` error.
        strip_formatting (bool, optional):
            If True, remove non-digit characters such as hyphens, spaces,
            and decimal suffixes (e.g., convert ``"0123456.0"`` → ``"0123456"``).
        row_numbers (pd.Series, optional):
            Excel row numbers aligned with the Series index. Used to populate
            the ``row_number`` field in error logs.

    normalize(s):
        Normalize raw State ID values.

        Steps:
            1. Apply BaseColumn cleaning.
            2. Strip whitespace and optional formatting noise.
            3. Remove non-digit characters.
            4. Convert empty strings to `pd.NA`.

        Returns:
            pd.Series of cleaned digit strings or `pd.NA`.

    validate(s_norm):
        Validate that each normalized value matches the required pattern.

        Requirements:
            • Exactly seven digits (``"\\d{7}"``)
            • OR NA if not required

        Returns:
            pd.Series of boolean indicators.

    format(s_norm):
        Return final formatted values.

        Notes:
            • No auto-padding is performed.
            • Valid inputs must already be seven digits.
            • Returned values are suitable for reporting and database storage.

    errors_df(col, raw, s_norm, file, sheet, row_offset):
        Construct a structured DataFrame of validation errors.

        Error types recorded:
            • ``"Required but missing"`` — value missing when `required=True`
            • ``"Invalid Value, State ID must be 7 Digits (e.g. '0123456')"`` —
              triggered for:
                • Non-empty raw inputs that do not normalize to 7 digits
                • Values that normalize to NA but were present in raw form

        Output columns:
            ["file", "sheet", "row_number", "column",
             "rule", "raw_value", "normalized"]

        Row number logic:
            • Use `self.row_numbers` if supplied,
            • Otherwise fall back to DataFrame index + ``row_offset``.

    Notes:
        • State IDs may begin with leading zeros, which are preserved.
        • This validator does not support alphanumeric IDs.
        • Downstream systems should rely on normalized output for uniqueness checks.
    """

    name = "state_id_7"
    _non_digits = re.compile(r"\D+")

    def __init__(self, 
                 required: bool = False, 
                 strip_formatting: bool = True, 
                 row_numbers = None):

        """
        required = True -> blank after cleaning counts as an error 
        strip_formatting -> remove hyphens/spaces/etc. before validating
        """

        self.required = required
        self.strip_formatting = strip_formatting
        self.row_numbers = row_numbers

    # ---- Step 1: normalize (vectorized) ----

    def normalize(self, s: pd.Series) -> pd.Series:

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
        ok_pattern = s_norm.str.fullmatch(r"\d{7}", na=False)
        ok_required = ok_pattern & (~s_norm.isna() if self.required else True)
        return ok_required
    
    def format(self, s_norm: pd.Series) -> pd.Series:
        # We don't auto-pad; must already be 7 digits to be considered valid. 
        # Return the normalized value as the final, canonical display. 
        return s_norm
    
    def errors_df(self, col: str, raw: pd.Series, s_norm: pd.Series, file = None, sheet = None, row_offset: int=1) -> pd.DataFrame:

        masks = {
            "Required but missing": s_norm.isna() & raw.isna() if self.required else pd.Series(False, index = s_norm.index),
            "Invalid Value, State ID must be 7 Digits (e.g. '0123456')": s_norm.notna() & ~s_norm.str.fullmatch(r"\d{7}"),
            "Invalid Value, State ID must be 7 Digits (e.g. '0123456')": s_norm.isna() & raw.notna()
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
    Column type for CIP (Classification of Instructional Programs) codes.

    This validator normalizes and validates CIP codes to one of the three
    canonical forms defined by NCES:

        • ``DD``           — 2-digit “CIP Series”
        • ``DD.DD``        — 4-digit “CIP Subseries”
        • ``DD.DDDD``      — 6-digit “CIP Program”

    It also supports multi-valued cells (e.g., several CIP codes separated by
    commas, semicolons, or whitespace) and outputs them as a semicolon-delimited
    string in normalized form.

    Behavior Overview:
        • Applies BaseColumn cleaning (strip whitespace, replace Excel errors).
        • Splits multi-code entries on common separators.
        • Removes all characters except digits and periods.
        • Automatically converts common malformed forms into canonical patterns:

              - ``"151201"``     → ``"15.1201"``
              - ``"1512"``       → ``"15.12"``
              - ``"15.120100"``  → ``"15.1201"``
              - ``"15 12"``      → ``"15.12"``

        • Drops unparseable junk codes.
        • Produces ``pd.NA`` if no valid CIP codes remain.

    Args:
        required (bool, optional):
            If True, missing values after normalization generate a
            ``"Required but missing"`` validation error.
        row_numbers (pd.Series, optional):
            Excel row numbers aligned to Series indices. Used to populate the
            ``row_number`` field in error logs.

    normalize(s):
        Normalize raw CIP code strings.

        Steps:
            1. Apply BaseColumn cleaning and strip floating-point suffixes.
            2. Split each entry into candidate codes.
            3. Sanitize by removing non-digit/non-dot characters.
            4. Attempt to coerce each candidate into a canonical CIP format.
            5. Recombine valid codes as a semicolon-delimited string.

        Returns:
            pd.Series:
                Normalized CIP code strings, or ``pd.NA`` if no valid codes
                could be derived.

    format(s_norm):
        Formatting step; returns normalized CIP strings unchanged.

    errors_df(col, raw, s_norm, file, sheet, row_offset):
        Construct a structured DataFrame of validation errors.

        Error types recorded:
            • ``"Required but missing"`` —
                Value is empty after cleaning but column is marked required.
            • ``"Invalid Value, must match CIP format (e.g. '15', '15.12', '15.1201')"`` —
                Triggered when:
                    – raw data is present but normalization fails, or
                    – one or more CIP codes in a multi-code cell do not
                      conform to allowed patterns.

        Validation rule:
            All CIP codes within a cell must match one of the canonical patterns
            (2-digit, 4-digit with dot, or 6-digit with dot). If any code is invalid,
            the entire cell is flagged.

        Returns:
            pd.DataFrame with columns:
                ["file", "sheet", "row_number", "column",
                 "rule", "raw_value", "normalized"]

        Row number logic:
            • If ``row_numbers`` was supplied, values are pulled from it.
            • Otherwise, row numbers default to ``index + row_offset``.

    Notes:
        • This validator checks *format only* — it does not confirm that a CIP
          code exists in the official NCES taxonomy.
        • Empty or malformed codes are silently skipped during normalization.
        • Use semicolon-delimited output for downstream exploding or mapping.
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
        return s_norm

    # --- errors ---
    def errors_df(self, col: str, raw: pd.Series, s_norm: pd.Series,
                  file=None, sheet=None, row_offset: int = 1) -> pd.DataFrame:

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
            ),
            "Invalid Value, must match CIP format (e.g. '15', '15.12', '15.1201')": (
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
    Column type for hourly wage fields.

    This validator extracts and validates hourly wage values expressed as
    free-text, stripping currency symbols and extraneous wording while enforcing
    configurable minimum and maximum wage thresholds.

    Unlike typical numeric validators, this class *explicitly detects wage ranges*
    (e.g., ``"15-20"``, ``"12/15"``, ``"10 to 12"``). Ranges are not coerced and are
    instead surfaced as validation errors because they represent ambiguous or
    non-atomic wage entries.

    Behavior Overview:
        • Applies BaseColumn cleaning (remove Excel error tokens, strip whitespace).
        • Detects and flags wage *ranges* via regular expressions.
        • Removes currency symbols and common unit labels (e.g. ``"per hr"``).
        • Strips all non-numeric characters except the decimal point.
        • Parses remaining text into a float (e.g., ``"$17" → 17.0``).
        • Values of ``0`` are treated as missing (commonly an encoding issue).
        • Formatting step outputs wages as ``"$17.00"``.

    Args:
        required (bool, optional):
            If True, missing values after cleaning generate a
            ``"Required but missing"`` validation error.
        min_wage (float, optional):
            Lower bound for valid wages. Values below this threshold raise the
            error ``"Invalid Value, must be >= $X.XX"``.
        max_wage (float, optional):
            Upper bound for reasonable wages. Values above this threshold trigger
            a *confirmation* warning rather than a hard failure.
        row_numbers (pd.Series, optional):
            Excel row numbers used for reporting. If None, row numbers default to
            ``index + row_offset``.

    normalize(s):
        Normalize free-text wage values into numeric floats.

        Steps:
            1. Lowercase and trim text.
            2. Detect ranges using ``self._range_pattern`` and preserve the raw
               value for error classification.
            3. Remove currency symbols, “hr”/“hourly”/“per hr”, etc.
            4. Strip all non-digit / non-decimal characters.
            5. Convert to float; invalid or zero values → ``pd.NA``.

        Returns:
            pd.Series:
                Floats representing hourly wages, or ``pd.NA`` where the value is
                missing, invalid, or a detected range.

    format(s_norm):
        Convert normalized floats into ``"$XX.XX"`` formatted strings.

        Returns:
            pd.Series of strings or ``pd.NA`` for missing values.

    errors_df(col, raw, s_norm, file, sheet, row_offset):
        Construct a structured DataFrame of validation errors.

        Error types recorded:
            • ``"Required but missing"`` —
                  Value is empty after normalization and column is required.
            • ``"Invalid Value, must be >= $min_wage"`` —
                  Wage is below the configured lower bound.
            • ``"Confirmation required, unusually high (> $max_wage)"`` —
                  Wage exceeds typical labor-market ranges; not technically invalid
                  but requires human review.
            • ``"Invalid Value, must be a number indicating hourly wage"`` —
                  Raw value exists but cannot be parsed (including detected ranges).

        Range handling:
            • Any raw entry matching the range pattern (e.g. ``"15-20"``, ``"14/16"``,
              ``"10 to 12"``) is automatically flagged in the last category.

        Returns:
            pd.DataFrame:
                A structured table with columns:
                    ["file", "sheet", "row_number",
                     "column", "rule", "raw_value", "normalized"]

        Row number logic:
            • Uses ``row_numbers`` when provided.
            • Otherwise computes ``index + row_offset``.

    Notes:
        • This validator enforces *atomic* wage entries — ranges must be corrected
          manually before analysis.
        • Currency formatting is normalized consistently in `format()`.
        • ``0`` is treated as missing because spreadsheets sometimes export empty
          wage cells as ``0`` when coerced to numeric types.
    """

    name: str = "hourly_wage"

    def __init__(self, required: bool = False, min_wage: float = 5.0, max_wage: float = 45.0, row_numbers = None):
        self.required = required
        self.min_wage = 5.0 if min_wage is None else min_wage
        self.max_wage = 45.0 if max_wage is None else max_wage
        self._pattern_strip = re.compile(r"[^0-9\.]")  # strip everything except digits and dot
        self._range_pattern = re.compile(r"\d+\s*[-/]\s*\d+|\d+\s+to\s+\d+", re.IGNORECASE)
        self.row_numbers = row_numbers

    # --- normalize ---
    def normalize(self, s: pd.Series) -> pd.Series:
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
        return s_norm.map(lambda x: f"${x:.2f}" if isinstance(x, float) else pd.NA)

    # --- errors ---
    def errors_df(self, col: str, raw: pd.Series, s_norm: pd.Series,
                  file=None, sheet=None, row_offset: int = 1) -> pd.DataFrame:

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
    Column type for hours-worked fields.

    This validator parses typical weekly or program hours from free-text inputs,
    enforcing numeric constraints and reasonable upper bounds (e.g., ``<= 80``).
    All values are cleaned, coerced to floats when possible, and validated
    against minimum/maximum thresholds.

    Behavior Overview:
        • Applies BaseColumn cleaning (strip whitespace, remove Excel error tokens).
        • Converts valid numeric strings into floats.
        • Treats empty strings, whitespace-only values, and failed parses as ``pd.NA``.
        • Enforces non-negative hours.
        • Enforces a configurable maximum (default: 80 hours).
        • Formatting step converts whole-number floats to integers for cleaner output.

    Examples of accepted inputs:
        ┌──────────────┬────────────────────────────┐
        │ Raw Input     │ Normalized Representation  │
        ├──────────────┼────────────────────────────┤
        │ "40"          │ 40                         │
        │ "37.5"        │ 37.5                       │
        │ "  15  "      │ 15                         │
        │ "" / " "      │ NA                         │
        │ "abc"         │ NA (with validation error) │
        └──────────────┴────────────────────────────┘

    Args:
        required (bool, optional):
            If True, missing values after cleaning generate a
            ``"Required but missing"`` validation error.
        max_hours (int, optional):
            Upper bound for reasonable reported weekly hours.
            Values exceeding this threshold are considered invalid.
        row_numbers (pd.Series, optional):
            Excel row numbers for accurate error reporting.
            If None, row numbers default to ``index + row_offset``.

    normalize(s):
        Normalize free-text hour values to numeric form.

        Steps:
            1. Clean via `BaseColumn.base_clean()`.
            2. Strip whitespace and coerce to float using a safe converter.
            3. Invalid numbers or blank values → ``pd.NA``.

        Returns:
            pd.Series of floats or ``pd.NA`` values.

    format(s_norm):
        Format normalized numeric values.

        • Whole-number floats are converted to integers (e.g., ``40.0 → 40``).
        • Fractional hours remain floats (e.g., ``37.5``).

        Returns:
            pd.Series with cleaned numeric values.

    errors_df(col, raw, s_norm, file, sheet, row_offset):
        Produce a structured error report for invalid hour entries.

        Error types recorded:
            • ``"Required but missing"`` —
                  No usable value and field is required.
            • ``"Invalid Value, must be non-negative"`` —
                  Negative hours such as ``-5``.
            • ``"Invalid Value, cannot exceed X hours"`` —
                  Hours greater than ``max_hours`` (e.g., > 80).
            • ``"Invalid Value, must be a number indicating typical weekly hours"`` —
                  Raw input exists but could not be parsed to a number.

        Returns:
            pd.DataFrame with columns:
                ["file", "sheet", "row_number",
                 "column", "rule", "raw_value", "normalized"]

        Row number handling:
            • Uses `row_numbers` when supplied.
            • Otherwise computes row numbers from index + `row_offset`.

    Notes:
        • This validator treats ambiguous or text-based entries (e.g. "a lot")
          as invalid unless manually corrected by the user.
        • Hours are assumed to refer to *weekly* or *program* hours and therefore
          constrained to realistic ranges.
    """

    name: str = "hours_worked"

    def __init__(self, required: bool = False, max_hours: int = 80, row_numbers = None):
        self.required = required
        self.max_hours = max_hours
        self.row_numbers = row_numbers

    # --- normalize ---
    def normalize(self, s: pd.Series) -> pd.Series:
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
        return s_norm.map(lambda x: int(x) if pd.notna(x) and float(x).is_integer() else x)

    # --- errors ---
    def errors_df(self, col: str, raw: pd.Series, s_norm: pd.Series,
                  file=None, sheet=None, row_offset: int = 1) -> pd.DataFrame:

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
    Column type for NAICS (North American Industry Classification System) codes.

    This validator parses and normalizes NAICS industry codes as 2–6 digit
    numeric identifiers, supporting a wide range of common input formats
    (e.g., "31", "31151", "311513", "311513.0", "311/3115", "31; 311; 31151" ).

    Behavior Overview:
        • Applies BaseColumn cleaning (strip whitespace, remove Excel errors).
        • Strips non-numeric characters, removes decimal suffixes, and splits
          multi-code entries on common delimiters (comma, semicolon, slash, spaces).
        • Accepts any valid NAICS code length (2, 3, 4, 5, or 6 digits).
        • Filters out malformed or ambiguous codes.
        • Produces a semicolon-delimited list for rows containing multiple codes.

    Examples of valid normalized outputs:
        ┌───────────────────────┬────────────────────────────┐
        │ Raw Input             │ Normalized Output          │
        ├───────────────────────┼────────────────────────────┤
        │ "31151"               │ "31151"                    │
        │ "311513.0"            │ "311513"                   │
        │ "31/311/3115"         │ "31;311;3115"              │
        │ "31151300"            │ "311513" (trailing zeros)  │
        │ "" / " " / None       │ NA                         │
        └───────────────────────┴────────────────────────────┘

    Args:
        required (bool, optional):
            If True, missing values after normalization generate a
            ``"Required but missing"`` validation error.
        row_numbers (pd.Series, optional):
            Spreadsheet row numbers for accurate error reporting. If not
            provided, error logs compute row numbers from index + ``row_offset``.

    normalize(s):
        Normalize raw NAICS entries to 2–6 digit codes.

        Steps:
            1. Apply BaseColumn cleaning.
            2. Remove junk characters & decimal portions.
            3. Split multi-code entries on common delimiters.
            4. Keep only numeric strings of length 2–6.
            5. Collapse malformed entries to ``pd.NA``.

        Returns:
            pd.Series of semicolon-delimited valid NAICS codes,
            or ``pd.NA`` where no valid codes are detected.

    format(s_norm):
        Return normalized NAICS codes unchanged (no further formatting applied).

    errors_df(col, raw, s_norm, file, sheet, row_offset):
        Construct a structured error report describing invalid NAICS codes.

        Error types recorded:
            • ``"Required but missing"`` —
                  Field is required but no usable value exists.
            • ``"Invalid Value, must match NAICS format (e.g. '31', '31151', '311513')"`` —
                  Raw values present but not convertible into any valid NAICS code, or
                  normalized values that fail the 2–6 digit rule.

        Returns:
            pd.DataFrame with columns:
                ["file", "sheet", "row_number",
                 "column", "rule", "raw_value", "normalized"]

        Row-number logic:
            • Uses provided ``row_numbers`` when available.
            • Falls back to index + ``row_offset`` for consistent reporting.

    Notes:
        • NAICS codes represent hierarchical sectors (2 digits → broad, 6 digits → detailed).
        • This validator tolerates multi-code entries but does not attempt semantic
          validation beyond confirming valid digit lengths.
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
        return s_norm

    # --- errors ---
    def errors_df(self, col: str, raw: pd.Series, s_norm: pd.Series,
                  file=None, sheet=None, row_offset: int = 1) -> pd.DataFrame:

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

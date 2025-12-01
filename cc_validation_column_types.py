import pandas as pd 
from rapidfuzz import process, fuzz
import re
import unicodedata 

class BaseColumn:
    
    ERROR_TOKENS =  {"#VALUE!","#REF!","#DIV/0!","#NAME?","#NULL!","#NUM!","#N/A",
        "nan","<NA>","NaN","null"}
    
    def base_clean(self, s: pd.Series) -> pd.Series:
        s = s.astype("string")
        s = s.str.strip().replace("", pd.NA)
        s = s.replace(r"^\s*$", pd.NA, regex=True)
        s = s.replace(self.ERROR_TOKENS, pd.NA)
        return s

class categoricalColumn(BaseColumn):

    """
    Column type for limited-response categorical fields.
    Normalizes, validates against accepted responses, and can fuzzy match typos.
    """

    def __init__(self, accepted_responses: list[str], required: bool = False,
                 fuzzy: bool = True, min_score: int = 90, row_numbers = None):
        """
        accepted_responses -> canonical list of valid responses
        required -> blank counts as an error if True
        fuzzy -> allow fuzzy matching of near misses
        min_score -> threshold for fuzzy matches (0-100)
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

    def _clean(self, text: str) -> str:
        """Standardize case + whitespace for lookup."""
        if text is None:
            return ""
        if pd.isna(text):
            return ""
        if re.fullmatch(r"0+", text):
            return ""
        return self._whitespace.sub(" ", str(text)).strip().casefold()
    
    # --- normalize ---
    def normalize(self, s: pd.Series) -> pd.Series:
        
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
    Column type for file-specific categorical mappings.
    Each file_id (e.g., 'BRBC', 'CWP', etc.) has its own canonical-to-variant map.

    ### Note that this requires a special accepted response structure to account for the file specific values. 

    Example accepted_responses structure:
    {
        "BRBC": {
            "Intro to Manufacturing": ["intro to manufacturing", "intro to manufacturing (hcc)"],
            "SolidWorks": ["solidworks"]
        },
        "CWP": {
            "Medical Assistant": ["medical assistant", "med asst"]
        }
    }
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
    Column type for free-text identifiers.
    Normalizes by lowercasing, trimming, and collapsing whitespace.
    Treats whitespace-only values as missing but not as formatting errors.
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
            "yes": "Yes", "y": "Yes", "true": "Yes", "1": "Yes",
            "no": "No", "n": "No", "false": "No", "0": "No"
        }
        self.row_numbers = row_numbers

    def normalize(self, s: pd.Series) -> pd.Series: 

        s = self.base_clean(s)
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
    Column Type for Dates 
    Must include month, day, and year and not be an unrealistic value like 1/1/1895 
    """

    name: str = "date_time"
    
    def __init__(self, 
                 required: bool = False, 
                 min_date: str| None = "1900-01-01", 
                 max_date: str|None = "2100-12-31",
                 row_numbers = None):
        
        """
        required = True -> blank after cleaning counts as an error 
        min_date, max_date -> bounds for validation 
        """

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
    Column Type for Zip Codes
    Rule: Value must be either 5 digits "06877" or four digits to be padded to five, "6877" 
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

    def normalize(self, 
                  s: pd.Series) -> pd.Series: 

        s = self.base_clean(s)
        s = s.astype("string").str.strip()
        if self.strip_formatting:
            s = s.fillna("").str.replace(self._non_digits,"",regex=True)
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
            "Invalid Value, zipcode must 5 digits (e.g. 06543) or 4 digits (6434)": s_norm.notna() & ~s_norm.str.fullmatch(r"\d{4,5}"),
            "Invalid Value, zipcode must 5 digits (e.g. 06543) or 4 digits (6434)": s_norm.isna() & raw.notna()
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
    Column Type for "State ID #" 
    Rule: value must be exactly seven digits (eg. '0123456')
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
    Column type for O*NET-SOC codes.
    Validates and auto-formats codes to 'DD-DDDD.DD' (e.g. '15-2051.00').
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
    Column type for CIP codes (Classification of Instructional Programs).
    Validates and auto-formats to 'DD', 'DD.DD', or 'DD.DDDD' forms.
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
    Column type for hourly wages.
    Cleans currency symbols/text and validates against reasonable wage ranges.
    Rejects ranges like '15-20', '12/15', '10 to 12' with a dedicated error.
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
    Column type for hours worked.
    Must be numeric, non-negative, and <= 80.
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
    Column type for NAICS codes (North American Industry Classification System).
    Validates and auto-formats to 2–6 digit numeric codes.
    Accepts common delimiters and strips extra characters.

    Examples of valid normalized outputs:
        '31', '311', '3115', '31151', '311513'
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


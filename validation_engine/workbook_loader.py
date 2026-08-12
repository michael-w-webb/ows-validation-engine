"""
Workbook Loading and Preprocessing Utilities
============================================

This module provides high-reliability tools for loading CareerConneCT / GJC Excel
workbooks in environments where files may be protected, contain inconsistent
schemas, differ across organizations, or be intermittently locked by OneDrive
or user activity. It handles:

1. **Excel COM automation**  
   - Unprotecting sheets
   - Unhiding sheets
   - Saving and stabilizing workbook visibility  
   - Robust initialization and teardown of `win32com` Excel instances

2. **Dynamic or static sheet loading**
   - Retry logic for transient `PermissionError` (common with OneDrive syncing)
   - Config-driven `starting_row`, `starting_column`, and `columns_used`
   - Header extraction using noisy, variant-aware matching against canonical labels

3. **Key creation**
   - Optional integration with :class:`KeyCreator` for row-level ID generation
   - Automatic dropping of invalid rows (e.g., non-alphabetic name fields)
   - Provenance tagging (e.g., file-of-origin for multi-workbook ingestion)

4. **Multi-workbook concatenation**
   - Load multiple files for a single organization or reporting period
   - Merge sheets across files while preserving source metadata
   - Final de-duplication and index resetting

Major Components
----------------

Functions
~~~~~~~~~
- ``ensure_unprotected_visible``  
  Unprotects and unhides all sheets in a workbook using Excel COM.

- ``extract_columns_noisy``  
  Maps messy/variant Excel headers to canonical labels using normalization
  and tolerant matching. Useful for inconsistent partner submissions.

- ``clean_text``  
  Basic string cleaning for Excel messiness (nonbreaking spaces, stray encodings).

Classes
~~~~~~~
- :class:`WorkbookLoader`  
  Loads a single workbook according to a schema-defined set of sheets.
  Handles COM preprocessing (optional), header extraction, dynamic column mapping,
  and row-level cleanup + key creation.

- :class:`MultiWorkbookLoader`  
  Loads and concatenates multiple workbooks that conform to the same schema.
  Useful for partners who submit multiple files by region, cohort, or location.

Typical Workflow
----------------
1. Preprocess the workbook (unprotect/hide/clean).
2. Read each configured sheet using pandas.
3. Apply canonical header mapping (dynamic or fixed).
4. Insert ``id_key`` or other KeyCreator-derived identifiers.
5. Clean unusable rows (blank/invalid names).
6. Return ``dict[sheet_name → DataFrame]`` to the validation engine.

Dependencies
------------
- pandas
- win32com (Excel COM automation)
- pythoncom
- traceback / datetime / os / time
- KeyCreator (optional row-level ID generator)
- strict_alphabetic_normalize (optional row filtering helper)

Notes
-----
This module assumes:
- Windows environment (due to COM).
- Excel is installed.
- User has permissions to unprotect sheets (passwords may vary per program).
- The provided `sheet_defs` schema contains label specifications and 
  starting rows/columns.

It is intentionally robust against inconsistent partner data submissions,
permission locks, and malformed Excel headers.
"""

from multiprocessing.util import debug

import pandas as pd 
import os
import win32com.client as win32
import time
import traceback
from datetime import datetime
import pythoncom
import win32com.client

from validation_engine.key_creator import KeyCreator
from validation_engine.standard_normalizations import strict_alphabetic_normalize
from validation_engine.validation_column_concept_classes import concept_classes

def ensure_unprotected_visible(excel, file_path, password="workforce"):
    """
    Open an Excel workbook via COM automation, unprotect all sheets, and make them visible.

    This utility is designed for partner-submitted CareerConneCT/GJC workbooks that may
    arrive locked, password-protected, or with hidden sheets. It modifies the file
    *in-place*, ensuring that all sheets can be read downstream by pandas.

    The function:
      1. Opens the workbook using a provided Excel COM instance.
      2. Attempts to unprotect the workbook-level protection (if present).
      3. Iterates through all worksheets:
         - Unprotects each sheet using the provided password.
         - Sets sheet visibility (``ws.Visible = -1``).
      4. Saves the workbook.
      5. Ensures proper cleanup and closes the workbook object in a ``finally`` block.

    Args:
        excel:
            An active ``win32com.client.Dispatch("Excel.Application")`` instance.
            The caller is responsible for creating and later quitting this instance.
        file_path (str):
            Absolute path to the Excel file to modify.
        password (str, optional):
            Password used to unprotect sheets and workbooks. Defaults to ``"workforce"``.

    Returns:
        str:
            The original ``file_path`` (for chaining or logging).

    Side Effects:
        - Modifies the workbook on disk (saves changes immediately).
        - Unhides all sheets.
        - Removes sheet- and workbook-level protection when the password matches.
        - Prints status messages and warnings to stdout.

    Raises:
        None explicitly. Errors during unprotect/unhide operations are caught and logged.
        Non-COM failures during file opening may propagate.

    Notes:
        - This function assumes a Windows environment with Microsoft Excel installed.
        - If the supplied password is incorrect, sheets may remain protected.
        - Hidden sheets that are explicitly "very hidden" (xlSheetVeryHidden = 2)
          can still be unhidden using this approach unless protected.
        - Caller must ensure ``excel.Quit()`` is eventually called.
    """
    def retry(call, attempts=5, delay=0.4):
        for _ in range(attempts):
            try:
                return call()
            except Exception:
                time.sleep(delay)
        raise
        
    wb = None
    try:
        print(f"🔓 Unprotecting and unhiding sheets in: {file_path}")
        wb = excel.Workbooks.Open(file_path, UpdateLinks=0)
        time.sleep(0.5)
        # Unprotect the workbook itself (if protected)
        try:
            wb.Unprotect(password or "")
        except Exception:
            pass

        for ws in wb.Worksheets:
            try:
                ws.Unprotect(password or "")
            except Exception:
                pass
            try:
                ws.Visible = -1  # xlSheetVisible = -1
            except Exception as e:
                print(f"⚠️ Could not unhide {ws.Name}: {e}")

        wb.Save()
        print(f"✔ Workbook unprotected and saved: {file_path}")
        return file_path

    finally:
        if wb:
            try:
                retry(lambda: wb.Close(SaveChanges=1))
            except Exception as e:
                print(f"⚠️ Workbook did not close cleanly: {e}")

def warn_suffix_duplicates(raw_df, col_map, debug=False):
    """
    Warn the user if the Excel file contains multiple columns that appear to be
    unintentional duplicates based on suffixes like '.1', '.2', '.3'**.

    This helper does NOT modify header matching logic or consolidation behavior.
    Its ONLY job is to notify the user that the input workbook may contain
    unexpected duplicate columns.

    Why this helper exists
    -----------------------
    Pandas automatically appends numeric suffixes such as '.1', '.2', '.3' when
    an Excel file contains multiple columns with identical names. For example:

        Excel headers:
            "Date of Birth (MM/DD/YYYY)"
            "Date of Birth (MM/DD/YYYY)"
            "Date of Birth (MM/DD/YYYY)"

        Pandas becomes:
            "Date of Birth (MM/DD/YYYY)"
            "Date of Birth (MM/DD/YYYY).1"
            "Date of Birth (MM/DD/YYYY).2"

    In many submissions, this indicates that the workbook definitions
    should be updated to account for the suffixes in order to consolidate
    or there are unintended duplicate columns.

    This function alerts the user in these cases.

    What counts as a suspicious duplicate?
    --------------------------------------
    A group of duplicate columns will trigger a **warning** when:

        1. 2 or more raw columns differ ONLY by suffix ('.1', '.2', '.3'), AND
        2. All of the full column names (including suffix) are **NOT** explicitly listed
           as valid variants in `col_map`.

    Otherwise:
        - If duplicates ARE explicitly defined in col_map → no warning.
        - If duplicates do not relate to any canonical variant → only debug log.

    Examples
    --------
    Example 1: Suspicious duplicates (warning printed)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        col_map = {
            "Client Date of Birth": [
                "Date of Birth",
                "Date Of Birth",
                "Date of Birth (MM/DD/YYYY)"
            ]
        }

        Excel file contains:
            "Date of Birth (MM/DD/YYYY)"
            "Date of Birth (MM/DD/YYYY).1"
            "Date of Birth (MM/DD/YYYY).2"

        None of the suffix variants ('.1', '.2') are defined in col_map,
        therefore the user receives:

            [WARN] Possible unintended duplicate columns detected for
                   'date of birth (mm/dd/yyyy)': [...]

        This helps the user correct their workbook definitions or review the file.

    Example 2: Intentional duplicates (NO warning)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        col_map = {
            "Client Date of Birth": [
                "DOB Partner Enhanced",
                "DOB Partner Enhanced.1",
                "DOB Partner Enhanced.2"
            ]
        }

        Excel file contains:
            "DOB Partner Enhanced"
            "DOB Partner Enhanced.1"
            "DOB Partner Enhanced.2"

        All duplicates appear intentionally in col_map → NO warning printed.

    Parameters
    ----------
    raw_df : pd.DataFrame
        Raw DataFrame read from Excel BEFORE normalization or mapping.
    col_map : dict
        Canonical → [variant names]. Variants are normalized and compared to
        the base column names extracted from the raw DataFrame.

    Returns
    -------
    None
        This function prints warnings but does not modify the DataFrame.
    """

     # Build normalized sets of *all* explicitly defined variants
    defined_variants_norm = {
        str(v).strip().lower()
        for variants in col_map.values()
        for v in variants
    }

    seen = {}

    for raw_col in raw_df.columns:
        raw_str = str(raw_col)
        norm = raw_str.strip().lower()

        # Detect numeric suffix (e.g. ".1", ".2", ".10")
        if "." in norm:
            base, suffix = norm.split(".", 1)
            if suffix.isdigit():
                # Only treat this as a duplicate if suffix is numeric
                seen.setdefault(base, []).append(raw_str)
                continue

        # Non-numeric prefix OR no dot → treat column as its own base
        seen.setdefault(norm, []).append(raw_str)

    # Check for suspicious duplicates
    for base, cols in seen.items():

        # Check which of the duplicate columns are explicitly defined variants
        normalized_dup_cols = [str(c).strip().lower() for c in cols]
        count_defined = sum(1 for c in normalized_dup_cols if c in defined_variants_norm)
        total_cols = len(cols)

        # If there are duplicates and not all are defined, print warning.
        if total_cols > 1 and total_cols != count_defined:
            print(
                f"[WARN] Possible unintended duplicate columns detected for '{base}':\n"
                f"       {cols}\n"
                f"       Some or all of these columns are not present in workbook definitions.\n"
                f"       Consider updating workbook definitions with suffixes to allow for consolidation."
            )

def extract_columns_noisy(raw_df: pd.DataFrame, col_map: dict, accepted_responses: dict, preview_rows: int = 5, debug: bool = False):
    """
    Select and reorder columns from a messy Excel DataFrame using a canonical-to-variants
    mapping, with tolerant header matching and optional debug output.

    This function is designed for partner-submitted Excel files where header labels may
    vary across submissions (e.g., ``"First Name"``, ``"FirstName"``, ``"FName"``).
    It normalizes the raw column headers (strip + lowercase), then matches them against
    a set of variants for each canonical label in ``col_map``. For each canonical label:

    * If a matching header is found, that column is selected.
    * If no matching header is found, a column of ``NA`` is inserted.
    * Columns are returned in the order of keys in ``col_map``.

    The result is:
    * A DataFrame containing the selected/reordered columns, with **integer** column
    labels (0..n-1) suitable for downstream relabeling.
    * The list of canonical labels corresponding to those columns.

    Args:
        raw_df (pd.DataFrame):
            Raw DataFrame read from Excel. Column names are treated as-is and
            normalized internally via ``str(c).strip().lower()``.
        col_map (dict):
            Mapping of canonical column labels to one or more possible header variants.
            Example:

            .. code-block:: python

                col_map = {
                    "First Name": ["First Name", "FirstName", "FName"],
                    "Last Name":  ["Last Name", "Surname", "LName"],
                }
        accepted_responses (dict):
            Mapping of canonical column labels to dict of col concept class, col type, and accepted responses
        preview_rows (int, optional):
            Number of rows to show in the debug preview of ``raw_df``. Default is 5.
        debug (bool, optional):
            If True, prints detailed information about header normalization,
            matches/misses, and NA-only columns. Default is True.

    Returns:
        tuple[pd.DataFrame, list[str]]:
            - df_no_headers:
                DataFrame containing the selected columns in the order of ``col_map``.
                Columns are relabeled to consecutive integers starting at 0.
            - canonical_labels:
                List of canonical column labels corresponding to the columns in
                ``df_no_headers``.
            - canonical_labels_present:
                List of canonical column labels that were found in the raw_df and are present in the final DataFrame.

    Notes:
        - If no variant for a canonical label is found in ``raw_df``, the corresponding
        column in ``df_no_headers`` will be entirely ``NA``.
        - Duplicate normalized header names in ``raw_df`` are reported via debug
        messages, but only the first occurrence is used.
        - This function does not mutate ``raw_df``.
    """

    if debug:
        print("\n=== [extract_columns] START ===")
        print(f"[shape] raw_df.shape = {raw_df.shape}")

        # Show raw_df columns as strings
        raw_cols_as_str = [str(c) for c in raw_df.columns.tolist()]
        print(f"[cols] raw_df.columns (as str, count={len(raw_cols_as_str)}): {raw_cols_as_str[:30]}")
        if len(raw_cols_as_str) > 30:
            print("       ... (truncated)")


    # Warn user about suffix-based duplicates (does not affect matching) so they can update workbook definitions if needed.
    # This is necessary if user wants to c
    warn_suffix_duplicates(raw_df, col_map=col_map, debug=debug)

    # Build normalization map: normalized -> original
    norm_cols = {}
    for c in raw_df.columns:
        key = str(c).strip().lower()

        # Store ALL raw columns under same normalized key
        if key not in norm_cols:
            norm_cols[key] = [c]         # now a list
        else:
            if debug:
                print(f"[warn] duplicate normalized header: '{key}' now maps to: {norm_cols[key]}")

    if debug:
        # Show a few normalized keys
        sample_norm = list(norm_cols.keys())[:30]
        print(f"[norm map] sample normalized keys (count={len(norm_cols)}): {sample_norm}")
        if len(norm_cols) > 30:
            print("           ... (truncated)")

    selected_cols = []
    canonical_labels = [] # This list will contain all canonical_labels in the workbook defintions.
    canonical_labels_present = [] # This list will contain all canonical lables in the workbook definitions that are present in the file.
    matched_count = 0
    missing_count = 0

    # Optional preview of data
    if debug:
        try:
            print("[preview] top rows of raw_df (first 5 cols shown):")
            print(raw_df.iloc[:preview_rows, :min(5, raw_df.shape[1])])
        except Exception as e:
            print(f"[preview] failed: {e}")

    # Map col headers to canonical headers
    for canonical, variants in col_map.items():
        if not isinstance(variants, (list, tuple)):
            variants = [variants]

        # found_col = None
        found_cols = [] # List to accomoadate for multiple variants found in the same file.
        tried = []

        # Check each variant for a match in the normalized raw columns, append multiple variants found for the same canonical value in a list.
        for variant in variants:
            variant_norm = str(variant).strip().lower()
            tried.append(variant_norm)
            if variant_norm in norm_cols:
                found_cols.append(norm_cols[variant_norm][0])

        # If at least one variant was found, proceed with mapping
        if len(found_cols) > 0:

            # If only one raw column matched, map that column to the canonical header.
            if len(found_cols) == 1:
                merged = raw_df[found_cols[0]].copy()

            # Else, if multiple raw columns matched, consolidate them based on the consolidation method defined in the concept class.
            else:
                 # Retrieve consolidation_key from concept class
                concept_class = accepted_responses.get(canonical, {}).get("concept_class", None) # get concept class from workbook definitions
                consolidation_method = getattr(concept_classes.get(concept_class), "consolidation_method", "single-select") # get consolidation method based on concept class

                # If consolidation method is single-select, then just take the first non-null value
                if consolidation_method == "single-select":
                    # Existing behavior: first non-null wins
                    merged = raw_df[found_cols[0]].copy()
                    for colname in found_cols[1:]:
                        merged = merged.fillna(raw_df[colname])

                # If consolidation method is additive, then join the strings by a ','
                elif consolidation_method == "additive":
                    # New behavior: combine all non-null/non-empty values
                    def combine_vals(row):
                        vals = [
                            row[c] for c in found_cols
                            if pd.notna(row[c]) and str(row[c]).strip() != ""
                        ]
                        return ", ".join(map(str, vals)) if vals else pd.NA

                    merged = raw_df[found_cols].apply(combine_vals, axis=1)

                else:
                    raise ValueError(f"Unknown consolidation_key '{consolidation_method}' for column '{canonical}'")

            selected_cols.append(merged)
            matched_count += 1

            # Only add a canonical value to the canonical labels present if a variant is found in the file. 
            # This is beneficial for large projects that have many data elements in workbook definitions that may not be present in all files.
            canonical_labels_present.append(canonical)

        # This list contains all canonical_labels in the workbook defintions.    
        canonical_labels.append(canonical)

    if debug:
        print(f"[summary] matched={matched_count}, missing={missing_count}, total={len(canonical_labels)}")

    # Combine into ordered DataFrame
    df_ordered = pd.concat(selected_cols, axis=1)
    if debug:
        print(f"[combine] df_ordered.shape = {df_ordered.shape}")

    # Remove headers (force 0..n-1)
    df_no_headers = df_ordered.copy()
    df_no_headers.columns = range(df_no_headers.shape[1])

    if debug:
        # Heuristic: all columns NA?
        all_na_cols = df_no_headers.isna().all(axis=0).sum()
        if all_na_cols == df_no_headers.shape[1]:
            print("[warn] All selected columns are NA. Likely no headers matched.")
        else:
            print(f"[info] NA-only columns: {all_na_cols}/{df_no_headers.shape[1]}")
        print("=== [extract_columns] END ===\n")

    return df_no_headers, canonical_labels, canonical_labels_present

def clean_text(val):
    """
    Normalize a single Excel cell value by removing common non-printing characters.

    This helper is used to clean cell-level text extracted from Excel files,
    especially where partner submissions include stray encoding artifacts such as:

    - Non-breaking spaces (``\\xa0``)
    - Mis-encoded characters (e.g., ``'Â'`` before accented characters)
    - Extra surrounding whitespace

    Args:
        val: Any value from a pandas cell. Typically a string, but may be numeric,
             missing, or other types depending on the source Excel file.

    Returns:
        The cleaned string if ``val`` is a string; otherwise returns ``val`` unchanged.

    Notes:
        - This function is intentionally conservative: it does not alter non-string
          values or attempt more aggressive normalization.
        - Typically applied via ``DataFrame.applymap(clean_text)`` during sheet loading.
    """    
    if isinstance(val, str):
        return val.replace('\xa0', ' ').replace('Â', '').strip()
    return val

def find_sheet_by_headers(file_obj, config, max_header_row=4, min_match_ratio=0.5):

    xl = pd.ExcelFile(file_obj, engine="openpyxl")

    expected_variants = {
        str(v).strip().lower()
        for variants in config["labels"].values()
        for v in variants
    }

    best_sheet = None
    best_row = None
    best_score = 0

    for sheet in xl.sheet_names:

        preview = xl.parse(sheet, header=None, nrows=max_header_row + 5)

        check_length = min(len(preview), max_header_row)

        for row in range(check_length):

            

            headers = {
                str(x).strip().lower()
                for x in preview.iloc[row].tolist()
                if pd.notna(x)
            }

            score = len(headers & expected_variants)

            if score > best_score:
                best_score = score
                best_sheet = sheet
                best_row = row

    if best_sheet is None:
        raise ValueError("No sheet with matching headers found")

    expected_count = len(config["labels"])

    match_ratio = best_score / max(expected_count, 1)

    if match_ratio < min_match_ratio:
        raise ValueError(
            f"No reliable sheet match (best match {best_sheet}, ratio={match_ratio:.2f})"
        )

    print(
        f"⚠️ Using sheet '{best_sheet}' with header row {best_row} "
        f"(matched {best_score} columns)"
    )

    return best_sheet, best_row


class WorkbookLoader:
    """
        Loader for a single Excel workbook using a schema-driven sheet definition.

        This class encapsulates all logic for:
        * Preprocessing a workbook via Excel COM (unprotecting/unhiding sheets).
        * Reading one or more sheets into pandas DataFrames using `sheet_defs`.
        * Optionally performing dynamic, variant-aware header extraction.
        * Adding row-level identifiers (via `KeyCreator`) and `row_number`.
        * Filtering out rows with invalid or missing first/last name values.

        It is designed to handle noisy, partner-submitted workbooks where:
        * Headers may differ across submissions.
        * Workbooks may arrive protected or with hidden sheets.
        * Files may be intermittently locked (OneDrive, concurrent users, etc.).
        """
    def __init__(self, file_path, workbook_type, sheet_defs, starting_row = 0, dynamic=False, password="workforce", keycreator: KeyCreator = None, multi_sheet_mode: bool = True):
        """
        Initialize a WorkbookLoader for a specific Excel file and schema.

        Args:
            file_path (str):
                Path to the Excel workbook to load.
            workbook_type (str):
                Key into `sheet_defs` indicating which workbook definition to use
                (e.g., "training data").
            sheet_defs (dict):
                Schema describing sheet-specific configuration. Typically of the form:

                .. code-block:: python

                    sheet_defs = {
                        "training data": {
                            "Report": {
                                "starting_row": 1,
                                "starting_column": 0,
                                "labels": [...],
                                "columns_used": [...],
                            },
                            ...
                        }
                    }

            dynamic (bool, optional):
                If True, use `extract_columns_noisy` to match headers against
                canonical labels. If False, assume headers align with `labels`
                and use static positional slicing. Default is False.
            password (str, optional):
                Password used to unprotect the workbook and sheets. Default is
                "workforce".
            keycreator (KeyCreator, optional):
                Optional key generator used to add an `id_key` column for each
                row in multi-sheet mode.
        """



        self.file_path = file_path
        self.workbook_type = workbook_type
        self.starting_row = starting_row
        self.sheet_defs = sheet_defs
        self.dynamic = dynamic
        self.password = password
        self.multi_sheet_mode = multi_sheet_mode

        self.keycreator = keycreator
        
    def preprocess_excel(self):
        """
        Unprotect and unhide the workbook using Excel COM automation.

        This method:
          * Initializes COM for the current thread.
          * Creates an Excel Application instance via `win32.Dispatch`.
          * Attempts to set `Visible=False` and `DisplayAlerts=False`.
          * Calls :func:`ensure_unprotected_visible` to unprotect/unhide sheets.
          * Cleans up the Excel instance and uninitializes COM in a `finally` block.

        It is robust against intermittent COM initialization issues and will retry
        `Excel.Application` creation once after a short delay if the first attempt
        fails. Errors during unprotect/unhide are logged but not re-raised.

        Side Effects:
            - Modifies the workbook on disk (unprotects/unhides, then saves).
            - Writes progress and warning messages to stdout.
            - Starts and stops an Excel COM instance.
        """

        print(f"🔧 Preprocessing workbook: {self.file_path}")

        # --- Ensure COM is initialized for this thread ---
        pythoncom.CoInitialize()

        # --- Create or connect to Excel safely ---
        try:
            excel = win32.Dispatch("Excel.Application")
        except Exception as e:
            print(f"⚠️ Excel.Dispatch() failed ({e}), retrying after short delay...")
            time.sleep(0.5)
            excel = win32.Dispatch("Excel.Application")

        # --- Attempt to set properties safely ---
        try:
            excel.Visible = False   # you can keep True if needed
        except Exception as e:
            print(f"⚠️ Could not set Excel.Visible — {e}")

        try:
            excel.DisplayAlerts = False
        except Exception as e:
            print(f"⚠️ Could not set DisplayAlerts — {e}")

        # --- Execute main task ---
        try:
            ensure_unprotected_visible(excel, self.file_path, password=self.password)
        except Exception as e:
            print(f"❌ Error while unprotecting/unhiding workbook: {e}")
        finally:
            # Always close Excel cleanly
            try:
                
                pythoncom.CoUninitialize()
                excel.Quit()
            except Exception:
                pass

    def load_sheets(self) -> dict[str, pd.DataFrame]:
        """
        Load all configured sheets from the workbook into pandas DataFrames.

        For each sheet defined in ``sheet_defs[self.workbook_type]`` this method:

          1. Repeatedly attempts to read the sheet using `pandas.read_excel`:
             - Retries indefinitely on ``PermissionError`` (e.g., OneDrive lock),
               with a capped backoff.
             - Logs non-permission errors and skips the sheet.
          2. Applies one of two header strategies:
             - **Dynamic mode** (`self.dynamic=True`): uses
               :func:`extract_columns_noisy` to map messy headers to canonical labels.
             - **Static mode**: slices columns starting at ``starting_column`` and
               assigns labels from the configuration.
          3. Adds a ``row_number`` column (1-based Excel-style row index, offset by 2
             to account for header rows) to each sheet.
          4. In multi-sheet mode, optionally adds an ``id_key`` column using
             ``self.keycreator``.
          5. Filters out rows where both "First Name" and "Last Name" fail strict
             alphabetic normalization, if those columns exist.

        The result is a dictionary keyed by sheet name, ready to be passed into the
        validation engine.

        Returns:
            dict[str, pd.DataFrame]:
                Mapping of sheet name → cleaned DataFrame for that sheet.

        Side Effects:
            - Populates/updates ``self.permission_denied_log`` with any load errors.
            - Prints progress and error messages to stdout.

        Notes:
            - This method assumes `self.sheet_defs` is structured with
              ``starting_row``, ``starting_column``, ``labels``, and optionally
              ``columns_used`` for each sheet.
            - The retry loop for `PermissionError` is intentional to deal with
              transient sync/locking issues in shared OneDrive environments.
        """
        dfs_by_sheet = {}
        permission_denied_log = getattr(self, "permission_denied_log", [])

        sheet_defs_for_type = self.sheet_defs[self.workbook_type]
        # multi_sheet_mode = len(sheet_defs_for_type) > 1

        for sheet_key, config in sheet_defs_for_type.items():
            starting_col = config.get("starting_column", 0)

            sheet_specific_starting_row = config.get("starting_row", self.starting_row)
            starting_row = sheet_specific_starting_row

            raw_df = None
            attempt = 0

            # ------------------------------------------------------------
            # 🔁 Infinite retry loop
            # ------------------------------------------------------------
            while raw_df is None:
                try:
                    with open(self.file_path, "rb") as f:

                        read_kwargs = {
                            "header": starting_row,
                            "engine": "openpyxl",
                            "sheet_name":sheet_key,
                            "usecols": config.get("columns_used", None),
                        }

                        # if self.multi_sheet_mode:
                        #     read_kwargs["sheet_name"] = sheet_key

                        raw_df = pd.read_excel(f, **read_kwargs).applymap(clean_text)
                        # raw_df = pd.read_excel(
                        #     f,
                        #     sheet_name=sheet_key,
                        #     header=starting_row,
                        #     engine="openpyxl",
                        #     usecols=config.get("columns_used", None)
                        # ).applymap(clean_text)
                    # ✅ success
                    print(f"✅ Successfully read '{sheet_key}' from {self.file_path}")
                    break

                except PermissionError as pe:
                    attempt += 1
                    wait_time = min(10, 2 + attempt)  # steady backoff, capped at 10s
                    now = datetime.now().strftime("%H:%M:%S")
                    print(
                        f"[{now}] 🚫 Permission denied reading '{sheet_key}' "
                        f"from {self.file_path} — retrying in {wait_time}s (attempt {attempt})"
                    )
                    time.sleep(wait_time)
                    continue

                except ValueError as e:

                    # pandas throws ValueError when sheet_name does not exist
                    if "Worksheet named" in str(e):

                        print(
                            f"⚠️ Sheet '{sheet_key}' not found in {self.file_path}. "
                            "Searching workbook for matching headers."
                        )

                        with open(self.file_path, "rb") as f:
                            found_sheet, found_row = find_sheet_by_headers(f, config)

                        print(
                            f"⚠️ Using fallback sheet '{found_sheet}' "
                            f"(header row {found_row}) instead of '{sheet_key}'"
                        )

                        with open(self.file_path, "rb") as f:
                            raw_df = pd.read_excel(
                                f,
                                sheet_name=found_sheet,
                                header=found_row,
                                engine="openpyxl",
                                usecols=config.get("columns_used", None),
                            ).applymap(clean_text)

                        break

                except Exception as e:
                    print(f"❌ Error loading sheet {sheet_key} from {self.file_path}: {e}")
                    traceback.print_exc()
                    permission_denied_log.append({
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "file_path": self.file_path,
                        "sheet": sheet_key,
                        "error": str(e),
                        "workbook_type": self.workbook_type
                    })
                    break  # non-permission errors shouldn’t retry forever


            # Skip sheet if not successfully read
            if raw_df is None:
                continue

            # ------------------------------------------------------------
            # Normal processing logic
            # ------------------------------------------------------------
            try:
                if self.dynamic:
                    df, labels, labels_present = extract_columns_noisy(raw_df, config["labels"], config["accepted_responses"])
                else:
                    df = raw_df.iloc[:, starting_col:] if starting_col > 0 else raw_df
                    labels = config["labels"]
                    labels_present = config["labels_present"]

                # Ensure all columns present are relabeled to their canonical names, even if some are missing
                df.columns = labels_present

                # Ensure all expected labels are present, filling missing ones with NA
                if df.columns.tolist() != labels:
                    print(f"⚠️ WARNING: Not all columns from labels are present in '{sheet_key}'. Reindexing columns to match expected labels.")

                if self.multi_sheet_mode:
                    df = df.copy()
                    if self.keycreator is not None:
                        df = self.keycreator.add_key_column(df, key_col="id_key")
                    df[f"row_number_{sheet_key}"] = df.index + 2
                else:
                    df[f"row_number_{sheet_key}"] = df.index + 2

                dfs_by_sheet[sheet_key] = df

            except Exception as e:
                print(f"⚠️ Post-processing failed for {sheet_key}: {e}")
                traceback.print_exc()
                continue

        # ------------------------------------------------------------
        # Filter out rows with no first/last name
        # ------------------------------------------------------------
            for sheet_name, df in dfs_by_sheet.items():
                if "First Name" in df.columns and "Last Name" in df.columns:

                    # Apply strict alphabetic normalization to detect valid rows
                    first_norm = df["First Name"].apply(strict_alphabetic_normalize)
                    last_norm  = df["Last Name"].apply(strict_alphabetic_normalize)

                    # Keep rows where at least one field is valid
                    mask_valid = first_norm.notna() | last_norm.notna()

                    dfs_by_sheet[sheet_name] = df[mask_valid].copy()

        self.permission_denied_log = permission_denied_log
        return dfs_by_sheet

class MultiWorkbookLoader:
    """
    Loader for concatenating multiple Excel workbooks into a unified
    sheet-by-sheet structure according to a shared schema definition.

    This class wraps :class:`WorkbookLoader` to provide batch ingestion when
    partners submit multiple files for the same reporting period, program, or
    location (e.g., separate New Haven / Bridgeport / Hartford spreadsheets).

    It handles:
        - Preprocessing all files via Excel COM (unprotect/hide/unlock).
        - Loading each file’s sheets using the same `sheet_defs` configuration.
        - Injecting an optional `id_key` via a shared `KeyCreator`.
        - Preserving file-level provenance via a `source_file` column.
        - Concatenating sheets across workbooks and applying final cleanup
          (deduplication, index reset, etc.).

    Designed for noisy, inconsistent partner submissions that still follow a
    common schema (labels, starting rows, required sheets).
    """
    def __init__(self, file_paths, workbook_type, sheet_defs, starting_row = 0, dynamic=False, password="workforce", keycreator: KeyCreator = None, multi_sheet_mode: bool = True):
        """
        Initialize a MultiWorkbookLoader.

        Args:
            file_paths (list[str] or set[str]):
                Collection of Excel file paths to be merged. All workbooks must
                conform to the same sheet-definition schema.
            workbook_type (str):
                Key into `sheet_defs` indicating which configuration to use
                (e.g., "training data").
            sheet_defs (dict):
                Schema describing sheet-specific configurations for each workbook
                type. Same structure used by :class:`WorkbookLoader`.
            dynamic (bool, optional):
                If True, use noisy header extraction (`extract_columns_noisy`).
                If False, assume static labels. Default is False.
            password (str, optional):
                Password used to unprotect/unhide sheets via Excel COM.
                Default is "workforce".
            keycreator (KeyCreator, optional):
                Optional row-level key generator used by underlying
                `WorkbookLoader` instances.
        """

        self.file_paths = list(file_paths)
        self.workbook_type = workbook_type
        self.sheet_defs = sheet_defs
        self.starting_row = starting_row
        self.dynamic = dynamic
        self.password = password

        self.keycreator = keycreator

    def preprocess_all(self):
        """
        Unprotect and unhide all workbooks prior to loading, using a shared
        Excel COM instance.

        This method:
            - Initializes COM for the current thread.
            - Creates a single Excel application instance.
            - Iterates over all files in `self.file_paths` and calls
              :func:`ensure_unprotected_visible` on each.
            - Ensures Excel is always quit and COM is uninitialized cleanly.

        This reduces overhead compared to creating a new Excel instance per file,
        and is robust against intermittent COM initialization failures.

        Side Effects:
            - Modifies each workbook on disk (unprotect/unhide/save).
            - Prints progress and warning messages to stdout.
            - Starts a COM Excel instance and terminates it.

        Notes:
            - Assumes Windows + Microsoft Excel installed.
            - If the password is incorrect for any workbook, sheets may remain
              protected but loading may still succeed depending on how pandas
              handles locked files.
        """
        pythoncom.CoInitialize()
        """Unprotect/unhide all workbooks before loading."""
        try:
            excel = win32.Dispatch("Excel.Application")
        except Exception:
        # Retry after short delay — Excel may not have initialized
            time.sleep(0.5)
            excel = win32com.client.Dispatch("Excel.Application")
        try:
            excel.Visible = False
        except Exception as e:
            print(f"⚠️ Warning: Could not set Excel visibility — {e}")
            # continue silently; this is not fatal
        try:
            excel.DisplayAlerts = False
        except Exception as e:
            print(f"Warning: could not set Excel Display Alerts - {e}")
        try:
            for fp in self.file_paths:
                print(f"🔧 Preprocessing: {fp}")
                ensure_unprotected_visible(excel, fp, password=self.password)
        finally:
            pythoncom.CoUninitialize()
            excel.Quit()

    def load_all(self):
        """
        Load and concatenate all workbooks in `self.file_paths`.

        For each file:
            1. Logs which workbook is being processed.
            2. Creates a :class:`WorkbookLoader` with the shared schema.
            3. Calls `loader.load_sheets()` to obtain a dict of
               {sheet_name: DataFrame}.
            4. Adds a `source_file` column to track data provenance.
            5. Concatenates each sheet across workbooks.

        After loading all files, a final cleanup step:
            - Drops duplicate rows within each combined sheet.
            - Resets indexes for every sheet.

        Returns:
            dict[str, pd.DataFrame]:
                A mapping of sheet_name → concatenated DataFrame containing
                rows from all provided workbooks.

        Side Effects:
            - Prints progress information to stdout.
            - Uses :class:`WorkbookLoader`, which may create an Excel COM
              instance if preprocessing is used.
            - Adds a `source_file` column to each sheet’s DataFrame.

        Notes:
            - Sheet names must match across files according to `sheet_defs`.
            - This method does not call `preprocess_all()` automatically;
              the caller should invoke it when required.
            - Deduplication is simple (row-wise). Additional deconfliction rules
              may be added depending on program requirements.
        """
        all_sheets = {}

        

        for file_path in self.file_paths:
            print(f"\n📘 Loading workbook: {file_path}")
            loader = WorkbookLoader(
                file_path=file_path,
                workbook_type=self.workbook_type,
                sheet_defs=self.sheet_defs,
                starting_row=self.starting_row,
                dynamic=self.dynamic,
                password=self.password,
                keycreator=self.keycreator
            )

            dfs_by_sheet = loader.load_sheets()
            for sheet_name, df in dfs_by_sheet.items():
                df = df.copy()
                df["source_file"] = file_path  # add provenance

                if sheet_name not in all_sheets:
                    all_sheets[sheet_name] = df
                else:
                    all_sheets[sheet_name] = pd.concat([all_sheets[sheet_name], df], ignore_index=True)

        # Final cleanup pass
        for sheet_name, df in all_sheets.items():
            print(f"🧹 Finalizing sheet '{sheet_name}' - {len(df)} rows total")
            # Example normalization: drop duplicates or reset index
            all_sheets[sheet_name] = df.drop_duplicates().reset_index(drop=True)

        return all_sheets

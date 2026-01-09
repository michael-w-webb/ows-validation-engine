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

import pandas as pd 
import os
import win32com.client as win32
import time
import traceback
from datetime import datetime
import pythoncom
import win32com.client

from cc_key_creator import KeyCreator
from cc_standard_normalizations import strict_alphabetic_normalize

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
    wb = None
    try:
        print(f"🔓 Unprotecting and unhiding sheets in: {file_path}")
        wb = excel.Workbooks.Open(file_path, UpdateLinks=0)

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
            wb.Close(SaveChanges=1)

def extract_columns_noisy(raw_df: pd.DataFrame, col_map: dict, preview_rows: int = 5, debug: bool = True):
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

    # Build normalization map: normalized -> original
    norm_cols = {}
    for c in raw_df.columns:
        key = str(c).strip().lower()
        # keep first occurrence only to make duplicates obvious
        if key not in norm_cols:
            norm_cols[key] = c
        elif debug:
            print(f"[warn] duplicate normalized header: '{key}' maps to '{norm_cols[key]}' and '{c}'")

    if debug:
        # Show a few normalized keys
        sample_norm = list(norm_cols.keys())[:30]
        print(f"[norm map] sample normalized keys (count={len(norm_cols)}): {sample_norm}")
        if len(norm_cols) > 30:
            print("           ... (truncated)")

    selected_cols = []
    canonical_labels = []
    matched_count = 0
    missing_count = 0

    # Optional preview of data
    if debug:
        try:
            print("[preview] top rows of raw_df (first 5 cols shown):")
            print(raw_df.iloc[:preview_rows, :min(5, raw_df.shape[1])])
        except Exception as e:
            print(f"[preview] failed: {e}")

    for canonical, variants in col_map.items():
        if not isinstance(variants, (list, tuple)):
            variants = [variants]

        found_col = None
        tried = []

        for variant in variants:
            variant_norm = str(variant).strip().lower()
            tried.append(variant_norm)
            if variant_norm in norm_cols:
                found_col = norm_cols[variant_norm]
                break

        if found_col is not None:
            selected_cols.append(raw_df[found_col])
            matched_count += 1
            if debug:
                print(f"[match] canonical='{canonical}' <- raw='{found_col}' (tried={tried})")
        else:
            selected_cols.append(pd.Series([pd.NA] * len(raw_df), index=raw_df.index))
            missing_count += 1
            if debug:
                print(f"[MISS ] canonical='{canonical}' had no match. tried variants={tried}")

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

    return df_no_headers, canonical_labels

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
    def __init__(self, file_path, workbook_type, sheet_defs, dynamic=False, password="workforce", keycreator: KeyCreator = None):
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
        self.sheet_defs = sheet_defs
        self.dynamic = dynamic
        self.password = password

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
        multi_sheet_mode = len(sheet_defs_for_type) > 1

        for sheet_key, config in sheet_defs_for_type.items():
            starting_row = config.get("starting_row", 1)
            starting_col = config.get("starting_column", 0)

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
                            "usecols": config.get("columns_used", None),
                        }

                        if multi_sheet_mode:
                            read_kwargs["sheet_name"] = sheet_key

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
                    df, labels = extract_columns_noisy(raw_df, config["labels"])
                else:
                    df = raw_df.iloc[:, starting_col:] if starting_col > 0 else raw_df
                    labels = config["labels"]

                df.columns = labels

                if multi_sheet_mode:
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
    def __init__(self, file_paths, workbook_type, sheet_defs, dynamic=False, password="workforce", keycreator: KeyCreator = None):
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

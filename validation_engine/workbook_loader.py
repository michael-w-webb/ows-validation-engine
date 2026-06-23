"""
Workbook Loading and Preprocessing Utilities
============================================

This module provides tools for loading CareerConneCT / GJC Excel workbooks
in environments where files may be protected, contain inconsistent schemas,
differ across organizations, or be intermittently locked by OneDrive or
concurrent users.

Capabilities
------------

1. **Excel COM preprocessing (optional)**
   - Attempts to unprotect and unhide worksheets
   - Saves workbooks in a readable state for downstream processing
   - Uses defensive (best-effort) initialization and cleanup of
     ``win32com`` Excel instances

2. **Resilient sheet loading**
   - Unbounded retry on ``PermissionError`` with capped backoff
     (to tolerate transient file locks)
   - Config-driven ``starting_row``, ``starting_column``, and ``columns_used``
   - Fallback sheet detection via header matching when expected sheets
     are missing

3. **Header normalization**
   - Dynamic mode: tolerant, variant-aware matching of column headers
     via :func:`extract_columns_noisy`
   - Static mode: positional slicing with assumed alignment to configured labels

4. **Row-level processing**
   - Optional integration with :class:`KeyCreator` for identifier generation
   - Lightweight text normalization via :func:`clean_text`
   - Conditional filtering of rows based on name field validity

5. **Multi-workbook aggregation**
   - Batch loading of multiple files using a shared schema
   - Sheet-wise concatenation across workbooks
   - Provenance tracking via ``source_file`` column
   - Final row-wise deduplication and index normalization

Major Components
----------------

Functions
~~~~~~~~~
- ``ensure_unprotected_visible``  
  Attempts to remove protection and unhide all sheets via Excel COM.

- ``extract_columns_noisy``  
  Maps variant Excel headers to canonical labels using normalization
  and tolerant matching.

- ``clean_text``  
  Performs conservative normalization of cell-level text values.

- ``find_sheet_by_headers``  
  Heuristically identifies the correct sheet and header row when expected
  sheets are missing.

Classes
~~~~~~~
- :class:`WorkbookLoader`  
  Loads a single workbook using a schema definition. Handles resilient
  file access, optional header normalization, fallback sheet detection,
  and row-level processing.

- :class:`MultiWorkbookLoader`  
  Aggregates multiple workbooks into a unified sheet-by-sheet structure
  using a shared schema. Ingestion is best-effort; missing or failed
  sheets do not halt processing.

Typical Workflow
----------------
1. (Optional) Preprocess workbooks to remove protection and unhide sheets.
2. Load configured sheets using :class:`WorkbookLoader`.
3. Apply canonical header mapping (dynamic or static).
4. Optionally generate row-level identifiers.
5. Apply basic row filtering and text normalization.
6. (Optional) Aggregate multiple workbooks via :class:`MultiWorkbookLoader`.

Dependencies
------------
- pandas
- win32com (Excel COM automation)
- pythoncom
- traceback / datetime / os / time
- KeyCreator (optional)
- strict_alphabetic_normalize (optional)

Notes
-----
- Requires a Windows environment with Microsoft Excel installed (for COM).
- Preprocessing is optional but may be required for protected workbooks.
- File loading is resilient by design; partial results may be returned when
  errors occur.
- Assumes ``sheet_defs`` provides label definitions and positional metadata.
"""

import pandas as pd 
import win32com.client as win32
import time
import traceback
from datetime import datetime
import pythoncom
import win32com.client

from validation_engine.key_creator import KeyCreator
from validation_engine.standard_normalizations import strict_alphabetic_normalize

def ensure_unprotected_visible(excel, file_path, password="workforce"):
    """
    Open an Excel workbook via COM automation, attempt to remove protection,
    and ensure all worksheets are visible.

    This utility is intended for partner-submitted CareerConneCT/GJC workbooks
    that may be locked, password-protected, or contain hidden sheets. It modifies
    the file *in-place* to improve downstream readability (e.g., by pandas).

    Behavior:
        1. Opens the workbook using a provided Excel COM instance.
        2. Attempts to remove workbook-level protection.
        3. Iterates through all worksheets:
        - Attempts to unprotect each sheet using the provided password.
        - Sets sheet visibility to visible (``xlSheetVisible = -1``).
        4. Saves the workbook.
        5. Closes the workbook in a ``finally`` block, with retry logic to
        mitigate transient COM failures.

    Args:
        excel:
            Active ``win32com.client.Dispatch("Excel.Application")`` instance.
            Caller is responsible for lifecycle management (including ``Quit()``).
        file_path (str):
            Absolute path to the Excel file.
        password (str, optional):
            Password used for unprotect operations. Defaults to ``"workforce"``.

    Returns:
        str:
            The original ``file_path``.

    Side Effects:
        - Modifies and saves the workbook on disk.
        - Attempts to unhide all worksheets.
        - Emits diagnostic output to stdout.

    Raises:
        Exception:
            Propagates errors from ``Workbooks.Open`` and other non-handled COM failures.

    Notes:
        - Requires Windows with Microsoft Excel installed.
        - If the password is incorrect, some sheets may remain protected.
        - Handles hidden and "very hidden" sheets when not blocked by protection.
        - Workbook close is retried to handle intermittent COM issues.
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
        t0 = time.time()
        wb = excel.Workbooks.Open(file_path, UpdateLinks=0)
        print("Excel open time:", time.time() - t0)
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

def extract_columns_noisy(raw_df: pd.DataFrame, col_map: dict, preview_rows: int = 5, debug: bool = False):
    """
    Select and reorder columns from a noisy Excel-derived DataFrame using a
    canonical-to-variant header mapping.

    This function is designed for partner-submitted Excel files where header
    labels vary across submissions (e.g., "First Name", "FirstName", "FName").
    It performs tolerant matching by normalizing column headers via:

        str(header).strip().lower()

    and comparing against normalized variants provided in ``col_map``.

    For each canonical label (in order of ``col_map``):
        - The first matching variant is selected ("first-match wins").
        - If no match is found, a column of ``NA`` values is inserted.
        - Output columns preserve the order of ``col_map``.

    Matching behavior:
        - Raw column names are normalized once and stored as a lookup map.
        - If multiple raw columns normalize to the same key, only the first
        occurrence is used (duplicates are optionally reported in debug mode).

    Args:
        raw_df (pd.DataFrame):
            Input DataFrame (e.g., from ``pd.read_excel``). Column names are
            treated as-is and normalized internally.
        col_map (dict[str, list[str] | str]):
            Mapping of canonical labels to one or more header variants.
            Variants are matched after normalization.
        preview_rows (int, optional):
            Number of rows to display in debug preview output. Default is 5.
        debug (bool, optional):
            If True, prints diagnostic output including:
                - raw and normalized headers
                - duplicate header warnings
                - match/miss decisions per column
                - small data preview
                - summary statistics
            Default is False.

    Returns:
        tuple[pd.DataFrame, list[str]]:
            - df_no_headers:
                DataFrame with selected columns, ordered by ``col_map``.
                Columns are relabeled to integer indices (0..n-1).
            - canonical_labels:
                List of canonical labels aligned positionally with
                ``df_no_headers.columns``.

    Notes:
        - Missing canonical labels result in all-NA columns.
        - Output column order strictly follows ``col_map`` key order.
        - This function does not mutate ``raw_df``.
        - Positional alignment between returned DataFrame columns and
        ``canonical_labels`` is intentional and required for downstream use.
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

def find_sheet_by_headers(file_obj, config, max_header_row=4, min_match_ratio=0.5):

    """
    Heuristically identify the most likely worksheet and header row based on
    overlap with expected column label variants.

    This function scans all sheets in an Excel file and evaluates candidate
    header rows by comparing their normalized cell values against a set of
    expected header variants derived from ``config["labels"]``. The sheet/row
    pair with the highest overlap score is selected, subject to a minimum
    match threshold.

    Matching logic:
        - Cell values are normalized via ``str(x).strip().lower()``.
        - Expected variants are constructed from all values in
        ``config["labels"]``.
        - For each sheet and candidate row (up to ``max_header_row``), a score
        is computed as the count of overlapping normalized values.
        - The (sheet, row) pair with the highest score is selected.

    Args:
        file_obj:
            File-like object or path compatible with ``pandas.ExcelFile``.
        config (dict):
            Sheet configuration containing a ``"labels"`` mapping of canonical
            column names to variant header strings.
        max_header_row (int, optional):
            Maximum number of top rows (per sheet) to evaluate as potential
            header rows. Default is 4.
        min_match_ratio (float, optional):
            Minimum acceptable ratio of matched headers, defined as:

                best_score / len(config["labels"])

            If the best candidate falls below this threshold, an error is raised.
            Default is 0.5.

    Returns:
        tuple[str, int]:
            - best_sheet:
                Name of the selected worksheet.
            - best_row:
                Zero-based row index identified as the header row.

    Raises:
        ValueError:
            - If no candidate sheet/row pair achieves a positive match.
            - If the best match does not meet ``min_match_ratio``.

    Side Effects:
        - Prints a warning indicating the selected sheet and header row.

    Notes:
        - This is a heuristic method and assumes that header rows contain a
        sufficient number of recognizable label variants.
        - Only the top ``max_header_row`` rows of each sheet are evaluated.
        - In cases of ties, the first encountered maximum is selected.
    """

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

    This class handles the ingestion of partner-submitted Excel workbooks into
    structured pandas DataFrames, with support for inconsistent schemas,
    protected files, and transient file access issues.

    Core responsibilities:
        - Optional preprocessing via Excel COM (unprotecting/unhiding sheets).
        - Reading configured sheets using ``sheet_defs``.
        - Resilient file access with indefinite retry on ``PermissionError``
        (e.g., OneDrive or concurrent access locks).
        - Fallback sheet detection using header matching when expected sheets
        are missing.
        - Optional dynamic, variant-aware header extraction.
        - Assignment of canonical column labels.
        - Optional row-level identifier generation via ``KeyCreator``.
        - Addition of row-level metadata (e.g., row number).
        - Basic row filtering based on name field validity.

    The loader is designed for noisy, partner-provided workbooks where:
        - Header names vary across submissions.
        - Sheets may be missing or renamed.
        - Files may be protected or partially inaccessible.
        - Data quality is inconsistent.

    Notes:
        - Dynamic mode (``dynamic=True``) performs tolerant header matching via
        :func:`extract_columns_noisy`.
        - Static mode assumes column alignment with configured labels and does
        not validate header correctness.
        - Row filtering is applied only when both "First Name" and "Last Name"
        columns are present, and retains rows where at least one field is valid.
    """
    def __init__(self, file_path, workbook_type, sheet_defs, starting_row = 0, dynamic=False, password="workforce", keycreator: KeyCreator = None, multi_sheet_mode: bool = True, api_source: bool = False):
        """
        Initialize a WorkbookLoader for a specific Excel file and schema.

        Args:
            file_path (str):
                Path to the Excel workbook to load.
            workbook_type (str):
                Key into ``sheet_defs`` identifying the workbook configuration
                (e.g., "training data").
            sheet_defs (dict):
                Schema describing sheet-specific configuration. Each workbook type
                maps to one or more sheet definitions containing:
                    - ``starting_row``
                    - ``starting_column``
                    - ``labels`` (canonical column names or mapping)
                    - optional ``columns_used``

            dynamic (bool, optional):
                If True, performs tolerant header matching using
                :func:`extract_columns_noisy`. If False, assumes columns align
                with ``labels`` and applies positional slicing. Default is False.

            password (str, optional):
                Password used for optional COM-based unprotect operations.
                Default is "workforce".

            keycreator (KeyCreator, optional):
                Optional key generator used to add an ``id_key`` column when
                ``multi_sheet_mode`` is enabled.

            multi_sheet_mode (bool, optional):
                If True, enables behaviors intended for multi-sheet ingestion,
                including optional key creation. Default is True.
        """



        self.file_path = file_path
        self.workbook_type = workbook_type
        self.starting_row = starting_row
        self.sheet_defs = sheet_defs
        self.dynamic = dynamic
        self.password = password
        self.multi_sheet_mode = multi_sheet_mode
        self.api_source = api_source

        self.keycreator = keycreator
        
    def preprocess_excel(self):
        """
        Preprocess the workbook by attempting to remove protection and ensure
        all worksheets are visible via Excel COM automation.

        This method:
            - Initializes COM for the current thread.
            - Creates or attaches to an Excel Application instance via
            ``win32.Dispatch("Excel.Application")``.
            - Attempts to set ``Visible=False`` and ``DisplayAlerts=False``.
            - Calls :func:`ensure_unprotected_visible` to unprotect and unhide sheets.
            - Attempts to close the Excel instance and uninitialize COM in a
            ``finally`` block.

        Initialization behavior:
            - If Excel COM initialization fails, a single retry is attempted
            after a short delay.

        Error handling:
            - Errors during unprotect/unhide are caught and logged.
            - Failures to initialize Excel after retry will propagate.

        Side Effects:
            - Modifies the workbook on disk (unprotects/unhides, then saves).
            - Emits progress and warning messages to stdout.
            - Starts (or attaches to) an Excel COM instance and attempts cleanup.
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

    def build_link_column_names(
        self,
        linking_columns
    ):

        """
        Creates standardized link key names.

        Example:
            ["First Name", "Last Name"]

        becomes:
            ["link_key_1", "link_key_2"]
        """

        return [
            f"link_key_{i + 1}"
            for i in range(len(linking_columns))
        ]


    def add_link_key_columns(
        self,
        df,
        config
    ):

        """
        Duplicates configured linking columns
        into standardized link_key_n columns.
        """

        linking_columns = config.get(
            "linking_columns",
            []
        )

        if not linking_columns:
            return df

        link_key_columns = (
            self.build_link_column_names(
                linking_columns
            )
        )

        for source_col, link_col in zip(
            linking_columns,
            link_key_columns
        ):

            if source_col in df.columns:

                df[link_col] = df[source_col]

            else:

                df[link_col] = pd.NA

        return df

    def load_sheets(self) -> dict[str, pd.DataFrame]:
        """
        Load all configured sheets from the workbook into pandas DataFrames.

        For each sheet defined in ``sheet_defs[self.workbook_type]`` this method:

        1. Attempts to read the sheet using ``pandas.read_excel``:
            - Retries indefinitely on ``PermissionError`` (e.g., OneDrive locks),
            using a capped backoff.
            - Logs non-permission errors and skips the sheet.
            - If the specified sheet is not found, attempts to locate a suitable
            fallback using :func:`find_sheet_by_headers`.

        2. Applies one of two header strategies:
            - **Dynamic mode** (``self.dynamic=True``):
            Uses :func:`extract_columns_noisy` to map variant headers to
            canonical labels.
            - **Static mode**:
            Slices columns starting at ``starting_column`` and assigns labels
            directly from configuration (no validation of alignment).

        3. Adds metadata columns:
            - ``row_number_{sheet}``: derived from ``df.index + 2`` (approximate
            Excel row reference, not strictly tied to ``starting_row``).
            - ``id_key`` (optional): added via ``self.keycreator`` in multi-sheet mode.

        4. Applies row-level filtering (per iteration):
            - If both "First Name" and "Last Name" columns exist, removes rows
            where both fail strict alphabetic normalization.

        The result is a dictionary keyed by sheet name, suitable for downstream
        validation.

        Returns:
            dict[str, pd.DataFrame]:
                Mapping of sheet name → processed DataFrame.

        Side Effects:
            - Populates/updates ``self.permission_denied_log`` with load errors.
            - Emits progress and diagnostic output to stdout.

        Notes:
            - Retry on ``PermissionError`` is unbounded by design to tolerate
            transient file locks.
            - Filtering is applied during iteration and may run multiple times
            as sheets are accumulated.
            - Assumes ``self.sheet_defs`` provides ``starting_row``,
            ``starting_column``, ``labels``, and optionally ``columns_used``.
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
                            )

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
                    df, labels = extract_columns_noisy(raw_df, config["labels"])
                else:
                    df = raw_df.iloc[:, starting_col:] if starting_col > 0 else raw_df
                    labels = config["labels"]

                df.columns = labels

                if self.api_source:

                    df = self.add_link_key_columns(
                            df=df,
                            config=config
                        )

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
    Loader for aggregating multiple Excel workbooks into a unified
    sheet-by-sheet structure using a shared schema definition.

    This class wraps :class:`WorkbookLoader` to provide batch ingestion when
    partners submit multiple files for the same reporting period, program, or
    location (e.g., separate regional spreadsheets).

    Core responsibilities:
        - Iterating over multiple workbook paths and loading each via
        :class:`WorkbookLoader`.
        - Applying a shared ``sheet_defs`` configuration across all files.
        - Preserving file-level provenance via a ``source_file`` column.
        - Concatenating DataFrames by sheet name across workbooks.
        - Performing simple final cleanup (row-wise deduplication, index reset).

    Optional capabilities:
        - Preprocessing workbooks via Excel COM (see :meth:`preprocess_all`).
        - Injecting row-level identifiers via a shared ``KeyCreator``.

    Behavioral notes:
        - Ingestion is best-effort: missing sheets or partial failures in
        individual workbooks do not prevent other files from loading.
        - Sheet aggregation is dynamic; only sheets successfully loaded are
        included in the final output.
        - No strict validation is performed to ensure schema consistency
        across files.

    Designed for noisy, inconsistent partner submissions that broadly follow
    a common schema but may vary in structure, naming, or completeness.
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
        Preprocess all workbooks by attempting to remove protection and ensure
        all worksheets are visible, using a shared Excel COM instance.

        This method:
            - Initializes COM for the current thread.
            - Creates or attaches to a single Excel Application instance.
            - Attempts to set ``Visible=False`` and ``DisplayAlerts=False``.
            - Iterates over ``self.file_paths`` and calls
            :func:`ensure_unprotected_visible` for each workbook.
            - Attempts to close the Excel instance and uninitialize COM in a
            ``finally`` block.

        Using a shared Excel instance reduces overhead compared to launching a
        separate instance per file.

        Initialization behavior:
            - If Excel COM initialization fails, a single retry is attempted
            after a short delay.

        Error handling:
            - Errors during individual workbook processing are handled within
            :func:`ensure_unprotected_visible`.
            - Failures to initialize Excel after retry will propagate.

        Side Effects:
            - Modifies each workbook on disk (unprotects/unhides, then saves).
            - Emits progress and warning messages to stdout.
            - Starts (or attaches to) an Excel COM instance and attempts cleanup.

        Notes:
            - Requires Windows with Microsoft Excel installed.
            - If the password is incorrect, some sheets may remain protected.
            - Cleanup of the Excel instance is attempted but not guaranteed in
            the presence of COM failures.
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
        Load and concatenate all workbooks in ``self.file_paths`` into a unified
        sheet-by-sheet structure.

        For each file:
            1. Logs which workbook is being processed.
            2. Instantiates a :class:`WorkbookLoader` with the shared schema.
            3. Calls ``loader.load_sheets()`` to obtain a mapping of
            ``{sheet_name: DataFrame}``.
            4. Adds a ``source_file`` column to each DataFrame to preserve provenance.
            5. Concatenates DataFrames by sheet name across all workbooks.

        After all files are processed, a final cleanup step:
            - Drops duplicate rows within each combined sheet (full-row comparison).
            - Resets the index for each sheet.

        Returns:
            dict[str, pd.DataFrame]:
                Mapping of ``sheet_name → concatenated DataFrame`` containing rows
                from all successfully loaded workbooks.

        Side Effects:
            - Emits progress information to stdout.
            - Adds a ``source_file`` column to each sheet’s DataFrame.

        Notes:
            - Sheets are included on a best-effort basis; missing or failed sheets
            in individual workbooks are skipped.
            - Sheet names do not need to be identical across all files; only
            observed sheets are included in the final output.
            - This method does not perform preprocessing; callers should invoke
            :meth:`preprocess_all` beforehand if required.
            - Deduplication is row-wise and does not use keys or subset matching.
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

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
    Open the Excel file, unprotect all sheets, and make them visible.
    Does NOT convert or re-save file format.
    Returns the original file path.
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
    raw_df: DataFrame read from Excel (no header or with header already handled as you intend)
    col_map: dict like {"First Name": ["First Name","FirstName","FName"], ...}
    Returns (df_no_headers, canonical_labels)
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
    if isinstance(val, str):
        return val.replace('\xa0', ' ').replace('Â', '').strip()
    return val

class WorkbookLoader:
    def __init__(self, file_path, workbook_type, sheet_defs, dynamic=False, password="workforce", keycreator: KeyCreator = None):
        self.file_path = file_path
        self.workbook_type = workbook_type
        self.sheet_defs = sheet_defs
        self.dynamic = dynamic
        self.password = password

        self.keycreator = keycreator

    
    def preprocess_excel(self):
        """
        Use COM automation to unprotect workbook and unhide sheets before reading.
        Handles intermittent Excel COM initialization errors gracefully.
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
        Return a dictionary of DataFrames keyed by sheet name.
        Retries indefinitely on PermissionError (e.g., OneDrive file lock).
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
                        raw_df = pd.read_excel(
                            f,
                            sheet_name=sheet_key,
                            header=starting_row,
                            engine="openpyxl",
                            usecols=config.get("columns_used", None)
                        ).applymap(clean_text)
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
                    df["row_number"] = df.index + 2
                else:
                    df["row_number"] = df.index + 2

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
    def __init__(self, file_paths, workbook_type, sheet_defs, dynamic=False, password="workforce", keycreator: KeyCreator = None):
        """
        file_paths: list or set of Excel file paths
        workbook_type: key for sheet_defs (e.g. "Participant Data")
        sheet_defs: dict of {workbook_type: {sheet_name: config}}
        """
        self.file_paths = list(file_paths)
        self.workbook_type = workbook_type
        self.sheet_defs = sheet_defs
        self.dynamic = dynamic
        self.password = password

        self.keycreator = keycreator

    def preprocess_all(self):

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
        Load and concatenate all workbooks.
        Returns: dict {sheet_name: combined DataFrame across all files}
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

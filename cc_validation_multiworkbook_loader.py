import pandas as pd
import win32com.client as win32

class MultiWorkbookLoader:
    def __init__(self, file_paths, workbook_type, sheet_defs, dynamic=False, password="workforce"):
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

    def preprocess_all(self):
        """Unprotect/unhide all workbooks before loading."""
        excel = win32.Dispatch("Excel.Application")
        excel.Visible = False
        excel.DisplayAlerts = False

        try:
            for fp in self.file_paths:
                print(f"🔧 Preprocessing: {fp}")
                ensure_unprotected_visible(excel, fp, password=self.password)
        finally:
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
                password=self.password
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

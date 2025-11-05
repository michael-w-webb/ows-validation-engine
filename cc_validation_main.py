import pandas as pd 

from cc_validation_engine import ValidationEngine
from cc_validation_workbook_loader import WorkbookLoader, MultiWorkbookLoader
from cc_column_label_list import cc_column_label_list
from cc_file_directory import cc_file_directory



# Containers for results
all_normalized = []
all_errors = []
all_mismatches = []  

for org, data_types in cc_file_directory.items():

    if "training data" not in data_types:
        continue

    # Get all periods and pick the last one (sorted alphanumerically)
    periods = sorted(data_types["training data"].keys())
    if not periods:
        continue
    period = periods[-1]

    file_meta = data_types["training data"][period]
    file_path = file_meta["file path"]
    workbook_format = file_meta["format"]

     # ✅ Choose single vs. multi loader
    if isinstance(file_path, (list, set, tuple)):
        print(f"📘 Loading multiple workbooks for {org} ({len(file_path)} files)")
        loader = MultiWorkbookLoader(
            file_paths=file_path,
            workbook_type=workbook_format,
            sheet_defs=cc_column_label_list["training data"],
            dynamic=True
        )
        loader.preprocess_all()
        dfs_by_sheet = loader.load_all()  # dict[sheet_name] = combined_df
    else:
        print(f"📗 Loading single workbook for {org}")
        loader = WorkbookLoader(
            file_path=file_path,
            workbook_type=workbook_format,
            sheet_defs=cc_column_label_list["training data"],
            dynamic=True
        )
        loader.preprocess_excel()
        dfs_by_sheet = loader.load_sheets()

    engine = ValidationEngine(cc_column_label_list)
    
    file_id = f"{org}|{period}".replace(" ", "_")

    engine.validate_workbook(
        file=file_id,
        workbook_type="training data",
        workbook_format=workbook_format,
        dfs_by_sheet=dfs_by_sheet
    )

    dfs = list(engine.normalized_data.items())  # [(sheet_name, df), ...]

    nonmatching_records = []  # local for this org/period

    def record_mismatches(keys, org, period, sheet, issue):
        for k in keys:
            nonmatching_records.append({
                "org": org,
                "period": period,
                "sheet": sheet,
                "id_key": k,
                "issue": issue
            })

    # --- Step 1: find all globally duplicated id_keys ---
    all_dup_keys = set()
    for sheet_name, df in dfs:
        if "id_key" in df.columns:
            dup_keys = df.loc[df["id_key"].duplicated(), "id_key"].unique()
            if len(dup_keys) > 0:
                record_mismatches(dup_keys, org, period, sheet_name, "duplicate_in_sheet")
                all_dup_keys.update(dup_keys)

    # --- Step 2: drop those keys from every sheet before comparing/merging ---
    cleaned_dfs = []
    for sheet_name, df in dfs:
        if "id_key" in df.columns:
            df = df[~df["id_key"].isin(all_dup_keys)].copy()
        cleaned_dfs.append((sheet_name, df))

    # --- Step 3: do matching/missing/extra on the cleaned data ---
    base_name, base_df = cleaned_dfs[0]
    merged = base_df.copy()

    for sheet_name, df in cleaned_dfs[1:]:
        if "id_key" not in df.columns:
            continue

        base_keys = set(merged["id_key"])
        sheet_keys = set(df["id_key"])

        missing_in_sheet = base_keys - sheet_keys
        extra_in_sheet   = sheet_keys - base_keys

        if missing_in_sheet:
            record_mismatches(missing_in_sheet, org, period, sheet_name, "missing_in_sheet")
        if extra_in_sheet:
            record_mismatches(extra_in_sheet, org, period, sheet_name, "extra_in_sheet")

        merged = merged.merge(df, on="id_key", how="inner", suffixes=("", f"_{sheet_name}"))

    normalized_combined = merged

    mismatches_df = pd.DataFrame(nonmatching_records)

    # --- Add to global collectors ---
    if not mismatches_df.empty:
        all_mismatches.append(mismatches_df)

    dedup_cols = ["id_key", "First Name", "Last Name", "row_number"]
    mask = normalized_combined.columns.duplicated() & normalized_combined.columns.isin(dedup_cols)
    normalized_combined = normalized_combined.loc[:, ~mask]

    normalized_combined["org"] = org
    normalized_combined["period"] = period
    all_normalized.append(normalized_combined)

    errs = engine.get_all_errors()
    if not errs.empty:
        errs["org"] = org
        errs["period"] = period
        all_errors.append(errs)


# --- Combine everything ---
normalized_final = pd.concat(all_normalized, ignore_index=True)
errors_final = pd.concat(all_errors, ignore_index=True) if all_errors else pd.DataFrame()
mismatches_final = pd.concat(all_mismatches, ignore_index=True) if all_mismatches else pd.DataFrame()

# --- Write once at the end ---
output_file = r"C:\Users\webbm\OneDrive - State of Connecticut\Documents\cc_validation_results_all_orgs_11_3.xlsx"
with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
    normalized_final.to_excel(writer, sheet_name="Normalized Data", index=False)
    errors_final.to_excel(writer, sheet_name="Validation Errors", index=False)
    if not mismatches_final.empty:
        mismatches_final.to_excel(writer, sheet_name="Key Mismatches", index=False)

print(f"✅ Results written to {output_file}")

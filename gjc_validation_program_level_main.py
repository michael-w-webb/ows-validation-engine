import pandas as pd 

from cc_validation_engine import ValidationEngine
from cc_validation_workbook_loader import WorkbookLoader
from gjc_column_label_lists import workbook_program_definitions, workbook_definitions
from gjc_file_metadata_dicitionary import submission_files
from cc_key_creator import KeyCreator
from cc_standard_normalizations import strict_alphabetic_normalize
#from gjc_validation_cross_rule_sets import CONDITIONALLY_REQUIRED_BY_DATE_COMPARISON_RULES, CONDITIONALLY_REQUIRED_RULES

workbook_definitions = workbook_program_definitions
# Containers for results


cross_rules = []
#     ("Conditionally Required", CONDITIONALLY_REQUIRED_RULES),
#     ("Conditionally Required by Date", CONDITIONALLY_REQUIRED_BY_DATE_COMPARISON_RULES)
# ]

for target_period in ["PY4 Q2"]:
                      #, "PY2 Q3", "PY2 Q4", "PY3 Q1", "PY3 Q2", "PY3 Q3", "PY3 Q4", "PY4 Q1"]:   ### specify period for file selection here. Could be adjusted to loop through all periods if desired.

    all_normalized = []
    all_errors = []
    all_mismatches = []  

    for org, data_types in submission_files.items():

        target_book = "TPI"

        if target_book not in data_types:
            continue
    
        # Get all periods and pick the last one (sorted alphanumerically)
        periods = sorted(data_types[target_book].keys())
        if target_period not in periods:
            continue
        period = target_period

        file_meta = data_types[target_book][period]

        if file_meta.get("formatting_issues", False):
            continue

        file_path = file_meta["file path"]
        workbook_format = file_meta["format"]

        #### starting row for data ingestion, treated as the 'header' value in read_excel, it can take a value from the file itself 
        #### as it does here (if available), but it can also take a sheet specific value from the workbook_definitions object inside of 
        #### workbook loader if one is specified there. The order of precedence is goings to be : workbook_definitions -> file_meta -> default (0)

        starting_row = 0  # default starting row
        if "starting row" in file_meta and file_meta["starting row"] is not None:
            starting_row = file_meta["starting row"]

        #### Start - Key Specification #### 

        ## Before loading workbooks, instantiate key creator and provide specifications 

        sheetlink_keycreator = KeyCreator(
        key_fields=["Training Provider Name", "Training Program Name"],     # minimal for now
        normalizers={
            "Training Provider Name": strict_alphabetic_normalize,
            "Training Program Name": strict_alphabetic_normalize,
        },
        required_fields=["Training Provider Name", "Training Program Name"],  # will drop invalid rows
        return_unhashed=True,                       # unhashed for easier debugging
    )
        
        ### key creator for entry level and linking to person database
        # No normalization because this is called after normalization is completed.  

        kc_strict = KeyCreator(
        key_fields=["First Name", "Last Name", "Date of Birth", "Zip Code"],
        required_fields=["First Name, Last Name", "Date of Birth", "Zip Code"],
        return_unhashed=True,
        )

        kc_med_name_dob = KeyCreator(
        key_fields=["First Name", "Last Name", "Date of Birth"],
        required_fields=["First Name, Last Name","Date of Birth"],
        return_unhashed=True,
        )

        kc_med_name_zip = KeyCreator(
        key_fields=["First Name", "Last Name", "Zip Code"],
        required_fields=["First Name, Last Name","Zip Code"],
        return_unhashed=True,
        )

        kc_weak = KeyCreator(
        key_fields=["First Name","Last Name"],
        required_fields =["First Name","Last Name"],
        return_unhashed=True,
        )

        keycreators = []
        
        # [(kc_strict, "id_key_strict_name_dob_zip"),
        #             (kc_med_name_dob, "id_key_medium_name_dob"),
        #             (kc_med_name_zip, "id_key_medium_name_zip"),
        #             (kc_weak, "id_key_weak_name")]

        multi_sheet_mode = True

        loader = WorkbookLoader(
            file_path=file_path,
            workbook_type=workbook_format,
            sheet_defs=workbook_definitions[target_book],
            starting_row=starting_row,
            dynamic=True,
            keycreator = sheetlink_keycreator,
            multi_sheet_mode= multi_sheet_mode
        )

        loader.preprocess_excel()
        dfs_by_sheet = loader.load_sheets()
        engine = ValidationEngine(workbook_definitions, cross_rules= cross_rules, logging = False)
        
        file_id = f"{org}|{period}".replace(" ", "_")

        engine.validate_workbook(
            file=file_id,
            workbook_type=target_book,
            workbook_format=workbook_format,
            dfs_by_sheet=dfs_by_sheet,
            keycreators= keycreators,
            passed_identity_sheet="Institutional_Information"
        )

        dfs = list(engine.normalized_data.items())  # [(sheet_name, df), ...]

        # Collect validation results
        errs = engine.get_all_errors()
        if not errs.empty:
            errs["org"] = org
            errs["period"] = period
            all_errors.append(errs)

        # --- multi-sheet logic below (only runs when >1 sheet) ---
        mismatches = pd.DataFrame(engine.mismatches)    
        if not mismatches.empty:
            mismatches["org"] = org
            mismatches["period"] = period

        all_mismatches.append(engine.mismatches)
        all_normalized.append(engine.single_sheet)


    # --- Combine everything ---
    normalized_final = pd.concat(all_normalized, ignore_index=True)
    errors_final = pd.concat(all_errors, ignore_index=True) if all_errors else pd.DataFrame()

    flat_rows = [
        row
        for sublist in all_mismatches
        for row in sublist
    ]

    mismatches_final = pd.DataFrame(flat_rows)

    # --- Write once at the end ---
    output_file = rf"C:\Users\webbm\OneDrive - State of Connecticut\Documents\gjc_validation_results_all_orgs_program_level_{target_period}.xlsx"
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        normalized_final.to_excel(writer, sheet_name="Normalized Data", index=False)
        errors_final.to_excel(writer, sheet_name="Validation Errors", index=False)
        if not mismatches_final.empty:
            mismatches_final.to_excel(writer, sheet_name="Key Mismatches", index=False)

    print(f"✅ Results written to {output_file}")

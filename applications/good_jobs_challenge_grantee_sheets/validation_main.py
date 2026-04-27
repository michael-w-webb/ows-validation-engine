import pandas as pd 

from config import OUTPUT_DIRECTORY

from validation_engine.validation_engine import ValidationEngine
from validation_engine.workbook_loader import WorkbookLoader
from validation_engine.key_creator import KeyCreator
from validation_engine.standard_normalizations import strict_alphabetic_normalize

from applications.good_jobs_challenge_grantee_sheets.workbook_definitions import workbook_definitions
from applications.good_jobs_challenge_grantee_sheets.file_directory import file_directory
from applications.good_jobs_challenge_grantee_sheets.cross_rule_sets import CONDITIONALLY_REQUIRED_BY_DATE_COMPARISON_RULES, CONDITIONALLY_REQUIRED_RULES

workbook_definitions = workbook_definitions
# Containers for results

LOGGING = True
LOG_DESCRIPTION = " 4/27 - Full run through to ensure we have at least one run with completed = 1 for each org/quarter combo"

cross_rules = [
    ("Conditionally Required", CONDITIONALLY_REQUIRED_RULES),
    ("Conditionally Required by Date", CONDITIONALLY_REQUIRED_BY_DATE_COMPARISON_RULES)
]

TARGET_ORGS = None#["WIB_HC"]
TARGET_PERIODS = ["PY3 Q4", "PY4 Q1","PY4 Q2","PY4 Q3"]

ALL_PERIODS = ["PY2 Q3", "PY2 Q4", "PY3 Q1", "PY3 Q2", "PY3 Q3", "PY3 Q4", "PY4 Q1","PY4 Q2","PY4 Q3"]

periods_to_run = TARGET_PERIODS if TARGET_PERIODS else ALL_PERIODS

for target_period in periods_to_run:                      #, "PY2 Q3", "PY2 Q4", "PY3 Q1", "PY3 Q2", "PY3 Q3", "PY3 Q4", "PY4 Q1"]:   ### specify period for file selection here. Could be adjusted to loop through all periods if desired.

    all_normalized = []
    all_errors = []
    all_mismatches = []  

    for org, data_types in file_directory.items():

        if TARGET_ORGS and org not in TARGET_ORGS:
            continue

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
        key_fields=["First Name", "Last Name"],     # minimal for now
        normalizers={
            "First Name": strict_alphabetic_normalize,
            "Last Name": strict_alphabetic_normalize,
        },
        required_fields=["First Name", "Last Name"],  # will drop invalid rows
        return_unhashed=True,                       # unhashed for easier debugging
    )
        
        ### key creator for entry level and linking to person database
        # No normalization because this is called after normalization is completed.  

        kc_strict = KeyCreator(
        key_fields=["First Name_normalized", "Last Name_normalized", "Date of Birth_normalized", "Zip Code_normalized"],
        required_fields=["First Name_normalized", "Last Name_normalized", "Date of Birth_normalized", "Zip Code_normalized"],
        return_unhashed=True,
        )

        kc_med_name_dob = KeyCreator(
        key_fields=["First Name_normalized", "Last Name_normalized", "Date of Birth_normalized"],
        required_fields=["First Name_normalized", "Last Name_normalized", "Date of Birth_normalized"],
        return_unhashed=True,
        )

        kc_med_name_zip = KeyCreator(
        key_fields=["First Name_normalized", "Last Name_normalized", "Zip Code_normalized"],
        required_fields=["First Name_normalized", "Last Name_normalized", "Zip Code_normalized"],
        return_unhashed=True,
        )

        kc_weak = KeyCreator(
        key_fields=["First Name_normalized","Last Name_normalized"],
        required_fields =["First Name_normalized","Last Name_normalized"],
        return_unhashed=True,
        )

        keycreators = [(kc_strict, "id_key_strict_name_dob_zip"),
                    (kc_med_name_dob, "id_key_medium_name_dob"),
                    (kc_med_name_zip, "id_key_medium_name_zip"),
                    (kc_weak, "id_key_weak_name")]


        multi_sheet_mode = len(workbook_definitions[target_book][workbook_format]) > 1

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
        engine = ValidationEngine(workbook_definitions, cross_rules= cross_rules, logging = LOGGING, log_description = LOG_DESCRIPTION)
        
        file_id = f"{org}|{period}".replace(" ", "_")

        engine.validate_workbook(
            file=file_id,
            workbook_type=target_book,
            workbook_format=workbook_format,
            dfs_by_sheet=dfs_by_sheet,
            keycreators= keycreators,
            passed_identity_sheet="Participant_Info"
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
    output_file = OUTPUT_DIRECTORY / f"gjc_validation_results_all_orgs_{target_period}.xlsx"
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        normalized_final.to_excel(writer, sheet_name="Normalized Data", index=False)
        errors_final.to_excel(writer, sheet_name="Validation Errors", index=False)
        if not mismatches_final.empty:
            mismatches_final.to_excel(writer, sheet_name="Key Mismatches", index=False)

    print(f"✅ Results written to {output_file}")

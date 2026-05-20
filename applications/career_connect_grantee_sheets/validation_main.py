"""
==============================
Career ConneCT Validation Main Script
==============================

This is the Career ConneCT validation main script. It instatiates the validation engine / workbook
loader with arguments that are specific to Career ConneCT data and file structure. If the pipeline
requires program specific data at somepoint, this should be its entryway. 

The file proceeds through the following sections: 

1. File selection - selecting files from a file directory object
2. Key specification - defining key creators for both sheet-level (within workbook) and person-level keys
3. Workbook loading - loading workbooks via the appropriate loader class
4. Validation - running the validation engine on the loaded workbooks
5. Key evaluation - assessing key presence/absence/duplication across sheets
6. Print out - consolidating and writing results to an Excel file

For more complete explanations of each section, see the comments within the code. 

Inputs: 
- File directory object from 'cc_file_directory.py' specifying file paths and metadata
- Workbook definitions from 'cc_column_label_list.py' specifying sheet structures and validation rules
- Crossrule definitions from 'cc_validation_cross_rule_sets.py'
- Key creator specifications, including key fields and normalizations
- Logging status (enabled as a validation engine argument)
- File Type, specified as a string to select files from the directory
- Period, specified as a string to select files from the directory (code will need to be adjusted to do this)

Outputs: 
- Excel file with multiple sheets:
    - Normalized Data: consolidated normalized dataset across all orgs/periods
    - Validation Errors: detailed log of validation errors encountered
    - Key Mismatches: log of key presence/absence/duplication issues across sheets

"""
### dataframe import
import pandas as pd 
from datetime import datetime
from config import OUTPUT_DIRECTORY


### General Engine Imports 
from validation_engine.validation_engine import ValidationEngine
from validation_engine.workbook_loader import WorkbookLoader, MultiWorkbookLoader
from validation_engine.key_creator import KeyCreator
from validation_engine.standard_normalizations import strict_alphabetic_normalize

### Application Specific Imports
from applications.career_connect_grantee_sheets.workbook_definitions import workbook_definitions
from applications.career_connect_grantee_sheets.file_directory import file_directory
from applications.career_connect_grantee_sheets.cross_rule_sets import CONNECTED_PRESENCE_RULES, CONDITIONALLY_BLANK_UNLESS_RULES, CONDITIONALLY_ALLOWED_RULES, CONDITIONALLY_REQUIRED_RULES , CONDITIONALLY_REQUIRED_BY_DATE_COMPARISON_RULES

### specify cross rule sets, these are dataset specific and should be adjusted for each program (e.g. GJC, CC, etc.)

cross_rules = [
            ("Connected Presence", CONNECTED_PRESENCE_RULES),
            ("Conditionally Blank", CONDITIONALLY_BLANK_UNLESS_RULES),
            ("Conditionally Allowed", CONDITIONALLY_ALLOWED_RULES),
            ("Conditionally Required", CONDITIONALLY_REQUIRED_RULES),
            ("Conditionally Required by Date", CONDITIONALLY_REQUIRED_BY_DATE_COMPARISON_RULES),
    ]

GRAB_LATEST = True
LOGGING = True
LOG_DESCRIPTION = "5/5 PY4 Q3 Reporting"

# TARGET_ORGS = ["Charter Oak State College Foundation"]
TARGET_ORGS = None
TARGET_PERIODS = ["PY4 Q3"]

ALL_PERIODS = ["PY2 Q3", "PY2 Q4", "PY3 Q1", "PY3 Q2", "PY3 Q3", "PY3 Q4", "PY4 Q1","PY4 Q2","PY4 Q3"]

periods_to_run = TARGET_PERIODS if TARGET_PERIODS else ALL_PERIODS

for target_period in periods_to_run:    

    all_normalized = []
    all_errors = []
    all_mismatches = []

    for org, data_types in file_directory.items():

        if TARGET_ORGS and org not in TARGET_ORGS:
            continue

        ##### Start - File selection ##### 

        ## This section loads a file path (or collection of filepaths) and associated meta-data 
        ## from a file directory specified by the user. Currently the user also still needs to  
        ## specify a dataset type value that is used to deliniate between file types in the directory.  

        ## File path and metadata are passed to workbook loader.  
        
        ## Current file types are:
        # 
        # For Career ConneCT - "training data" 
        # For Good Jobs Challenge - "TPI" and "SSI" 
        

        file_type = "training data"
        
        available_periods = list(data_types[file_type].keys())

        if not available_periods:
            continue  # no files available

        if target_period in available_periods:
            selected_period = target_period

        elif GRAB_LATEST:
            selected_period = list(data_types[file_type].keys())[-1]

            print(
                f"{org}: {target_period} not found. "
                f"Using latest available period {selected_period}."
            )

        else:
            print(
                f"{org}: {target_period} not found and GRAB_LATEST=False. Skipping."
            )
            continue

        print(f"Starting a run on {org} {file_type} @ {datetime.now()}")

        if file_type not in data_types:
            continue

        if data_types[file_type].get(selected_period) is None:
            continue

        file_meta = data_types[file_type][selected_period]
        file_path = file_meta["file path"]
        workbook_format = file_meta["format"]

        #### starting row for data ingestion, treated as the 'header' value in read_excel, it can take a value from the file itself 
        #### as it does here (if available), but it can also take a sheet specific value from the workbook_definitions object inside of 
        #### workbook loader if one is specified there. The order of precedence is goings to be : workbook_definitions -> file_meta -> default (0)

        starting_row = 0  # default starting row
        if "starting row" in file_meta and file_meta["starting row"] is not None:
            starting_row = file_meta["starting row"]

        ##### End - File Selection #####

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
        key_fields=["First Name", "Last Name", "Client Date of Birth", "Zip Code"],
        required_fields=["First Name", "Last Name", "Client Date of Birth", "Zip Code"],
        return_unhashed=True,
        )

        kc_med_name_dob = KeyCreator(
        key_fields=["First Name", "Last Name", "Client Date of Birth"],
        required_fields=["First Name", "Last Name", "Client Date of Birth"],
        return_unhashed=True,
        )

        kc_med_name_zip = KeyCreator(
        key_fields=["First Name", "Last Name", "Zip Code"],
        required_fields=["First Name", "Last Name", "Zip Code"],
        return_unhashed=True,
        )

        kc_weak = KeyCreator(
        key_fields=["First Name","Last Name"],
        required_fields =["First Name","Last Name"],
        return_unhashed=True,
        )

        keycreators = [(kc_strict, "id_key_strict_name_dob_zip"),
                    (kc_med_name_dob, "id_key_medium_name_dob"),
                    (kc_med_name_zip, "id_key_medium_name_zip"),
                    (kc_weak, "id_key_weak_name")]
        
        ##### Start - Workbook Loading ##### 

        ## Start the workbook class that is appropriate based on whether you have a 
        ## single file paths or set of file paths. Workbook loader passes a dictionary  
        ## of sheet names and datasets to the validation engine.  

        multi_sheet_mode = len(workbook_definitions[file_type][workbook_format]) > 1

        print(f"{org} {file_type} - Beginning File Load @ {datetime.now()}")

        # ✅ Choose single vs. multi loader
        if isinstance(file_path, (list, set, tuple)):
            print(f"📘 Loading multiple workbooks for {org} ({len(file_path)} files)")
            loader = MultiWorkbookLoader(
                file_paths=file_path,
                workbook_type=workbook_format,
                sheet_defs=workbook_definitions[file_type],
                starting_row= starting_row,
                dynamic=True,
                keycreator=sheetlink_keycreator,
                multi_sheet_mode=multi_sheet_mode
            )
            loader.preprocess_all()
            dfs_by_sheet = loader.load_all()  # dict[sheet_name] = combined_df

        else:
            print(f"📗 Loading single workbook for {org}")
            loader = WorkbookLoader(
                file_path=file_path,
                workbook_type=workbook_format,
                sheet_defs=workbook_definitions[file_type],
                starting_row = starting_row,
                dynamic=True,
                keycreator=sheetlink_keycreator,
                multi_sheet_mode=multi_sheet_mode
            )
            loader.preprocess_excel()
            dfs_by_sheet = loader.load_sheets()

        print(f"{org} {file_type} - Finishing File Load @ {datetime.now()}")

        ###### End - Workbook Loading ######

        ###### Start - Validation ######
        
        ## This section calls the validation engine, which runs both data normalization ('cc_validation_column_types.py')
        ## and cross rule checks ('cc_cross_rule_engine.py'). It relies on the workbook definition object from 
        ## 'cc_column_label_list.py' as well as the sheet/dataset dictionary generated by the workbook loader.  

        ## Section produces both the normalized data sets (dfs) and the error list generated by normalization (errs).

        engine = ValidationEngine(workbook_definitions, cross_rules= cross_rules, logging = LOGGING, log_description=LOG_DESCRIPTION)
        
        file_id = f"{org}|{target_period}".replace(" ", "_")

        ##### End - Validation #####

        print(f"{org} {file_type} - Starting Validation @ {datetime.now()}")

        engine.validate_workbook(
            file=file_id,
            workbook_type=file_type,
            workbook_format=workbook_format,
            dfs_by_sheet=dfs_by_sheet,
            keycreators=keycreators,
            passed_identity_sheet= "Personal Information"
        )

        ##### Start - Key Evaluation  ##### 

        ## This section assesses whether the keys that are present in each of the sheet/dataset pairings 
        ## produced by the validation engine are present/absent/duplicated elsewhere. It logs the particular 
        ## issue and its location. It removes problematic keys and passes the normalized data to the final print out. 

        ## It's potentially problematic that this dedupe is happening after cross-rule application. 
        ## It could cause errors upstream.


        #### cross-rules require key issues to be resolved and normalization errors 
        #### on duplicated rows are redundant, so validation happens afterwards. 
        ####actually need to move key matching inside of the workbook


        dfs = list(engine.normalized_data.items())  # [(sheet_name, df), ...]

        errs = engine.get_all_errors()
        if not errs.empty:
            errs["org"] = org
            errs["period"] = target_period
            all_errors.append(errs)

        mismatches = pd.DataFrame(engine.mismatches)    
        if not mismatches.empty:
            mismatches["org"] = org
            mismatches["period"] = target_period

        all_mismatches.append(engine.mismatches)
        all_normalized.append(engine.single_sheet)
        ##### End - Key Evaluation #####

    ###### Start - Print Out ###### 

    ## This section consoldiates the ouput from the different validation processes into a single report. 

    ## it draws from:
    #           all_normalized (finalized in the key evaluation section but produced in validation)
    #           all_errors (produced in the validation stage)
    #           all_mismatches (produced in the key evaluation stage)

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
    output_file = OUTPUT_DIRECTORY / f"cc_validation_results_all_orgs_{target_period}.xlsx"

    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        normalized_final.to_excel(writer, sheet_name="Normalized Data", index=False)
        errors_final.to_excel(writer, sheet_name="Validation Errors", index=False)
        if not mismatches_final.empty:
            mismatches_final.to_excel(writer, sheet_name="Key Mismatches", index=False)

    print(f"✅ Results written to {output_file}")

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

### Engine Imports 
from cc_validation_engine import ValidationEngine
from cc_validation_workbook_loader import WorkbookLoader, MultiWorkbookLoader
from cc_workbook_definitions import workbook_definitions
from cc_file_directory import cc_file_directory
from cc_key_creator import KeyCreator
from cc_standard_normalizations import strict_alphabetic_normalize
from cc_validation_cross_rule_sets import CONNECTED_PRESENCE_RULES, CONDITIONALLY_BLANK_UNLESS_RULES, CONDITIONALLY_ALLOWED_RULES, CONDITIONALLY_REQUIRED_RULES , CONDITIONALLY_REQUIRED_BY_DATE_COMPARISON_RULES

from dotenv import load_dotenv
import os

### Specify absolute path for file loading. Need to build out directory for this to work effectively. 
# load_dotenv()
# BASE_DIR = os.getenv("CC_DATA_DIR")

# if not BASE_DIR:
#     raise RuntimeError("CC_DATA_DIR is not set in the .env file.")

### specify cross rule sets, these are dataset specific and should be adjusted for each program (e.g. GJC, CC, etc.)

cross_rules = [
            ("Connected Presence", CONNECTED_PRESENCE_RULES),
            ("Conditionally Blank", CONDITIONALLY_BLANK_UNLESS_RULES),
            ("Conditionally Allowed", CONDITIONALLY_ALLOWED_RULES),
            ("Conditionally Required", CONDITIONALLY_REQUIRED_RULES),
            ("Conditionally Required by Date", CONDITIONALLY_REQUIRED_BY_DATE_COMPARISON_RULES),
    ]

for target_period in ["PY2 Q2", "PY2 Q3", "PY2 Q4", "PY3 Q1", "PY3 Q2", "PY3 Q3", "PY3 Q4", "PY4 Q1"]:   ### specify period for file selection here. Could be adjusted to loop through all periods if desired.

    # Containers for results
    all_normalized = []
    all_errors = []
    all_mismatches = []


    for org, data_types in cc_file_directory.items():
        
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
        
        if file_type not in data_types:
            continue

        # Get all periods and pick the last one (sorted alphanumerically)
        periods = sorted(data_types[file_type].keys())
        if target_period not in periods:
            continue
        period = target_period

        file_meta = data_types[file_type][period]
        file_path = file_meta["file path"]
        workbook_format = file_meta["format"]

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
        required_fields=["First Name, Last Name", "Client Date of Birth", "Zip Code"],
        return_unhashed=True,
        )

        kc_med_name_dob = KeyCreator(
        key_fields=["First Name", "Last Name", "Client Date of Birth"],
        required_fields=["First Name, Last Name","Client Date of Birth"],
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

        keycreators = [(kc_strict, "id_key_strict_name_dob_zip"),
                    (kc_med_name_dob, "id_key_medium_name_dob"),
                    (kc_med_name_zip, "id_key_medium_name_zip"),
                    (kc_weak, "id_key_weak_name")]
        
        ##### Start - Workbook Loading ##### 

        ## Start the workbook class that is appropriate based on whether you have a 
        ## single file paths or set of file paths. Workbook loader passes a dictionary  
        ## of sheet names and datasets to the validation engine.  

        # ✅ Choose single vs. multi loader
        if isinstance(file_path, (list, set, tuple)):
            print(f"📘 Loading multiple workbooks for {org} ({len(file_path)} files)")
            loader = MultiWorkbookLoader(
                file_paths=file_path,
                workbook_type=workbook_format,
                sheet_defs=workbook_definitions[file_type],
                dynamic=True,
                keycreator=sheetlink_keycreator
            )
            loader.preprocess_all()
            dfs_by_sheet = loader.load_all()  # dict[sheet_name] = combined_df

        else:
            print(f"📗 Loading single workbook for {org}")
            loader = WorkbookLoader(
                file_path=file_path,
                workbook_type=workbook_format,
                sheet_defs=workbook_definitions[file_type],
                dynamic=True,
                keycreator=sheetlink_keycreator
            )
            loader.preprocess_excel()
            dfs_by_sheet = loader.load_sheets()

        ###### End - Workbook Loading ######

        ###### Start - Validation ######
        
        ## This section calls the validation engine, which runs both data normalization ('cc_validation_column_types.py')
        ## and cross rule checks ('cc_cross_rule_engine.py'). It relies on the workbook definition object from 
        ## 'cc_column_label_list.py' as well as the sheet/dataset dictionary generated by the workbook loader.  

        ## Section produces both the normalized data sets (dfs) and the error list generated by normalization (errs).

        engine = ValidationEngine(workbook_definitions, cross_rules= cross_rules, logging = True)
        
        file_id = f"{org}|{period}".replace(" ", "_")

        ##### End - Validation #####

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
            errs["period"] = period
            all_errors.append(errs)

        mismatches = pd.DataFrame(engine.mismatches)    
        if not mismatches.empty:
            mismatches["org"] = org
            mismatches["period"] = period

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
    output_file = rf"C:\Users\webbm\OneDrive - State of Connecticut\Documents\cc_validation_results_all_orgs_{target_period}.xlsx"


    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        normalized_final.to_excel(writer, sheet_name="Normalized Data", index=False)
        errors_final.to_excel(writer, sheet_name="Validation Errors", index=False)
        if not mismatches_final.empty:
            mismatches_final.to_excel(writer, sheet_name="Key Mismatches", index=False)

    print(f"✅ Results written to {output_file}")

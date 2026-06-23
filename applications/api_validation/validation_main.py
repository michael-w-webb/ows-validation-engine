from validation_engine.key_creator import KeyCreator
from validation_engine.standard_normalizations import (
    strict_alphabetic_normalize
)
from validation_engine.workbook_loader import WorkbookLoader
from validation_engine.validation_engine import ValidationEngine

from config import OUTPUT_DIRECTORY
import json 
import pandas as pd 

definition_path = OUTPUT_DIRECTORY / "8d5a0278-1abe-4d74-abe2-0c99aa0a5ac2.json"

with open(definition_path, "r") as f:

    workbook_definitions = json.load(f)


def build_link_column_names(linking_columns):

    """
    Converts linking column definitions into
    standardized link key column names.

    Example:
        ["First Name", "Last Name"]

    becomes:
        ["link_key_1", "link_key_2"]
    """

    return [
        f"link_key_{i + 1}"
        for i in range(len(linking_columns))
    ]


def extract_linking_columns_from_sheet(sheet_config):

    """
    Pulls linking columns from a single
    sheet definition.
    """

    return sheet_config.get(
        "linking_columns",
        []
    )


def extract_linking_columns_from_workbook_definition(
    workbook_definitions,
    workbook_format=None,
    file_type=None,
    sheet_name=None
):

    """
    Traverses workbook definition structure:

        workbook_format
            -> file_type
                -> sheet_name
                    -> config

    and extracts linking columns.
    """

    if workbook_format is None:
        workbook_format = next(
            iter(workbook_definitions)
        )

    if file_type is None:
        file_type = next(
            iter(
                workbook_definitions[
                    workbook_format
                ]
            )
        )

    sheet_defs = (
        workbook_definitions[
            workbook_format
        ][
            file_type
        ]
    )

    if sheet_name is None:
        sheet_name = next(iter(sheet_defs))

    sheet_config = sheet_defs[sheet_name]

    return extract_linking_columns_from_sheet(
        sheet_config
    )


def build_sheetlink_keycreator(
    workbook_definitions,
    workbook_format=None,
    file_type=None,
    sheet_name=None,
    normalizer=strict_alphabetic_normalize,
    return_unhashed=True
):

    """
    Dynamically creates a KeyCreator using
    linking_columns from workbook definitions.

    Example linking columns:
        ["First Name", "Last Name"]

    Resulting key fields:
        ["link_key_1", "link_key_2"]
    """

    linking_columns = (
        extract_linking_columns_from_workbook_definition(
            workbook_definitions=workbook_definitions,
            workbook_format=workbook_format,
            file_type=file_type,
            sheet_name=sheet_name
        )
    )

    link_key_columns = build_link_column_names(
        linking_columns
    )

    normalizers = {
        col: normalizer
        for col in link_key_columns
    }

    return KeyCreator(
        key_fields=link_key_columns,
        normalizers=normalizers,
        required_fields=link_key_columns,
        return_unhashed=return_unhashed
    )

def run_validation():

    all_normalized = []
    all_errors = []
    all_mismatches = []

    org = "Charter Oak"
    target_period = "PY4 Q2"

    sheetlink_keycreator = build_sheetlink_keycreator(
        workbook_definitions
    )

    file_type = next(iter(workbook_definitions))

    workbook_format = next(
        iter(
            workbook_definitions[file_type]
        )
    )

    file_path = OUTPUT_DIRECTORY / "Career ConneCT Staggered DataEntry Spreadsheet COSCF December2025FINAL.xlsx"

    multi_sheet_mode =  len(workbook_definitions[file_type][workbook_format])>1

    loader = WorkbookLoader(
                file_path=file_path,
                workbook_type=workbook_format,
                sheet_defs=workbook_definitions[file_type],
                dynamic=True,
                keycreator=sheetlink_keycreator,
                multi_sheet_mode=multi_sheet_mode,
                api_source = True
            )

    loader.preprocess_excel()
    dfs_by_sheet = loader.load_sheets()

    print(dfs_by_sheet)

    engine = ValidationEngine(workbook_definitions, logging = False)

    engine.validate_workbook(
        file= "test|check",
        workbook_type=file_type,
        workbook_format=workbook_format,
        dfs_by_sheet=dfs_by_sheet,
        passed_identity_sheet= "Personal Information"
    )

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
    all_normalized.append(engine.returnable_data)
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

def main():
    run_validation()

if __name__ == "__main__":
    main()
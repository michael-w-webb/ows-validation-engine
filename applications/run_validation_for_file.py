from validation_engine.validation_engine import ValidationEngine
from validation_engine.workbook_loader import WorkbookLoader
from validation_engine.key_creator import KeyCreator
from validation_engine.standard_normalizations import strict_alphabetic_normalize

import pickle

def run_validation_for_file(
    *,
    file_path,
    workbook_format,
    file_type,
    workbook_definitions,
    cross_rules,
    org="TEST_ORG",
    target_period="TEST_Q1",
    starting_row=0,
    db_path=None,
    logging=True,
    log_description="Integration Test",
):
    """
    Execute a complete validation run against a single workbook.

    Intended for:
        - integration testing
        - debugging
        - ad-hoc validation

    Returns
    -------
    engine : ValidationEngine
        Completed validation engine instance.
    """

    # --------------------------------------------------
    # Key creators
    # --------------------------------------------------

    sheetlink_keycreator = KeyCreator(
        key_fields=["First Name", "Last Name"],
        normalizers={
            "First Name": strict_alphabetic_normalize,
            "Last Name": strict_alphabetic_normalize,
        },
        required_fields=["First Name", "Last Name"],
        return_unhashed=True,
    )

    kc_strict = KeyCreator(
        key_fields=[
            "First Name",
            "Last Name",
            "Client Date of Birth",
            "Zip Code",
        ],
        required_fields=[
            "First Name",
            "Last Name",
            "Client Date of Birth",
            "Zip Code",
        ],
        return_unhashed=True,
    )

    kc_med_name_dob = KeyCreator(
        key_fields=[
            "First Name",
            "Last Name",
            "Client Date of Birth",
        ],
        required_fields=[
            "First Name",
            "Last Name",
            "Client Date of Birth",
        ],
        return_unhashed=True,
    )

    kc_med_name_zip = KeyCreator(
        key_fields=[
            "First Name",
            "Last Name",
            "Zip Code",
        ],
        required_fields=[
            "First Name",
            "Last Name",
            "Zip Code",
        ],
        return_unhashed=True,
    )

    kc_weak = KeyCreator(
        key_fields=[
            "First Name",
            "Last Name",
        ],
        required_fields=[
            "First Name",
            "Last Name",
        ],
        return_unhashed=True,
    )

    keycreators = [
        (kc_strict, "id_key_strict_name_dob_zip"),
        (kc_med_name_dob, "id_key_medium_name_dob"),
        (kc_med_name_zip, "id_key_medium_name_zip"),
        (kc_weak, "id_key_weak_name"),
    ]

    # --------------------------------------------------
    # Workbook load
    # --------------------------------------------------

    multi_sheet_mode = (
        len(
            workbook_definitions[file_type][workbook_format]
        ) > 1
    )

    loader = WorkbookLoader(
        file_path=file_path,
        workbook_type=workbook_format,
        sheet_defs=workbook_definitions[file_type],
        starting_row=starting_row,
        dynamic=True,
        keycreator=sheetlink_keycreator,
        multi_sheet_mode=multi_sheet_mode,
    )

    loader.preprocess_excel()

    dfs_by_sheet = loader.load_sheets()

    with open(
        "tests/fixtures/career_connect_loader_output.pkl",
        "wb"
    ) as f:
        pickle.dump(dfs_by_sheet, f)    

    # --------------------------------------------------
    # Validation
    # --------------------------------------------------

    engine = ValidationEngine(
        workbook_definitions,
        cross_rules=cross_rules,
        logging=logging,
        log_description=log_description,
        db_path=db_path,  # <-- important
    )

    file_id = f"{org}|{target_period}"

    engine.validate_workbook(
        file=file_id,
        workbook_type=file_type,
        workbook_format=workbook_format,
        dfs_by_sheet=dfs_by_sheet,
        keycreators=keycreators,
        passed_identity_sheet="Personal Information",
    )

    engine.db_logger.close()

    return engine
import logging
import pandas as pd

from pathlib import Path
from time import perf_counter
from datetime import datetime

from validation_engine.key_creator import (
    KeyCreator
)

from validation_engine.standard_normalizations import (
    strict_alphabetic_normalize
)

from validation_engine.workbook_loader import (
    WorkbookLoader
)

from validation_engine.validation_engine import (
    ValidationEngine
)

logger = logging.getLogger(__name__)


class ValidationService:

    """
    Service responsible for executing
    workbook validation runs against
    persisted workbook definitions.
    """

    def __init__(
        self,
        output_directory,
        validation_run_repository
    ):

        self.output_directory = (
            Path(output_directory)
        )

        self.validation_run_repository = (
            validation_run_repository
        )

    # ========================================
    # Public Validation Entry Point
    # ========================================

    def run_validation(
        self,
        workbook_definition,
        validation_run_id,
        uploaded_file_path,
        org,
        target_period,
        passed_identity_sheet=(
            "Personal Information"
        )
    ):

        start_time = perf_counter()

        self.validation_run_repository.update_status(
            validation_run_id,
            "running"
        )

        logger.info(
            (
                "Starting validation run "
                "for org %s period %s"
            ),
            org,
            target_period
        )

        try:

            all_normalized = []
            all_errors = []
            all_mismatches = []

            sheetlink_keycreator = (
                self.build_sheetlink_keycreator(
                    workbook_definition
                )
            )

            workbook_name = next(
                iter(workbook_definition)
            )

            workbook_format = next(
                iter(
                    workbook_definition[
                        workbook_name
                    ]
                )
            )

            multi_sheet_mode = (
                len(
                    workbook_definition[
                        workbook_name
                    ][
                        workbook_format
                    ]
                ) > 1
            )

            logger.info(
                (
                    "Initializing workbook "
                    "loader for workbook %s "
                    "format %s"
                ),
                workbook_name,
                workbook_format
            )

            loader = WorkbookLoader(

                file_path=uploaded_file_path,

                workbook_type=workbook_format,

                sheet_defs=(
                    workbook_definition[
                        workbook_name
                    ]
                ),

                dynamic=True,

                keycreator=(
                    sheetlink_keycreator
                ),

                multi_sheet_mode=(
                    multi_sheet_mode
                ),

                api_source=True
            )

            logger.info(
                "Preprocessing workbook"
            )

            loader.preprocess_excel()

            logger.info(
                "Loading workbook sheets"
            )

            dfs_by_sheet = (
                loader.load_sheets()
            )

            logger.info(
                "Initializing validation engine"
            )

            engine = ValidationEngine(
                workbook_definition,
                logging=False
            )

            logger.info(
                "Running workbook validation"
            )

            engine.validate_workbook(

                file=(
                    f"{org}|{target_period}"
                ),

                workbook_type=(
                    workbook_name
                ),

                workbook_format=(
                    workbook_format
                ),

                dfs_by_sheet=(
                    dfs_by_sheet
                ),

                passed_identity_sheet=(
                    passed_identity_sheet
                )
            )

            logger.info(
                "Collecting validation outputs"
            )

            errs = (
                engine.get_all_errors()
            )

            if not errs.empty:

                errs["org"] = org

                errs["period"] = (
                    target_period
                )

                all_errors.append(errs)

            mismatches = pd.DataFrame(
                engine.mismatches
            )

            if not mismatches.empty:

                mismatches["org"] = org

                mismatches["period"] = (
                    target_period
                )

            all_mismatches.append(
                engine.mismatches
            )

            all_normalized.append(
                engine.returnable_data
            )

            logger.info(
                (
                    "Building consolidated "
                    "validation report"
                )
            )

            normalized_final = pd.concat(
                all_normalized,
                ignore_index=True
            )

            errors_final = (
                pd.concat(
                    all_errors,
                    ignore_index=True
                )

                if all_errors

                else pd.DataFrame()
            )

            flat_rows = [

                row

                for sublist in (
                    all_mismatches
                )

                for row in sublist
            ]

            mismatches_final = (
                pd.DataFrame(flat_rows)
            )

            timestamp = datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )

            output_file = (
                self.output_directory
                / (
                    "validation_results_"
                    f"{org}_"
                    f"{target_period}_"
                    f"{timestamp}.xlsx"
                )
            )

            logger.info(
                (
                    "Writing validation "
                    "report to %s"
                ),
                output_file
            )

            with pd.ExcelWriter(
                output_file,
                engine="openpyxl"
            ) as writer:

                normalized_final.to_excel(
                    writer,
                    sheet_name=(
                        "Normalized Data"
                    ),
                    index=False
                )

                errors_final.to_excel(
                    writer,
                    sheet_name=(
                        "Validation Errors"
                    ),
                    index=False
                )

                if (
                    not mismatches_final.empty
                ):

                    mismatches_final.to_excel(
                        writer,
                        sheet_name=(
                            "Key Mismatches"
                        ),
                        index=False
                    )

            logger.info(
                (
                    "Validation completed "
                    "successfully"
                )
            )

            runtime_seconds = (
                round(
                    perf_counter() - start_time,
                    2
                )
            )

            self.validation_run_repository.complete_run(

                validation_run_id=(
                    validation_run_id
                ),

                output_file_path=(
                    output_file
                ),

                runtime_seconds=(
                    runtime_seconds
                ),

                sheet_count=(
                    len(dfs_by_sheet)
                ),

                normalized_row_count=(
                    len(normalized_final)
                ),

                error_count=(
                    len(errors_final)
                ),

                mismatch_count=(
                    len(mismatches_final)
                )
            )

            return {

                "output_file":
                    output_file,

                "normalized_row_count":
                    len(normalized_final),

                "error_count":
                    len(errors_final),

                "mismatch_count":
                    len(mismatches_final),

                "sheet_count":
                    len(dfs_by_sheet),

                "org":
                    org,

                "target_period":
                    target_period,
                
                "runtime_seconds":
                    runtime_seconds
            }

        except Exception:

            logger.exception(
                (
                    "Validation run failed "
                    "for org %s period %s"
                ),
                org,
                target_period
            )

            self.validation_run_repository.fail_run(

                validation_run_id=(
                    validation_run_id
                ),

                failure_message=(
                    "Validation execution failed"
                )
            )

            raise

    # ========================================
    # KeyCreator Helpers
    # ========================================

    def build_link_column_names(
        self,
        linking_columns
    ):

        """
        Converts linking columns into
        standardized link key names.
        """

        return [

            f"link_key_{i + 1}"

            for i in range(
                len(linking_columns)
            )
        ]

    def extract_linking_columns_from_sheet(
        self,
        sheet_config
    ):

        """
        Pull linking columns from
        a single sheet definition.
        """

        return sheet_config.get(
            "linking_columns",
            []
        )

    def extract_linking_columns_from_workbook_definition(
        self,
        workbook_definition,
        workbook_name=None,
        workbook_format=None,
        sheet_name=None
    ):

        """
        Traverse workbook definition
        structure and extract linking
        columns from a sheet.
        """

        if workbook_name is None:

            workbook_name = next(
                iter(workbook_definition)
            )

        if workbook_format is None:

            workbook_format = next(
                iter(
                    workbook_definition[
                        workbook_name
                    ]
                )
            )

        sheet_defs = (
            workbook_definition[
                workbook_name
            ][
                workbook_format
            ]
        )

        if sheet_name is None:

            sheet_name = next(
                iter(sheet_defs)
            )

        sheet_config = (
            sheet_defs[sheet_name]
        )

        return (
            self.extract_linking_columns_from_sheet(
                sheet_config
            )
        )

    def build_sheetlink_keycreator(
        self,
        workbook_definition,
        workbook_name=None,
        workbook_format=None,
        sheet_name=None,
        normalizer=(
            strict_alphabetic_normalize
        ),
        return_unhashed=True
    ):

        """
        Build KeyCreator dynamically
        from workbook definition
        linking columns.
        """

        linking_columns = (

            self.extract_linking_columns_from_workbook_definition(

                workbook_definition=(
                    workbook_definition
                ),

                workbook_name=(
                    workbook_name
                ),

                workbook_format=(
                    workbook_format
                ),

                sheet_name=sheet_name
            )
        )

        link_key_columns = (
            self.build_link_column_names(
                linking_columns
            )
        )

        normalizers = {

            col: normalizer

            for col in (
                link_key_columns
            )
        }

        return KeyCreator(

            key_fields=(
                link_key_columns
            ),

            normalizers=normalizers,

            required_fields=(
                link_key_columns
            ),

            return_unhashed=(
                return_unhashed
            )
        )
import logging

logger = logging.getLogger(__name__)


def extract_workbook_structure(
    workbook,
    sheet_header_rows
):
    """
    Extract workbook column structure using
    per-sheet header row configuration.
    """

    logger.info(
        "Beginning workbook structure extraction"
    )

    workbook_structure = {}

    for sheet_name in workbook.sheetnames:

        logger.info(
            "Inspecting worksheet: %s",
            sheet_name
        )

        try:

            ws = workbook[sheet_name]

            current_header_row = (
                sheet_header_rows[sheet_name]
            )

            logger.info(
                "Using header row %s for sheet %s",
                current_header_row,
                sheet_name
            )

            # =================================
            # Blank / invalid worksheet handling
            # =================================

            if ws.max_row is None:

                logger.warning(
                    "Worksheet %s has no rows",
                    sheet_name
                )

                workbook_structure[
                    sheet_name
                ] = []

                continue

            if ws.max_column is None:

                logger.warning(
                    "Worksheet %s has no columns",
                    sheet_name
                )

                workbook_structure[
                    sheet_name
                ] = []

                continue

            if current_header_row > ws.max_row:

                logger.warning(
                    (
                        "Header row %s exceeds "
                        "worksheet max row %s "
                        "for sheet %s"
                    ),
                    current_header_row,
                    ws.max_row,
                    sheet_name
                )

                workbook_structure[
                    sheet_name
                ] = []

                continue

            # =================================
            # Header extraction
            # =================================

            try:

                header_cells = ws[
                    current_header_row
                ]

            except (
                IndexError,
                ValueError,
                TypeError
            ):

                logger.warning(
                    (
                        "Unable to extract "
                        "header row %s "
                        "for sheet %s"
                    ),
                    current_header_row,
                    sheet_name
                )

                workbook_structure[
                    sheet_name
                ] = []

                continue

            # =================================
            # Entirely blank header row
            # =================================

            if not any(
                cell.value is not None
                for cell in header_cells
            ):

                logger.warning(
                    (
                        "Header row %s is blank "
                        "for sheet %s"
                    ),
                    current_header_row,
                    sheet_name
                )

                workbook_structure[
                    sheet_name
                ] = []

                continue

            # =================================
            # Extract columns
            # =================================

            columns = [
                str(cell.value).strip()
                for cell in header_cells
                if cell.value is not None
            ]

            logger.info(
                (
                    "Extracted %s columns "
                    "from sheet %s"
                ),
                len(columns),
                sheet_name
            )

            workbook_structure[
                sheet_name
            ] = columns

        except Exception as sheet_error:

            logger.exception(
                (
                    "Unexpected error while "
                    "extracting structure "
                    "for sheet %s"
                ),
                sheet_name
            )

            workbook_structure[
                sheet_name
            ] = [
                f"ERROR: {sheet_error}"
            ]

    logger.info(
        "Completed workbook structure extraction"
    )

    return workbook_structure
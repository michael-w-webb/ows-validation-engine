from validation_engine.domain.workbook_definition import (
    WorkbookDefinition
)

from validation_engine.domain.workbook_format import (
    WorkbookFormat
)

from validation_engine.domain.sheet_definition import (
    SheetDefinition
)

from validation_engine.domain.canonical_column import (
    CanonicalColumn
)


def workbook_definition_from_legacy_dict(
    workbook_type: str,
    legacy_definition: dict
) -> WorkbookDefinition:
    """
    Convert legacy workbook_definitions structure into
    domain objects.
    """

    workbook_definition = WorkbookDefinition(
        workbook_type=workbook_type
    )

    for format_name, format_config in legacy_definition.items():

        workbook_format = WorkbookFormat(
            format_name=format_name,
            is_multi_sheet=len(format_config) > 1
        )

        for sheet_name, sheet_config in format_config.items():

            sheet_definition = SheetDefinition(
                sheet_name=sheet_name,
                expected_sheet_names=[sheet_name],
                starting_row=sheet_config.get(
                    "starting_row",
                    0
                ),
                starting_column=sheet_config.get(
                    "starting_column",
                    0
                ),
                columns_used=sheet_config.get(
                    "columns_used"
                )
            )

            labels = sheet_config.get("labels", {})

            accepted_responses = sheet_config.get(
                "accepted_responses",
                {}
            )

            for canonical_name in labels.keys():

                column = (
                    CanonicalColumn
                    .from_legacy_definition(
                        canonical_name,
                        labels,
                        accepted_responses
                    )
                )

                sheet_definition.canonical_columns.append(
                    column
                )

            workbook_format.sheet_definitions.append(
                sheet_definition
            )

        workbook_definition.formats.append(
            workbook_format
        )

    return workbook_definition
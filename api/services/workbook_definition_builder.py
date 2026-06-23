from collections import defaultdict
from config import OUTPUT_DIRECTORY
import json 
import logging

logger = logging.getLogger(__name__)


class WorkbookDefinitionBuilder:

    """
    Builds validation-engine-native
    workbook definition objects
    from WorkbookSession drafts.
    """

    def build_workbook_definition(
        self,
        session
    ):

        logger.info(
            (
                "Building workbook definition "
                "for session %s"
            ),
            session.resource_id
        )

        dataset_name = (
            session.workbook_name
        )

        format_name = (
            session.format_name
        )

        workbook_definition = {
            dataset_name: {
                format_name: {}
            }
        }

        format_container = (
            workbook_definition[
                dataset_name
            ][
                format_name
            ]
        )

        for sheet_name in (
            session.selected_sheets
        ):

            sheet_fields = [

                field

                for field in (
                    session.canonical_definitions
                )

                if (
                    field["sheet_name"]
                    == sheet_name
                )

                and (
                    field.get(
                        "included",
                        True
                    )
                )
            ]

            labels = {}

            accepted_responses = {}

            columns_used = []

            for field in sheet_fields:

                canonical_name = (
                    field[
                        "canonical_name"
                    ]
                )

                column_name = (
                    field[
                        "column_name"
                    ]
                )

                columns_used.append(
                    canonical_name
                )

                #
                # LABEL VARIANTS
                #

                labels[
                    canonical_name
                ] = list(
                    set(
                        field.get(
                            "column_variants",
                            []
                        )
                        + [column_name]
                    )
                )

                #
                # ACCEPTED RESPONSES
                #

                accepted_response = {

                    "type": (
                        field.get(
                            "column_type"
                        )
                        or "unspecified"
                    )
                }

                if field.get(
                    "required"
                ):

                    accepted_response[
                        "required"
                    ] = True

                if (
                    field.get(
                        "accepted_responses"
                    )
                    is not None
                ):

                    accepted_response[
                        "accepted_responses"
                    ] = (
                        field[
                            "accepted_responses"
                        ]
                    )

                accepted_responses[
                    canonical_name
                ] = (
                    accepted_response
                )

            format_container[
                sheet_name
            ] = {

                "labels":
                    labels,

                "accepted_responses":
                    accepted_responses,

                # "columns_used":
                #     columns_used,

                "starting_row":
                    session.sheet_header_rows.get(
                        sheet_name,
                        1
                    )-1,

                "starting_column":
                    0,

                "sheet_name":
                    sheet_name,

                "linking_columns":
                    session.linking_rules.get(
                        sheet_name,
                        []
                    )
            }

        logger.info(
            (
                "Workbook definition "
                "built successfully"
            )
        )

        session.workbook_definition = (
            workbook_definition
        )


        with open(
            OUTPUT_DIRECTORY / f"{session.resource_id}.json",
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                workbook_definition,
                f,
                indent=4,
                ensure_ascii=False
            )


        return session
from pathlib import Path

from sqlalchemy import column

from .workbook_loader import load_workbook_safe

from .sheet_inspector import (
    extract_workbook_structure
)

from .workbook_session import (
    WorkbookSession
)

from api.services.temp_storage import (
    create_temp_file,
    load_temp_file_path,
    update_resource_metadata,
    get_resource_metadata
)

import logging
import re

logger = logging.getLogger(__name__)


class ParserService:

    def create_session(
        self,
        contents,
        filename,
        workbook_name,
        format_name,
        is_multi_sheet,
        header_row=1
    ):

        logger.info(
            "Creating workbook session for %s",
            filename
        )

        try:

            suffix = Path(filename).suffix

            resource_id = create_temp_file(
                contents=contents,
                suffix=suffix
            )

            file_path = load_temp_file_path(
                resource_id
            )

            workbook = load_workbook_safe(
                file_path
            )

            sheet_header_rows = {
                sheet: header_row
                for sheet in workbook.sheetnames
            }

            update_resource_metadata(
                resource_id,
                {
                    "sheet_header_rows":
                        sheet_header_rows,
                    "workbook_name":
                        workbook_name,
                    "format_name":
                        format_name,
                    "is_multi_sheet":
                        is_multi_sheet,
                    "selected_sheets": []
                }
            )

            workbook_structure = (
                extract_workbook_structure(
                    workbook,
                    sheet_header_rows
                )
            )

            logger.info(
                (
                    "Created workbook session %s "
                    "with %s sheets"
                ),
                resource_id,
                len(workbook.sheetnames)
            )

            return WorkbookSession(
                resource_id=resource_id,
                file_path=file_path,
                workbook_name=workbook_name,
                format_name=format_name,
                is_multi_sheet=is_multi_sheet,
                sheet_header_rows=sheet_header_rows,
                workbook_structure=workbook_structure,
                selected_sheets=[]
            )

        except Exception:

            logger.exception(
                (
                    "Failed creating workbook "
                    "session for workbook %s"
                ),
                filename
            )

            raise

    def load_session(
        self,
        resource_id
    ):

        try:

            logger.info(
                "Loading workbook session %s",
                resource_id
            )

            file_path = load_temp_file_path(
                resource_id
            )

            metadata = get_resource_metadata(
                resource_id
            )

            if metadata is None:
                metadata = {}

            sheet_header_rows = metadata.get(
                "sheet_header_rows",
                {}
            )

            workbook = load_workbook_safe(
                file_path
            )

            workbook_structure = (
                extract_workbook_structure(
                    workbook,
                    sheet_header_rows
                )
            )

            return WorkbookSession(
                resource_id=resource_id,
                file_path=file_path,
                workbook_name=metadata.get(
                    "workbook_name"
                ),
                format_name=metadata.get(
                    "format_name"
                ),
                is_multi_sheet=metadata.get(
                    "is_multi_sheet",
                    False
                ),
                current_step=metadata.get(
                    "current_step",
                    "upload"
                ),
                selected_sheets=metadata.get(
                    "selected_sheets",
                    []
                ),
                linking_rules=metadata.get(
                    "linking_rules",
                    {}
                ),
                canonical_mappings=metadata.get(
                    "canonical_mappings",
                    []
                ),    
                canonical_definitions=metadata.get(
                    "canonical_definitions",
                    []
                ),
                sheet_header_rows=sheet_header_rows,
                workbook_structure=workbook_structure
            )

        except Exception:

            logger.exception(
                (
                    "Failed loading workbook "
                    "session %s"
                ),
                resource_id
            )

            raise

    def refresh_structure(
        self,
        session: WorkbookSession
    ):

        try:

            logger.info(
                "Refreshing workbook structure"
            )

            workbook = load_workbook_safe(
                session.file_path
            )

            session.workbook_structure = (
                extract_workbook_structure(
                    workbook,
                    session.sheet_header_rows
                )
            )

            return session

        except Exception:

            logger.exception(
                (
                    "Failed refreshing workbook "
                    "structure for session %s"
                ),
                session.resource_id
            )

            raise

    def persist_session(
        self,
        session: WorkbookSession
    ):

        logger.info(
            "Persisting workbook session %s",
            session.resource_id
        )

        try:

            update_resource_metadata(
                session.resource_id,
                {
                    "sheet_header_rows":
                        session.sheet_header_rows,
                    "workbook_name":
                        session.workbook_name,
                    "format_name":
                        session.format_name,
                    "is_multi_sheet":
                        session.is_multi_sheet,
                    "selected_sheets":
                        session.selected_sheets,
                    "linking_rules":
                        session.linking_rules,
                    "canonical_mappings":
                        session.canonical_mappings,
                    "current_step":
                        session.current_step,
                    "canonical_definitions":
                        session.canonical_definitions
                }
            )

        except Exception:

            logger.exception(
                (
                    "Failed persisting workbook "
                    "session %s"
                ),
                session.resource_id
            )

            raise

    def update_sheet_header(
        self,
        resource_id,
        target_sheet,
        header_row
    ):

        logger.info(
            (
                "Updating header row for "
                "sheet %s to row %s"
            ),
            target_sheet,
            header_row
        )

        try:

            session = self.load_session(
                resource_id
            )

            session.set_header_row(
                target_sheet,
                header_row
            )

            self.persist_session(
                session
            )

            self.refresh_structure(
                session
            )

            logger.info(
                (
                    "Updated header row "
                    "successfully for sheet %s"
                ),
                target_sheet
            )

            return session

        except Exception:

            logger.exception(
                (
                    "Failed updating header row "
                    "for sheet %s"
                ),
                target_sheet
            )

            raise

    def update_selected_sheets(
        self,
        resource_id,
        selected_sheets
    ):

        logger.info(
            (
                "Updating selected sheets "
                "for session %s"
            ),
            resource_id
        )

        session = self.load_session(
            resource_id
        )

        session.selected_sheets = (
            selected_sheets
        )

        session.current_step = (
            "linking"
        )

        self.persist_session(
            session
        )

        return session
    
    def update_linking_rules(
        self,
        resource_id,
        linking_rules: dict
    ):

        logger.info(
            (
                "Updating linking rules "
                "for session %s"
            ),
            resource_id
        )

        try:

            session = self.load_session(
                resource_id
            )

            session.linking_rules = (
                linking_rules
            )

            session.current_step = (
                "canonical_mapping"
            )

            self.persist_session(
                session
            )

            return session

        except Exception:

            logger.exception(
                (
                    "Failed updating linking "
                    "rules for session %s"
                ),
                resource_id
            )

            raise

    def generate_canonical_definitions(
        self,
        session: WorkbookSession
    ):

        logger.info(
            (
                "Generating canonical "
                "definitions for session %s"
            ),
            session.resource_id
        )

        canonical_definitions = []

        for sheet_name in (
            session.selected_sheets
        ):

            columns = (
                session.workbook_structure[
                    sheet_name
                ]
            )

            for column in columns:

                if column in session.linking_rules[sheet_name]:
                    linking_key = True
                else:
                    linking_key = False

                safe_sheet = re.sub(r"[^a-zA-Z0-9_-]", "_", sheet_name)
                safe_column = re.sub(r"[^a-zA-Z0-9_-]", "_", column)

                canonical_definitions.append(
                    {
                        "field_id":
                            f"{safe_sheet}::{safe_column}",

                        "sheet_name":
                            sheet_name,

                        "column_name":
                            column,

                        "included": True,

                        "linking_key": linking_key,

                        "canonical_name":
                            column,

                        "column_type":
                            (
                                "identifier"
                                if linking_key
                                else None
                            ),

                        "required":
                            linking_key,

                        "accepted_responses":
                            [],

                        "column_variants":
                            [column],

                        "status":
                            (
                                "configured"
                                if linking_key
                                else "unconfigured"
                            )
                    }
                )

        session.canonical_definitions = (
            canonical_definitions
        )

        self.persist_session(
            session
        )

        return session
    
    def omit_canonical_field(
        self,
        resource_id,
        field_index
    ):

        logger.info(
            (
                "Omitting canonical field "
                "%s for session %s"
            ),
            field_index,
            resource_id
        )

        session = self.load_session(
            resource_id
        )

        session.canonical_definitions[
            field_index
        ]["included"] = False

        self.persist_session(
            session
        )

        return session
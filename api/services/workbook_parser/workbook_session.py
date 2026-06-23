from dataclasses import dataclass, field

from pathlib import Path


@dataclass
class WorkbookSession:
    """
    Session object representing an in-progress
    workbook definition authoring workflow.
    """

    resource_id: str

    file_path: Path

    workbook_name: str | None = None

    format_name: str | None = None

    is_multi_sheet: bool = False

    current_step: str = "upload"

    selected_sheets: list[str] = field(
        default_factory=list
    )

    linking_rules: dict = field(
        default_factory=dict
    )
    canonical_mappings: list[dict] = field(
        default_factory=list
    )

    canonical_definitions: list[dict] = field(
        default_factory=list
    )

    sheet_header_rows: dict = field(
        default_factory=dict
    )

    workbook_structure: dict = field(
        default_factory=dict
    )

    metadata: dict = field(
        default_factory=dict
    )

    workbook_definition: dict = field(
        default_factory=dict
    )

    def set_header_row(
        self,
        sheet_name: str,
        header_row: int
    ):

        self.sheet_header_rows[
            sheet_name
        ] = header_row

    def select_sheet(
        self,
        sheet_name: str
    ):

        if sheet_name not in self.selected_sheets:

            self.selected_sheets.append(
                sheet_name
            )

    def unselect_sheet(
        self,
        sheet_name: str
    ):

        self.selected_sheets = [
            s
            for s in self.selected_sheets
            if s != sheet_name
        ]
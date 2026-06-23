from dataclasses import dataclass, field

from validation_engine.domain.sheet_definition import (
    SheetDefinition
)


@dataclass
class WorkbookFormat:
    """
    Represents one workbook implementation format.
    """

    format_name: str

    is_multi_sheet: bool = False

    sheet_definitions: list[SheetDefinition] = field(
        default_factory=list
    )

    metadata: dict = field(default_factory=dict)

    def get_sheet(
        self,
        sheet_name: str
    ) -> SheetDefinition | None:

        for sheet in self.sheet_definitions:

            if sheet.sheet_name == sheet_name:
                return sheet

        return None

    def to_dict(self):

        return {
            "format_name": self.format_name,
            "is_multi_sheet": self.is_multi_sheet,
            "sheet_definitions": [
                s.to_dict()
                for s in self.sheet_definitions
            ],
            "metadata": self.metadata
        }
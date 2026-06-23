from dataclasses import dataclass, field

from validation_engine.domain.workbook_format import (
    WorkbookFormat
)


@dataclass
class WorkbookDefinition:
    """
    Root aggregate object for workbook schemas.
    """

    workbook_type: str

    formats: list[WorkbookFormat] = field(
        default_factory=list
    )

    description: str | None = None

    metadata: dict = field(default_factory=dict)

    def get_format(
        self,
        format_name: str
    ) -> WorkbookFormat | None:

        for workbook_format in self.formats:

            if workbook_format.format_name == format_name:
                return workbook_format

        return None

    def to_dict(self):

        return {
            "workbook_type": self.workbook_type,
            "formats": [
                f.to_dict()
                for f in self.formats
            ],
            "description": self.description,
            "metadata": self.metadata
        }
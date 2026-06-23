from dataclasses import dataclass, field

from uuid import uuid4

from validation_engine.domain.workbook_format_draft import (
    WorkbookFormatDraft
)


@dataclass
class WorkbookDefinitionDraft:
    """
    Root draft object for workbook definition
    authoring workflows.
    """

    draft_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    workbook_name: str | None = None

    description: str | None = None

    formats: list[WorkbookFormatDraft] = field(
        default_factory=list
    )

    current_step: str = "upload"

    metadata: dict = field(
        default_factory=dict
    )

    def get_format(
        self,
        format_id: str
    ) -> WorkbookFormatDraft | None:

        for workbook_format in self.formats:

            if workbook_format.format_id == format_id:
                return workbook_format

        return None

    def to_dict(self):

        return {
            "draft_id":
                self.draft_id,
            "workbook_name":
                self.workbook_name,
            "description":
                self.description,
            "formats": [
                f.to_dict()
                for f in self.formats
            ],
            "current_step":
                self.current_step,
            "metadata":
                self.metadata
        }

    @classmethod
    def from_dict(
        cls,
        data: dict
    ):

        return cls(
            draft_id=data.get(
                "draft_id"
            ),
            workbook_name=data.get(
                "workbook_name"
            ),
            description=data.get(
                "description"
            ),
            formats=[
                WorkbookFormatDraft.from_dict(f)
                for f in data.get(
                    "formats",
                    []
                )
            ],
            current_step=data.get(
                "current_step",
                "upload"
            ),
            metadata=data.get(
                "metadata",
                {}
            )
        )
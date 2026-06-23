from dataclasses import dataclass, field


@dataclass
class WorkbookFormatDraft:
    """
    Draft representation of a workbook format
    during UI configuration.
    """

    format_id: str

    format_name: str

    is_multi_sheet: bool = False

    uploaded_file_path: str | None = None

    selected_sheets: list[str] = field(
        default_factory=list
    )

    linking_rules: list[dict] = field(
        default_factory=list
    )

    canonical_mappings: list[dict] = field(
        default_factory=list
    )

    metadata: dict = field(
        default_factory=dict
    )

    def to_dict(self):

        return {
            "format_id": self.format_id,
            "format_name": self.format_name,
            "is_multi_sheet":
                self.is_multi_sheet,
            "uploaded_file_path":
                self.uploaded_file_path,
            "selected_sheets":
                self.selected_sheets,
            "linking_rules":
                self.linking_rules,
            "canonical_mappings":
                self.canonical_mappings,
            "metadata":
                self.metadata
        }

    @classmethod
    def from_dict(
        cls,
        data: dict
    ):

        return cls(
            format_id=data.get(
                "format_id"
            ),
            format_name=data.get(
                "format_name"
            ),
            is_multi_sheet=data.get(
                "is_multi_sheet",
                False
            ),
            uploaded_file_path=data.get(
                "uploaded_file_path"
            ),
            selected_sheets=data.get(
                "selected_sheets",
                []
            ),
            linking_rules=data.get(
                "linking_rules",
                []
            ),
            canonical_mappings=data.get(
                "canonical_mappings",
                []
            ),
            metadata=data.get(
                "metadata",
                {}
            )
        )
from dataclasses import dataclass, field

from validation_engine.domain.canonical_column import (
    CanonicalColumn
)

from validation_engine.domain.linking_rule import (
    LinkingRule
)


@dataclass
class SheetDefinition:
    """
    Represents one logical sheet configuration.
    """

    sheet_name: str

    expected_sheet_names: list[str] = field(default_factory=list)

    starting_row: int = 0

    starting_column: int = 0

    columns_used: list[str] | None = None

    canonical_columns: list[CanonicalColumn] = field(
        default_factory=list
    )

    linking_rules: list[LinkingRule] = field(
        default_factory=list
    )

    metadata: dict = field(default_factory=dict)

    def get_column(
        self,
        canonical_name: str
    ) -> CanonicalColumn | None:

        for column in self.canonical_columns:

            if column.canonical_name == canonical_name:
                return column

        return None

    def to_dict(self):

        return {
            "sheet_name": self.sheet_name,
            "expected_sheet_names": self.expected_sheet_names,
            "starting_row": self.starting_row,
            "starting_column": self.starting_column,
            "columns_used": self.columns_used,
            "canonical_columns": [
                c.to_dict()
                for c in self.canonical_columns
            ],
            "metadata": self.metadata
        }
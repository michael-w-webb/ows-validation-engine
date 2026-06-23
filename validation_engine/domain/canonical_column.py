from dataclasses import dataclass, field
from typing import Any


@dataclass
class CanonicalColumn:
    """
    Canonical representation of a workbook column.
    """

    canonical_name: str

    data_type: str

    required: bool = False

    accepted_responses: list[Any] = field(default_factory=list)

    variants: list[str] = field(default_factory=list)

    description: str | None = None

    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:

        return {
            "canonical_name": self.canonical_name,
            "data_type": self.data_type,
            "required": self.required,
            "accepted_responses": self.accepted_responses,
            "variants": self.variants,
            "description": self.description,
            "metadata": self.metadata
        }

    @classmethod
    def from_legacy_definition(
        cls,
        canonical_name: str,
        labels_dict: dict,
        accepted_responses_dict: dict
    ):

        response_config = accepted_responses_dict.get(
            canonical_name,
            {}
        )

        return cls(
            canonical_name=canonical_name,
            data_type=response_config.get("type", "unknown"),
            required=response_config.get("required", False),
            accepted_responses=response_config.get(
                "accepted_responses",
                []
            ),
            variants=labels_dict.get(canonical_name, [])
        )
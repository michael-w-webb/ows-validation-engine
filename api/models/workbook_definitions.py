from pydantic import BaseModel

from typing import List


# ==================================================
# Column Definition
# ==================================================

class ColumnDefinition(BaseModel):
    """
    Declarative schema definition for a workbook column.
    """

    source_column: str

    canonical_name: str

    data_type: str

    required: bool = False

    identity: bool = False

    cross_sheet: bool = False


# ==================================================
# Sheet Definition
# ==================================================

class SheetDefinition(BaseModel):
    """
    Declarative schema definition for a workbook sheet.
    """

    sheet_name: str

    header_row: int

    columns: List[ColumnDefinition]


# ==================================================
# Workbook Definition
# ==================================================

class WorkbookDefinition(BaseModel):
    """
    Top-level workbook schema definition.
    """

    workbook_name: str

    sheets: List[SheetDefinition]
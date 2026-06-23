# validation_engine/column_names.py
from collections.abc import Iterable
from dataclasses import dataclass
import pandas as pd

DELIM = "_|_|_"
NORMALIZED_SUFFIX = "_normalized"


@dataclass(frozen=True)
class ParsedColumn:
    original: str
    base: str
    sheet: str | None
    normalized: bool


def build(
    base: str,
    sheet: str | None = None,
    normalized: bool = False
) -> str:

    col = base

    if normalized:
        col += NORMALIZED_SUFFIX

    if sheet:
        col += f"{DELIM}{sheet}"

    return col

def parse(col: str) -> ParsedColumn:

    original = col

    normalized = False
    sheet = None

    if DELIM in col:
        col, sheet = col.split(DELIM, 1)

    if col.endswith(NORMALIZED_SUFFIX):
        normalized = True
        col = col[:-len(NORMALIZED_SUFFIX)]

    return ParsedColumn(
        original=original,
        base=col,
        sheet=sheet,
        normalized=normalized
    )

def base_name(col: str) -> str:
    return parse(col).base


def sheet_name(col: str) -> str | None:
    return parse(col).sheet


def is_normalized(col: str) -> bool:
    return parse(col).normalized

def remove_sheet_suffix(col: str) -> str:

    parsed = parse(col)

    return build(
        base=parsed.base,
        normalized=parsed.normalized
    )

def remove_normalized_suffix(col: str) -> str:

    parsed = parse(col)

    return build(
        base=parsed.base,
        sheet=parsed.sheet,
        normalized=False
    )

def strip_normalized_suffixes(df):

    rename_map = {
        c: remove_normalized_suffix(c)
        for c in df.columns
    }

    new_cols = list(rename_map.values())

    duplicates = [
        col
        for col in set(new_cols)
        if new_cols.count(col) > 1
    ]

    if duplicates:

        formatted = "\n".join(
            f"    - {col}"
            for col in sorted(duplicates)
        )

        raise ValueError(
            "Removing normalized suffixes would create duplicate "
            "column names.\n\n"
            "Conflicting columns:\n"
            f"{formatted}"
        )

    return df.rename(columns=rename_map)


def add_sheet_suffix(
    df,
    sheet_name,
    omitted_columns=None
):
    """
    Add sheet provenance suffixes to all columns except those
    explicitly omitted.

    Example:

        First Name
            -> First Name_|_|_Participant Database

        First Name_normalized
            -> First Name_normalized_|_|_Participant Database

        id_key
            -> id_key (if omitted)

    Parameters
    ----------
    df : pd.DataFrame
    sheet_name : str
    omitted_columns : set[str] | list[str] | None

    Returns
    -------
    pd.DataFrame
    """

    omitted_columns = set(omitted_columns or {"id_key"})

    rename_map = {}

    for col in df.columns:

        if col in omitted_columns:
            continue

        parsed = parse(col)

        if parsed.sheet is not None:
            raise ValueError(
                f"Column '{col}' already contains sheet provenance."
            )

        rename_map[col] = build(
            base=parsed.base,
            normalized=parsed.normalized,
            sheet=sheet_name
        )

    return df.rename(columns=rename_map)

def find_column(
    columns,
    base=None,
    sheet=None,
    normalized=None
):
    """
    Find exactly one matching column.

    Raises
    ------
    KeyError
        No matching columns found.

    ValueError
        More than one matching column found.
    """

    matches = find_columns(
        columns=columns,
        base=base,
        sheet=sheet,
        normalized=normalized
    )

    if not matches:

        raise KeyError(
            "No columns matched the supplied specification.\n"
            f"base={base!r}, "
            f"sheet={sheet!r}, "
            f"normalized={normalized!r}"
        )

    if len(matches) > 1:

        formatted = "\n".join(
            f"    - {col}"
            for col in matches
        )

        raise ValueError(
            "More than one column matched the supplied specification.\n\n"
            f"base={base!r}, "
            f"sheet={sheet!r}, "
            f"normalized={normalized!r}\n\n"
            "Matching columns:\n"
            f"{formatted}\n\n"
            "Refine your search criteria or use "
            "find_columns() if multiple results are expected."
        )

    return matches[0]

def find_columns(
    columns: Iterable[str],
    base: str | None = None,
    sheet: str | None = None,
    normalized: bool | None = None
) -> list[str]:
    """
    Find all columns matching the supplied criteria.

    Parameters
    ----------
    columns : iterable[str]
        DataFrame columns.

    base : str | None
        Base column name.
        Example:
            "First Name"

    sheet : str | None
        Restrict to a specific sheet.
        Example:
            "Participant Database"

    normalized : bool | None
        True  -> only normalized columns
        False -> only raw columns
        None  -> either

    Returns
    -------
    list[str]
        Matching column names.
    """

    matches = []

    for col in columns:

        parsed = parse(col)

        if base is not None:
            if parsed.base != base:
                continue

        if sheet is not None:
            if parsed.sheet != sheet:
                continue

        if normalized is not None:
            if parsed.normalized != normalized:
                continue

        matches.append(col)

    return matches

def strip_sheet_suffixes(df):

    rename_map = {
        c: remove_sheet_suffix(c)
        for c in df.columns
    }

    return df.rename(columns=rename_map)

def assert_sheet_provenance(df, omitted_columns=None):

    omitted_columns = set(omitted_columns or [])

    bad_cols = []

    for col in df.columns:

        if col in omitted_columns:
            continue

        parsed = parse(col)

        if parsed.sheet is None:
            bad_cols.append(col)

    if bad_cols:

        formatted = "\n".join(
            f"    - {c}"
            for c in bad_cols
        )

        raise ValueError(
            "Columns missing sheet provenance:\n"
            f"{formatted}"
        )

def get_required_column(
    row,
    base,
    normalized=True,
    sheet=None
):
    
    try:
    
        return find_column(
            row.index,
            base=base,
            normalized=normalized,
            sheet=sheet
        )

    except KeyError as e:

            raise KeyError(
                "Required column not found.\n"
                f"base={base!r}, "
                f"sheet={sheet!r}, "
                f"normalized={normalized!r}"
            ) from e

def get_required_value(
    row,
    base,
    normalized=True,
    sheet=None
):
    col = get_required_column(
        row,
        base=base,
        normalized=normalized,
        sheet=sheet
    )

    value = row.get(col)

    if pd.isna(value):

        raise ValueError(
            f"Required value for '{base}' "
            f"(resolved to '{col}') is null."
        )

    return value

def get_value(
    row,
    base,
    normalized=True,
    sheet=None
):
    col = get_required_column(
        row,
        base=base,
        normalized=normalized,
        sheet=sheet
    )

    return row.get(col)
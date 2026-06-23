from validation_engine.column_names import * 

import pytest
import pandas as pd 

def test_parse_normalized_sheet_column():

    parsed = parse(
        "First Name_normalized_|_|_Participant"
    )

    assert parsed.base == "First Name"
    assert parsed.sheet == "Participant"
    assert parsed.normalized is True

def test_parse_raw_sheet_column():

    parsed = parse(
        "First Name_|_|_Participant"
    )

    assert parsed.base == "First Name"
    assert parsed.sheet == "Participant"
    assert parsed.normalized is False

def test_parse_unsuffixed_column():

    parsed = parse("First Name")

    assert parsed.base == "First Name"
    assert parsed.sheet is None
    assert parsed.normalized is False

def test_build_normalized_sheet():

    assert build(
        "First Name",
        sheet="Participant",
        normalized=True
    ) == "First Name_normalized_|_|_Participant"

def test_parse_build_roundtrip():

    original = (
        "First Name_normalized_|_|_Participant"
    )

    parsed = parse(original)

    rebuilt = build(
        parsed.base,
        parsed.sheet,
        parsed.normalized
    )

    assert rebuilt == original

def test_add_sheet_suffix():

    df = pd.DataFrame(
        columns=[
            "id_key",
            "First Name",
            "First Name_normalized"
        ]
    )

    out = add_sheet_suffix(
        df,
        "Participant"
    )

    assert "id_key" in out.columns

    assert (
        "First Name_|_|_Participant"
        in out.columns
    )

    assert (
        "First Name_normalized_|_|_Participant"
        in out.columns
    )

def test_add_sheet_suffix_raises_if_already_suffixed():

    df = pd.DataFrame(
        columns=[
            "id_key",
            "First Name_|_|_Participant"
        ]
    )

    with pytest.raises(ValueError):
        add_sheet_suffix(df, "Participant")

def test_find_column_exact_match():

    cols = [
        "First Name_normalized_|_|_Participant"
    ]

    result = find_column(
        cols,
        base="First Name",
        sheet="Participant",
        normalized=True
    )

    assert result == cols[0]

def test_find_column_raises_on_multiple_matches():

    cols = [
        "First Name_|_|_Participant",
        "First Name_normalized_|_|_Participant"
    ]

    with pytest.raises(ValueError):
        find_column(
            cols,
            base="First Name"
        )

def test_parse_preserves_original():

    original = (
        "First Name_normalized_|_|_Participant"
    )

    parsed = parse(original)

    assert parsed.original == original

def test_find_column_raises_when_missing():

    cols = [
        "First Name_normalized_|_|_Participant"
    ]

    with pytest.raises(KeyError):
        find_column(
            cols,
            base="Last Name"
        )

def test_add_sheet_suffix_respects_omitted_columns():

    df = pd.DataFrame(
        columns=[
            "id_key",
            "meta_id",
            "First Name"
        ]
    )

    out = add_sheet_suffix(
        df,
        "Participant",
        omitted_columns={"id_key", "meta_id"}
    )

    assert "id_key" in out.columns
    assert "meta_id" in out.columns

    assert (
        "First Name_|_|_Participant"
        in out.columns
    )
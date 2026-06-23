# tests/test_key_creator.py

import warnings

import pandas as pd
import pytest

from validation_engine.key_creator import KeyCreator


# --------------------------------------------------
# _resolve_field
# --------------------------------------------------

def test_resolve_field_prefers_normalized():

    row = pd.Series({
        "First Name": "Mike",
        "First Name_normalized": "Michael"
    })

    kc = KeyCreator(
        key_fields=["First Name_normalized"],
        return_unhashed=True
    )

    assert (
        kc._resolve_field(
            row,
            "First Name_normalized"
        )
        == "Michael"
    )


def test_resolve_field_falls_back_to_raw():

    row = pd.Series({
        "First Name": "Mike"
    })

    kc = KeyCreator(
        key_fields=["First Name_normalized"],
        return_unhashed=True
    )

    assert (
        kc._resolve_field(
            row,
            "First Name_normalized"
        )
        == "Mike"
    )


def test_resolve_field_returns_none_when_missing():

    row = pd.Series({})

    kc = KeyCreator(
        key_fields=["First Name_normalized"]
    )

    assert (
        kc._resolve_field(
            row,
            "First Name_normalized"
        )
        is None
    )


def test_resolve_field_prefers_non_null_value():

    row = pd.Series({
        "First Name_normalized_|_|_A": None,
        "First Name_normalized_|_|_B": "Michael"
    })

    kc = KeyCreator(
        key_fields=["First Name_normalized"]
    )

    assert (
        kc._resolve_field(
            row,
            "First Name_normalized"
        )
        == "Michael"
    )


def test_resolve_field_handles_suffixed_columns():

    row = pd.Series({
        "First Name_normalized_|_|_Participant Database":
            "Michael"
    })

    kc = KeyCreator(
        key_fields=["First Name_normalized"]
    )

    assert (
        kc._resolve_field(
            row,
            "First Name_normalized"
        )
        == "Michael"
    )


# --------------------------------------------------
# Warning behavior
# --------------------------------------------------

def test_conflicting_normalized_values_warn():

    row = pd.Series({
        "First Name_normalized_|_|_A": "Michael",
        "First Name_normalized_|_|_B": "Mike"
    })

    kc = KeyCreator(
        key_fields=["First Name_normalized"]
    )

    with pytest.warns(UserWarning):

        kc._resolve_field(
            row,
            "First Name_normalized"
        )


def test_identical_normalized_values_do_not_warn():

    row = pd.Series({
        "First Name_normalized_|_|_A": "Michael",
        "First Name_normalized_|_|_B": "Michael"
    })

    kc = KeyCreator(
        key_fields=["First Name_normalized"]
    )

    with warnings.catch_warnings():

        warnings.simplefilter("error")

        kc._resolve_field(
            row,
            "First Name_normalized"
        )


# --------------------------------------------------
# create_key_from_row
# --------------------------------------------------

def test_required_field_missing_returns_none():

    row = pd.Series({
        "First Name_normalized": "Michael"
    })

    kc = KeyCreator(
        key_fields=[
            "First Name_normalized",
            "Last Name_normalized"
        ],
        required_fields=[
            "First Name_normalized",
            "Last Name_normalized"
        ],
        return_unhashed=True
    )

    assert kc.create_key_from_row(row) is None


def test_create_unhashed_key():

    row = pd.Series({
        "First Name_normalized": "Michael",
        "Last Name_normalized": "Webb"
    })

    kc = KeyCreator(
        key_fields=[
            "First Name_normalized",
            "Last Name_normalized"
        ],
        return_unhashed=True
    )

    assert (
        kc.create_key_from_row(row)
        == "Michael|Webb"
    )


def test_create_hashed_key_is_deterministic():

    row = pd.Series({
        "First Name_normalized": "Michael",
        "Last Name_normalized": "Webb"
    })

    kc = KeyCreator(
        key_fields=[
            "First Name_normalized",
            "Last Name_normalized"
        ]
    )

    key1 = kc.create_key_from_row(row)
    key2 = kc.create_key_from_row(row)

    assert key1 == key2


def test_normalizer_is_applied():

    row = pd.Series({
        "First Name_normalized": "Michael"
    })

    kc = KeyCreator(
        key_fields=["First Name_normalized"],
        normalizers={
            "First Name_normalized": str.lower
        },
        return_unhashed=True
    )

    assert (
        kc.create_key_from_row(row)
        == "michael"
    )


# --------------------------------------------------
# add_key_column
# --------------------------------------------------

def test_add_key_column():

    df = pd.DataFrame({
        "First Name_normalized": ["Michael"],
        "Last Name_normalized": ["Webb"]
    })

    kc = KeyCreator(
        key_fields=[
            "First Name_normalized",
            "Last Name_normalized"
        ],
        return_unhashed=True
    )

    result = kc.add_key_column(df)

    assert "id_key" in result.columns
    assert "id_key_invalid" in result.columns

    assert result.loc[0, "id_key"] == "Michael|Webb"
    assert result.loc[0, "id_key_invalid"] is False
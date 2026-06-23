# test_parser_service.py

import pytest


# ============================================
# Session Creation
# ============================================

def test_create_session(
    simple_session
):

    assert simple_session.resource_id is not None

    assert (
        "Participants"
        in simple_session.workbook_structure
    )

    assert (
        simple_session.workbook_structure[
            "Participants"
        ] == [
            "First Name",
            "Last Name",
            "DOB",
            "Zip Code"
        ]
    )


# ============================================
# Header Row Mutation
# ============================================

def test_update_sheet_header(
    parser_service,
    offset_headers_session
):

    updated_session = (
        parser_service.update_sheet_header(
            resource_id=(
                offset_headers_session
                .resource_id
            ),
            target_sheet="Participants",
            header_row=4
        )
    )

    assert (
        updated_session.sheet_header_rows[
            "Participants"
        ] == 4
    )

    assert (
        updated_session.workbook_structure[
            "Participants"
        ] == [
            "First Name",
            "Last Name",
            "DOB",
            "Zip"
        ]
    )


# ============================================
# Multi-Sheet Session
# ============================================

def test_multi_sheet_session(
    multi_sheet_session
):

    structure = (
        multi_sheet_session
        .workbook_structure
    )

    assert (
        "Participants"
        in structure
    )

    assert (
        "Training"
        in structure
    )

    assert (
        "Employment"
        in structure
    )


# ============================================
# Missing Resource
# ============================================

def test_missing_resource_raises(
    parser_service
):

    with pytest.raises(
        FileNotFoundError
    ):

        parser_service.load_session(
            "fake_resource_id"
        )
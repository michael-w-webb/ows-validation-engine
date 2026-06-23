from pathlib import Path

import pytest

from api.services.workbook_parser.parser_service import (
    ParserService
)


# ============================================
# Fixture Directories
# ============================================

TEST_DIR = Path(__file__).resolve().parent

FIXTURE_DIR = TEST_DIR / "fixtures"


# ============================================
# Workbook File Paths
# ============================================

@pytest.fixture
def simple_workbook_path():

    return (
        FIXTURE_DIR
        / "simple_workbook.xlsx"
    )


@pytest.fixture
def offset_headers_path():

    return (
        FIXTURE_DIR
        / "offset_headers.xlsx"
    )


@pytest.fixture
def blank_sheet_workbook_path():

    return (
        FIXTURE_DIR
        / "blank_sheet_workbook.xlsx"
    )


@pytest.fixture
def multi_sheet_workbook_path():

    return (
        FIXTURE_DIR
        / "multi_sheet_workbook.xlsx"
    )


# ============================================
# Workbook File Contents
# ============================================

@pytest.fixture
def simple_workbook_contents(
    simple_workbook_path
):

    with open(
        simple_workbook_path,
        "rb"
    ) as f:

        return f.read()


@pytest.fixture
def offset_headers_contents(
    offset_headers_path
):

    with open(
        offset_headers_path,
        "rb"
    ) as f:

        return f.read()


@pytest.fixture
def blank_sheet_workbook_contents(
    blank_sheet_workbook_path
):

    with open(
        blank_sheet_workbook_path,
        "rb"
    ) as f:

        return f.read()


@pytest.fixture
def multi_sheet_workbook_contents(
    multi_sheet_workbook_path
):

    with open(
        multi_sheet_workbook_path,
        "rb"
    ) as f:

        return f.read()


# ============================================
# Parser Service
# ============================================

@pytest.fixture
def parser_service():

    return ParserService()


# ============================================
# Prebuilt Sessions
# ============================================

@pytest.fixture
def simple_session(
    parser_service,
    simple_workbook_contents
):

    return parser_service.create_session(
        contents=simple_workbook_contents,
        filename="simple_workbook.xlsx",
        header_row=1
    )


@pytest.fixture
def offset_headers_session(
    parser_service,
    offset_headers_contents
):

    return parser_service.create_session(
        contents=offset_headers_contents,
        filename="offset_headers.xlsx",
        header_row=1
    )


@pytest.fixture
def multi_sheet_session(
    parser_service,
    multi_sheet_workbook_contents
):

    return parser_service.create_session(
        contents=multi_sheet_workbook_contents,
        filename="multi_sheet_workbook.xlsx",
        header_row=1
    )


# ============================================
# Cleanup
# ============================================

@pytest.fixture(autouse=True)
def cleanup_temp_files():

    """
    Placeholder cleanup fixture.

    Eventually this can:
    - remove temp parser files
    - clear test metadata
    - reset temp directories
    - clean SQLite test DBs

    Runs automatically before/after tests.
    """

    yield
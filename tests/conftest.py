# tests/conftest.py

import pytest

from tests.init_test_db import init_db


@pytest.fixture
def test_db(tmp_path):

    db_path = tmp_path / "test_db.db"

    init_db(db_path)

    yield str(db_path)
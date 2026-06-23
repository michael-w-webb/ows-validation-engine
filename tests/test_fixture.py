# tests/test_fixture.py

def test_fixture(test_db):

    assert test_db.endswith(".db")
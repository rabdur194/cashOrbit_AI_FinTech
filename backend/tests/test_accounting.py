from fastapi import HTTPException
import pytest
from app.accounting import post_journal

class DummyDB:
    def add(self, value):
        pass
    def flush(self):
        pass

class DummyUser:
    organization_id = 1
    id = 1

def test_unbalanced_journal_is_rejected():
    with pytest.raises(HTTPException) as exc:
        post_journal(DummyDB(), DummyUser(), "test", 1, "bad entry", [
            {"account_code":"1000", "account_name":"Cash", "debit_minor":1000},
            {"account_code":"4000", "account_name":"Revenue", "credit_minor":900},
        ])
    assert exc.value.status_code == 400
    assert "equal" in exc.value.detail

def test_zero_value_journal_is_rejected():
    with pytest.raises(HTTPException):
        post_journal(DummyDB(), DummyUser(), "test", 1, "zero entry", [
            {"account_code":"1000", "account_name":"Cash", "debit_minor":0},
            {"account_code":"4000", "account_name":"Revenue", "credit_minor":0},
        ])


def test_balanced_journal_is_accepted():
    db = DummyDB()
    entry = post_journal(db, DummyUser(), "test", 2, "balanced entry", [
        {"account_code":"1000", "account_name":"Cash", "debit_minor":1200},
        {"account_code":"4000", "account_name":"Revenue", "credit_minor":1200},
    ])
    assert sum(line.debit_minor for line in entry.lines) == sum(line.credit_minor for line in entry.lines) == 1200

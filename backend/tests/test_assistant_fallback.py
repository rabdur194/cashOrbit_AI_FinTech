from app.routers.assistant import _fallback_answer


def sample_context():
    return {
        "as_of_date": "2026-10-28",
        "invoice_count": 2,
        "totals_by_currency": {
            "BDT": {"invoice_count": 1, "total_invoiced_minor": 100000, "collected_minor": 20000, "outstanding_minor": 80000, "overdue_outstanding_minor": 80000},
            "USD": {"invoice_count": 1, "total_invoiced_minor": 50000, "collected_minor": 0, "outstanding_minor": 50000, "overdue_outstanding_minor": 0},
        },
        "invoices": [
            {"invoice_number": "CO-1", "customer": "Example BD Ltd", "currency": "BDT", "outstanding_minor": 80000, "due_date": "2026-10-20", "is_overdue_today": True},
            {"invoice_number": "CO-2", "customer": "Example US Ltd", "currency": "USD", "outstanding_minor": 50000, "due_date": "2026-11-15", "is_overdue_today": False},
        ],
    }


def test_fallback_summary_keeps_currencies_separate():
    answer = _fallback_answer("Summarize outstanding balances", sample_context())
    assert "BDT 800.00 outstanding" in answer
    assert "USD 500.00 outstanding" in answer
    assert "1300.00 outstanding" not in answer


def test_fallback_prioritizes_overdue_invoice():
    answer = _fallback_answer("Which invoices are overdue?", sample_context())
    assert "CO-1" in answer
    assert "Example BD Ltd" in answer
    assert "BDT 800.00" in answer



from app.db import SessionLocal
from app.services.financial_integration_service import get_current_balance


def test_get_current_balance():
    db = SessionLocal()
    try:
        result = get_current_balance(db)
        assert "total_income" in result
        assert "total_expense" in result
        assert "balance" in result
        assert result["balance"] == (
            result["total_income"] - result["total_expense"]
        )
    finally:
        db.close()

        
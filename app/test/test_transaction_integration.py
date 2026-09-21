
import pytest
from datetime import date
from app.db import SessionLocal
from app.services.transaction_integration_service import (
    save_normalized_transaction,
)

def test_save_normalized_transaction():
    db = SessionLocal()
    try:
        transaction = save_normalized_transaction(
            db=db,
            transaction_type="expense",
            amount="50k",
            category="food",
            date_value="hôm nay",
            merchant="Phở Hà Nội",
            description="ăn phở",
            payment_method="cash",
            period="tháng này",
            reference_date=date(2026, 9, 18),
        )
        assert transaction.id is not None
        assert transaction.amount == 50_000
        assert transaction.category == "food"
        assert transaction.date == "2026-09-18"
        assert transaction.merchant == "Phở Hà Nội"
        assert transaction.description == "ăn phở"
        assert transaction.payment_method == "cash"

    finally:
        db.close()


def test_save_transaction_without_amount():
    db = SessionLocal()
    try:
        with pytest.raises(ValueError, match="Transaction amount is required"):
            save_normalized_transaction(
                db=db,
                transaction_type="expense",
                amount=None,
                category="food",
                description="Ăn phở",
            )

    finally:
        db.close()
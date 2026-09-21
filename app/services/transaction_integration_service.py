
from datetime import date
from sqlalchemy.orm import Session
from app.services.normalization_service import normalize_transaction
from app.services.transaction_service import create_transaction


def save_normalized_transaction(
    db: Session,
    transaction_type: str,
    amount: str | None = None,
    category: str | None = None,
    date_value: str | None = None,
    merchant: str | None = None,
    description: str | None = None,
    payment_method: str | None = None,
    period: str | None = None,
    reference_date: date | None = None,
):
    normalized = normalize_transaction(
        amount=amount,
        category=category,
        date_value=date_value,
        merchant=merchant,
        description=description,
        payment_method=payment_method,
        period=period,
        reference_date=reference_date,
    )

    if normalized["amount"] is None:
        raise ValueError("Transaction amount is required")
    transaction = create_transaction(
        db=db,
        transaction_type=transaction_type,
        amount=normalized["amount"],
        category=normalized["category"],
        date=normalized["date"],
        merchant=normalized["merchant"],
        description=normalized["description"],
        payment_method=normalized["payment_method"],
    )

    return transaction
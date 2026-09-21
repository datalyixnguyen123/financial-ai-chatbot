

from sqlalchemy.orm import Session
from app.services.transaction_service import (
    get_total_income,
    get_total_expense,
)
from app.services.financial_engine import calculate_balance
from app.services.financial_engine import (
    calculate_balance,
    calculate_total_expense,
)

def get_current_balance(db: Session) -> dict:
    total_income = get_total_income(db)
    total_expense = get_total_expense(db)
    balance = calculate_balance(
        total_income=total_income,
        total_expense=total_expense,
    )
    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": balance,
    }


def get_expense_summary(db: Session) -> dict:
    total_expense = get_total_expense(db)
    return {
        "total_expense": total_expense,
    }
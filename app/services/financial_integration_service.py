

from sqlalchemy.orm import Session
from app.services.transaction_service import (get_total_income, get_total_expense, get_monthly_totals,)
from app.services.financial_engine import calculate_balance
from app.services.financial_engine import (calculate_balance, calculate_total_expense,)
from app.models import(Transaction,)
from datetime import date
import re

def get_current_balance(db: Session) -> dict:
    total_income = get_total_income(db)
    total_expense = get_total_expense(db)
    balance = calculate_balance(total_income=total_income, total_expense=total_expense,)
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

def get_expense_by_category(db: Session, category: str) -> dict:
    transactions = (db.query(Transaction).filter(Transaction.transaction_type == "expense", Transaction.category == category,).all())
    total_expense = sum(transaction.amount for transaction in transactions)
    return {
        "category": category,
        "total_expense": total_expense,
    }

def get_monthly_financial_summary(db: Session, month: str | None = None) -> dict:
    if month is None or str(month).strip() == "":
        month = date.today().strftime("%Y-%m")
    month = str(month).strip()
    if not re.fullmatch(r"\d{4}-\d{2}", month):
        month = date.today().strftime("%Y-%m")
    total_income, total_expense = get_monthly_totals(db, month)
    contingency = total_income - total_expense
    return {
        "month": month,
        "total_monthly_income": total_income,
        "total_monthly_expense": total_expense,
        "total_contingency_money": contingency,
    }




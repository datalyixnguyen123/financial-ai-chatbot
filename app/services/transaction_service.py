

from sqlalchemy.orm import Session
from app.models import Transaction
import re
from difflib import SequenceMatcher

def create_transaction(
    db: Session,
    transaction_type: str,
    amount: float,
    category: str | None = None,
    date: str | None = None,
    merchant: str | None = None,
    description: str | None = None,
    payment_method: str | None = None,
    dedupe: bool = True,
) -> Transaction:
    if dedupe:
        existing = find_duplicate_transaction(
            db=db,
            transaction_type=transaction_type,
            amount=amount,
            category=category,
            date=date,
            merchant=merchant,
            description=description,
            payment_method=payment_method,
        )
        if existing is not None:
            return existing

    transaction = Transaction(
        transaction_type=transaction_type,
        amount=amount,
        category=category,
        date=date,
        merchant=merchant,
        description=description,
        payment_method=payment_method,
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

def _normalize_text(value: str | None) -> str:
    if value is None:
        return ""
    text = str(value).strip().lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s]", "", text, flags=re.UNICODE)
    return text.strip()

def _similarity(a: str, b: str) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()

def find_duplicate_transaction(
    db: Session,
    transaction_type: str,
    amount: float,
    category: str | None = None,
    date: str | None = None,
    merchant: str | None = None,
    description: str | None = None,
    payment_method: str | None = None,
) -> Transaction | None:
    filters = [
        Transaction.transaction_type == transaction_type,
        Transaction.amount.between(float(amount) - 0.0001, float(amount) + 0.0001),
    ]

    if category is None:
        filters.append(Transaction.category.is_(None))
    else:
        filters.append(Transaction.category == category)

    if date is None:
        filters.append(Transaction.date.is_(None))
    else:
        filters.append(Transaction.date == date)

    if merchant is None:
        filters.append(Transaction.merchant.is_(None))
    else:
        filters.append(Transaction.merchant == merchant)

    if payment_method is None:
        filters.append(Transaction.payment_method.is_(None))
    else:
        filters.append(Transaction.payment_method == payment_method)

    candidates = (db.query(Transaction).filter(*filters).order_by(Transaction.id.desc()).limit(8).all())
    if not candidates:
        return None

    desc_a = _normalize_text(description)
    for candidate in candidates:
        desc_b = _normalize_text(candidate.description)
        if not desc_a and not desc_b:
            return candidate
        if not desc_a or not desc_b:
            return candidate
        if desc_a == desc_b:
            return candidate
        if desc_a in desc_b or desc_b in desc_a:
            return candidate
        if _similarity(desc_a, desc_b) >= 0.82:
            return candidate
    return None

def get_transaction(db: Session, transaction_id: int,) -> Transaction | None:
    return db.get(Transaction, transaction_id)

def get_transactions(db: Session,) -> list[Transaction]:
    return db.query(Transaction).order_by(Transaction.id.desc()).all()

def update_transaction(
    db: Session,
    transaction_id: int,
    transaction_type: str | None = None,
    amount: float | None = None,
    category: str | None = None,
    date: str | None = None,
    merchant: str | None = None,
    description: str | None = None,
    payment_method: str | None = None,
) -> Transaction | None:
    transaction = db.get(Transaction, transaction_id)

    if transaction is None:
        return None
    if transaction_type is not None:
        transaction.transaction_type = transaction_type
    if amount is not None:
        transaction.amount = amount
    if category is not None:
        transaction.category = category
    if date is not None:
        transaction.date = date
    if merchant is not None:
        transaction.merchant = merchant
    if description is not None:
        transaction.description = description
    if payment_method is not None:
        transaction.payment_method = payment_method
    db.commit()
    db.refresh(transaction)
    return transaction

def delete_transaction(db: Session, transaction_id: int,) -> bool:
    transaction = db.get(Transaction, transaction_id)
    if transaction is None:
        return False
    db.delete(transaction)
    db.commit()

    return True


def get_total_income(db: Session) -> float:
    transactions = (db.query(Transaction).filter(Transaction.transaction_type == "income").all())
    return sum(transaction.amount for transaction in transactions)


def get_total_expense(db: Session) -> float:
    transactions = (db.query(Transaction).filter(Transaction.transaction_type == "expense").all())
    return sum(transaction.amount for transaction in transactions)

def get_monthly_totals(db: Session, month: str) -> tuple[float, float]:
    if not month:
        return 0.0, 0.0
    month = str(month).strip()
    transactions = (
        db.query(Transaction)
        .filter(Transaction.date.like(f"{month}-%"))
        .all()
    )
    total_income = sum(t.amount for t in transactions if t.transaction_type == "income")
    total_expense = sum(t.amount for t in transactions if t.transaction_type == "expense")
    return total_income, total_expense

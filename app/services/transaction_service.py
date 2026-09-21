

from sqlalchemy.orm import Session
from app.models import Transaction


def create_transaction(
    db: Session,
    transaction_type: str,
    amount: float,
    category: str | None = None,
    date: str | None = None,
    merchant: str | None = None,
    description: str | None = None,
    payment_method: str | None = None,
) -> Transaction:
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

def get_transaction(
    db: Session,
    transaction_id: int,
) -> Transaction | None:
    return db.get(Transaction, transaction_id)

def get_transactions(
    db: Session,
) -> list[Transaction]:
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

def delete_transaction(
    db: Session,
    transaction_id: int,
) -> bool:
    transaction = db.get(Transaction, transaction_id)

    if transaction is None:
        return False
    db.delete(transaction)
    db.commit()

    return True


def get_total_income(db: Session) -> float:
    transactions = (
        db.query(Transaction)
        .filter(Transaction.transaction_type == "income")
        .all()
    )
    return sum(transaction.amount for transaction in transactions)


def get_total_expense(db: Session) -> float:
    transactions = (
        db.query(Transaction)
        .filter(Transaction.transaction_type == "expense")
        .all()
    )
    return sum(transaction.amount for transaction in transactions)
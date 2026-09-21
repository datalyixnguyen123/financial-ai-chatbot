
from app.db import SessionLocal
from app.services.transaction_service import (
    create_transaction,
    get_transaction,
    update_transaction,
    delete_transaction,
)


def test_transaction_crud():
    db = SessionLocal()
    try:
        # CREATE
        transaction = create_transaction(
            db=db,
            transaction_type="expense",
            amount=50000,
            category="food",
            date="today",
            merchant="Phở Hà Nội",
            description="Ăn phở",
            payment_method="cash",
        )
        assert transaction.id is not None
        assert transaction.amount == 50000
        assert transaction.category == "food"

        transaction_id = transaction.id

        # READ
        saved_transaction = get_transaction(
            db=db,
            transaction_id=transaction_id,
        )
        assert saved_transaction is not None
        assert saved_transaction.amount == 50000

        # UPDATE
        updated_transaction = update_transaction(
            db=db,
            transaction_id=transaction_id,
            amount=60000,
            category="shopping",
        )
        assert updated_transaction is not None
        assert updated_transaction.amount == 60000
        assert updated_transaction.category == "shopping"

        # READ AFTER UPDATE
        saved_transaction = get_transaction(
            db=db,
            transaction_id=transaction_id,
        )
        assert saved_transaction is not None
        assert saved_transaction.amount == 60000
        assert saved_transaction.category == "shopping"

        # DELETE
        deleted = delete_transaction(
            db=db,
            transaction_id=transaction_id,
        )
        assert deleted is True

        # READ AFTER DELETE
        deleted_transaction = get_transaction(
            db=db,
            transaction_id=transaction_id,
        )
        assert deleted_transaction is None

    finally:
        db.close()
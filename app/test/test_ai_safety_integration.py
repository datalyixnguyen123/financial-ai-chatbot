from fastapi.testclient import TestClient
from sqlalchemy import func

from app.main import app
from app.db import SessionLocal
from app.models import Transaction


client = TestClient(app)


def get_transaction_count():
    db = SessionLocal()
    try:
        return db.query(func.count(Transaction.id)).scalar()
    finally:
        db.close()


def test_clarification_does_not_write_db():
    before_count = get_transaction_count()

    response = client.post(
        "/api/ai/analyze",
        json={
            "message": "Mua đồ hết 200"
        },
    )

    after_count = get_transaction_count()
    data = response.json()

    assert response.status_code == 200
    assert data["intent"] == "add_expense"
    assert data["status"] == "clarification"
    assert data["needs_clarification"] is True
    assert data["financial_result"] is None
    assert data["clarification_question"]
    assert after_count == before_count


def test_unknown_does_not_write_db():
    before_count = get_transaction_count()

    response = client.post(
        "/api/ai/analyze",
        json={
            "message": "asdfghjkl"
        },
    )

    after_count = get_transaction_count()
    data = response.json()

    assert response.status_code == 200
    assert data["intent"] == "unknown"
    assert data["status"] == "unknown"
    assert data["needs_clarification"] is True
    assert data["financial_result"] is None
    assert data["clarification_question"]
    assert after_count == before_count


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

def get_latest_transaction():
    db = SessionLocal()
    try:
        return (db.query(Transaction).order_by(Transaction.id.desc()).first())
    finally:
        db.close()

def test_e2e_accepted_expense_creates_transaction():
    before_count = get_transaction_count()
    response = client.post("/api/ai/analyze", json={"message": "Mua đồ hết 50k"},)
    after_count = get_transaction_count()
    data = response.json()

    assert response.status_code == 200
    assert data["intent"] == "add_expense"
    assert data["status"] == "accepted"
    assert data["needs_clarification"] is False
    assert data["entities"]["amount"] == 50000
    assert after_count == before_count + 1
    transaction = get_latest_transaction()
    assert transaction is not None
    assert transaction.transaction_type == "expense"
    assert transaction.amount == 50000


def test_e2e_accepted_income_creates_transaction():
    before_count = get_transaction_count()
    response = client.post("/api/ai/analyze", json={"message": "Tôi nhận lương 5 triệu"},)
    after_count = get_transaction_count()
    data = response.json()
    assert response.status_code == 200
    assert data["intent"] == "add_income"
    assert data["status"] == "accepted"
    assert data["needs_clarification"] is False
    assert data["entities"]["amount"] == 5000000
    assert after_count == before_count + 1
    transaction = get_latest_transaction()
    assert transaction is not None
    assert transaction.transaction_type == "income"
    assert transaction.amount == 5000000

def test_e2e_ambiguous_amount_requires_clarification():
    before_count = get_transaction_count()
    response = client.post("/api/ai/analyze",
        json={"message": "Mua đồ hết 200"},)
    after_count = get_transaction_count()
    data = response.json()

    assert response.status_code == 200
    assert data["intent"] == "add_expense"
    assert data["status"] == "clarification"
    assert data["needs_clarification"] is True
    assert data["financial_result"] is None
    assert after_count == before_count
    assert "clarification_question" in data
    assert data["clarification_question"]

def test_e2e_missing_required_amount_requires_clarification():
    before_count = get_transaction_count()
    response = client.post(
        "/api/ai/analyze",
        json={"message": "Hôm qua mình đi ăn ở nhà hàng"},
    )
    after_count = get_transaction_count()
    data = response.json()

    assert response.status_code == 200
    assert data["intent"] == "add_expense"
    assert data["status"] == "clarification"
    assert data["needs_clarification"] is True
    assert data["financial_result"] is None
    assert after_count == before_count
    assert data["clarification_question"]

def test_e2e_unknown_does_not_create_transaction():
    before_count = get_transaction_count()
    response = client.post(
        "/api/ai/analyze",
        json={"message": "asdfghjkl"},
    )
    after_count = get_transaction_count()
    data = response.json()

    assert response.status_code == 200
    assert data["intent"] == "unknown"
    assert data["status"] == "unknown"
    assert data["needs_clarification"] is True
    assert data["financial_result"] is None
    assert after_count == before_count
    assert data["clarification_question"]

def test_e2e_query_balance_returns_financial_engine_result():
    response = client.get("/api/financial/balance")
    data = response.json()

    assert response.status_code == 200
    assert "total_income" in data
    assert "total_expense" in data
    assert "balance" in data
    assert data["balance"] == (
        data["total_income"] - data["total_expense"]
    )

def test_e2e_query_expense_balance_endpoint_returns_expense_total():
    response = client.get("/api/financial/balance")
    data = response.json()

    assert response.status_code == 200
    assert "total_expense" in data
    assert data["total_expense"] >= 0
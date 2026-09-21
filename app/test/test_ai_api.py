from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_analyze_valid_expense():
    response = client.post(
        "/api/ai/analyze",
        json={
            "message": "Mua đồ hết 50k"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["intent"] == "add_expense"
    assert 0.0 <= data["confidence"] <= 1.0
    assert data["status"] == "accepted"
    assert data["needs_clarification"] is False
    assert data["entities"]["amount"] == 50000


def test_analyze_empty_message():
    response = client.post(
        "/api/ai/analyze",
        json={
            "message": ""
        },
    )

    assert response.status_code == 400

    data = response.json()

    assert data["error"]["code"] == "INVALID_REQUEST"

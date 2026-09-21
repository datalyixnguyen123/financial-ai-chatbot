

from app.services.validation_service import (validate_ai_output, get_confidence_status,)
from app.services.validation_service import is_ambiguous_amount

def test_valid_ai_output():
    result = validate_ai_output(
        intent="add_expense",
        confidence=0.95,
        amount=50000,
    )
    assert result["valid"] is True
    assert result["status"] == "accepted"


def test_invalid_intent():
    result = validate_ai_output(
        intent="invalid_intent",
        confidence=0.95,
        amount=50000,
    )
    assert result["valid"] is False
    assert "INVALID_INTENT" in result["errors"]


def test_invalid_confidence():
    result = validate_ai_output(
        intent="add_expense",
        confidence=1.5,
        amount=50000,
    )
    assert result["valid"] is False
    assert "INVALID_CONFIDENCE" in result["errors"]


def test_invalid_amount():
    result = validate_ai_output(
        intent="add_expense",
        confidence=0.95,
        amount=-50000,
    )
    assert result["valid"] is False
    assert "INVALID_AMOUNT" in result["errors"]


def test_confidence_thresholds():
    assert get_confidence_status(0.90) == "accepted"
    assert get_confidence_status(0.70) == "clarification"
    assert get_confidence_status(0.50) == "unknown"

def test_ambiguous_amount():
    assert is_ambiguous_amount("200") is True
    assert is_ambiguous_amount("50k") is False
    assert is_ambiguous_amount("50 nghìn") is False
    assert is_ambiguous_amount("2 triệu") is False
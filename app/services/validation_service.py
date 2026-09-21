

ALLOWED_INTENTS = {
    "add_expense",
    "add_income",
    "query_balance",
    "query_expense",
    "query_category",
    "set_budget",
    "saving_goal",
    "financial_advice",
    "unknown",
}

def validate_intent(intent: str) -> bool:
    return intent in ALLOWED_INTENTS

def validate_confidence(confidence: float) -> bool:
    return 0.0 <= confidence <= 1.0

def validate_amount(amount) -> bool:
    if amount is None:
        return True
    try:
        return float(amount) > 0
    except (TypeError, ValueError):
        return False

def validate_ai_output(
    intent: str,
    confidence: float,
    amount=None,
) -> dict:
    errors = []
    if not validate_intent(intent):
        errors.append("INVALID_INTENT")
    if not validate_confidence(confidence):
        errors.append("INVALID_CONFIDENCE")
    if not validate_amount(amount):
        errors.append("INVALID_AMOUNT")
    return {
        "valid": len(errors) == 0,
        "errors": errors,
    }

def get_confidence_status(confidence: float) -> str:
    if confidence >= 0.85:
        return "accepted"
    if confidence >= 0.60:
        return "clarification"
    return "unknown"

def validate_ai_output(
    intent: str,
    confidence: float,
    amount=None,
) -> dict:
    errors = []
    if not validate_intent(intent):
        errors.append("INVALID_INTENT")
    if not validate_confidence(confidence):
        errors.append("INVALID_CONFIDENCE")
    if not validate_amount(amount):
        errors.append("INVALID_AMOUNT")
    if errors:
        return {
            "valid": False,
            "errors": errors,
            "status": "rejected",
        }
    return {
        "valid": True,
        "errors": [],
        "status": get_confidence_status(confidence),
    }

def is_ambiguous_amount(amount) -> bool:
    """
    Phát hiện các amount dạng số đơn giản có thể thiếu đơn vị.
    Ví dụ: 200 có thể là 200 VND hoặc 200.000 VND.
    """
    if amount is None:
        return False
    if isinstance(amount, (int, float)):
        return amount > 0
    if isinstance(amount, str):
        value = amount.strip().lower()
        explicit_units = (
            "k",
            "nghìn",
            "ngàn",
            "triệu",
            "củ",
            "trăm",
        )
        if any(unit in value for unit in explicit_units):
            return False
        # Chỉ gồm số nguyên → có khả năng thiếu đơn vị.
        return value.isdigit()
    return False


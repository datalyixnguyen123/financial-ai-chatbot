
from app.services.decision_service import decide

def run_case(name, **kwargs):
    result = decide(**kwargs)
    print(f"\n[{name}]")
    print(result)
    return result

r1 = run_case(
    "clear expense",
    message="Hôm nay mình ăn trưa hết 80 nghìn",
    intent="add_expense",
    confidence=0.8734315,
    entities={"amount": 80000.0},
    raw_amount="80 nghìn",
)
assert r1["decision"] == "accept"


r2 = run_case(
    "ambiguous amount",
    message="Mua đồ hết 200",
    intent="add_expense",
    confidence=0.894826,
    entities={"amount": 200.0},
    raw_amount="200",
)
assert r2["decision"] == "clarification"
assert r2["reason"] == "ambiguous_amount"


r3 = run_case(
    "clear income medium confidence",
    message="Tháng này mình nhận lương 15 triệu",
    intent="add_income",
    confidence=0.8449294,
    entities={
        "amount": 15000000.0,
        "period": "this_month",
    },
    raw_amount="15 triệu",
)
assert r3["decision"] == "accept"
assert r3["reason"] == "strong_entity_and_context_evidence"


r4 = run_case(
    "balance query",
    message="Số dư hiện tại của mình là bao nhiêu?",
    intent="query_balance",
    confidence=0.7081225,
    entities={},
)
assert r4["decision"] == "accept"


r5 = run_case(
    "unknown",
    message="asdfghjkl",
    intent="unknown",
    confidence=0.2648769,
    entities={},
)
assert r5["decision"] == "unknown"

print("\n[low confidence]")
result = decide(
    message="asdfghjkl",
    intent="add_expense",
    confidence=0.26487696170806885,
    entities={
        "amount": None,
        "category": None,
        "date": None,
        "merchant": None,
        "description": "asdfghjkl",
        "payment_method": None,
        "duration": None,
        "target_amount": None,
        "period": None,
        "budget_limit": None,
    },
    raw_amount=None,
)
print(result)
assert result["decision"] == "unknown"
assert result["reason"] == "low_intent_confidence"

print("\nALL DECISION TESTS PASSED")

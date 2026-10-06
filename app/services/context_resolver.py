

from typing import Any

def resolve_context(
    *,
    persistent: dict[str, Any] | None = None,
    current: dict[str, Any] | None = None,
    conversation: dict[str, Any] | None = None,
    input_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Resolve context using explicit precedence:
    input_context > conversation > current > persistent
    The resolver does not mutate stored context.
    """
    persistent = persistent or {}
    current = current or {}
    conversation = conversation or {}
    input_context = input_context or {}

    resolved: dict[str, Any] = {}
    # Lowest priority
    resolved.update(persistent)
    # Temporary/current context
    resolved.update(current)
    # Recent conversation
    resolved.update(conversation)
    # Explicit current input
    resolved.update(input_context)

    return resolved


def resolve_follow_up(*, previous_turn: dict[str, Any], current_turn: dict[str, Any],) -> dict[str, Any]:

    previous_entities = previous_turn.get("entities") or {}
    current_entities = current_turn.get("entities") or {}
    previous_intent = previous_turn.get("intent")
    message = (current_turn.get("message") or "").strip().lower()
    
    correction_patterns = [
        "không, ý mình là",
        "không ý mình là",
        "à không, ý mình là",
        "không phải, ý mình là",
        "không phải ý mình là",
        "mình nói nhầm",
        "mình nói sai",
        "sửa lại",
        "cho mình sửa",
        "không, mình muốn nói",
        "à không, mình muốn nói",
    ]
    is_correction = any(
        pattern in message
        for pattern in correction_patterns
    )
    if is_correction:
        if previous_intent in {"add_expense", "add_income"}:
            corrected_entities = dict(previous_entities)
            for key, value in current_entities.items():
                if value is not None:
                    corrected_entities[key] = value
            return {
                "resolved": True,
                "intent": previous_intent,
                "entities": corrected_entities,
                "inherited": [
                    key
                    for key, value in previous_entities.items()
                    if value is not None and current_entities.get(key) is None
            ],
                "reason": "transaction_correction",
        }
    
 
    category_keywords = {
        "ăn": "food",
        "ăn uống": "food",
        "đi lại": "transport",
        "giao thông": "transport",
        "học": "education",
        "giáo dục": "education",
        "mua sắm": "shopping",
        "giải trí": "entertainment",
        "sức khỏe": "health",
        "y tế": "health",
        "hóa đơn": "bills",
        "tiền nhà": "rent",
    }

    category = current_entities.get("category")
    previous_period = previous_entities.get("period")
    current_period = current_entities.get("period")

    period_keywords = {
    "tháng này": "this_month",
    "tháng trước": "last_month",
    "tuần này": "this_week",
    "tuần trước": "last_week",
    }

    if current_period is None:
        for keyword, mapped_period in period_keywords.items():
            if keyword in message:
                current_period = mapped_period
                break
    period = current_period or previous_period
    if current_period is not None and previous_entities.get("category") is not None:
        return {
            "resolved": True,
            "intent": "query_category",
            "entities": {
            "category": previous_entities["category"],
            "period": period,
        },
            "inherited": ["category"],
            "reason": "period_follow_up",
    }
    if category is None:
        for keyword, mapped_category in category_keywords.items():
            if keyword in message:
                category = mapped_category
                break

    
    period = current_period or previous_period

    if category is not None and previous_period is not None:
        return {
            "resolved": True,
            "intent": "query_category",
            "entities": {
                "category": category,
                "period": period,
            },
            "inherited": (
                ["period"]
                if current_period is None
                else []
            ),
            "reason": "category_follow_up",
        }
    if current_period is not None and previous_entities.get("category") is not None:
        return {
            "resolved": True,
            "intent": "query_category",
            "entities": {
                "category": previous_entities["category"],
                "period": period,
        },
        "inherited": ["category"],
        "reason": "period_follow_up",
    }
    
    # Insufficient evidence
    return {
        "resolved": False,
        "intent": None,
        "entities": {},
        "inherited": [],
        "reason": "insufficient_follow_up_evidence",
    }

from app.services.context_resolver import resolve_follow_up

previous_turn = {
    "intent": "query_expense",
    "entities": {
        "period": "this_month",
    },
}

current_turn = {
    "intent": "financial_advice",
    "confidence": 0.323,
    "entities": {},
    "message": "Còn tiền ăn thì sao?",
}

result = resolve_follow_up(
    previous_turn=previous_turn,
    current_turn=current_turn,
)

print(result)


previous_turn = {
    "intent": "query_category",
    "entities": {
        "category": "food",
        "period": "this_month",
    },
}

current_turn = {
    "intent": "financial_advice",
    "confidence": 0.323,
    "entities": {},
    "message": "Còn tháng trước?",
}

result = resolve_follow_up(
    previous_turn=previous_turn,
    current_turn=current_turn,
)

print(result)

previous_turn = {
    "intent": "query_category",
    "entities": {
        "category": "food",
        "period": "this_month",
    },
}

current_turn = {
    "intent": "financial_advice",
    "confidence": 0.30,
    "entities": {},
    "message": "Còn đi lại?",
}

result = resolve_follow_up(
    previous_turn=previous_turn,
    current_turn=current_turn,
)

print(result)


previous_turn = {
    "intent": "query_category",
    "entities": {
        "category": "food",
        "period": "this_month",
    },
}

current_turn = {
    "intent": "financial_advice",
    "confidence": 0.30,
    "entities": {},
    "message": "Thế còn khoản đó?",
}

result = resolve_follow_up(
    previous_turn=previous_turn,
    current_turn=current_turn,
)

print(result)

# 5. Current turn có cả category + period
result = resolve_follow_up(
    previous_turn={
        "intent": "query_category",
        "entities": {
            "category": "food",
            "period": "this_month",
        },
    },
    current_turn={
        "intent": "financial_advice",
        "confidence": 0.4,
        "entities": {},
        "message": "Còn đi lại tháng trước?",
    },
)

# 6. Current period phải override previous period
result = resolve_follow_up(
    previous_turn={
        "intent": "query_category",
        "entities": {
            "category": "food",
            "period": "this_month",
        },
    },
    current_turn={
        "intent": "financial_advice",
        "confidence": 0.4,
        "entities": {},
        "message": "Còn tháng trước?",
    },
)

# 7. Câu follow-up không đủ thông tin
result = resolve_follow_up(
    previous_turn={
        "intent": "query_expense",
        "entities": {
            "period": "this_month",
        },
    },
    current_turn={
        "intent": "financial_advice",
        "confidence": 0.3,
        "entities": {},
        "message": "Còn cái đó thì sao?",
    },
)


# 8. Follow-up không liên quan tài chính
result = resolve_follow_up(
    previous_turn={
        "intent": "query_category",
        "entities": {
            "category": "food",
            "period": "this_month",
        },
    },
    current_turn={
        "intent": "unknown",
        "confidence": 0.2,
        "entities": {},
        "message": "Hôm nay thời tiết thế nào?",
    },
)





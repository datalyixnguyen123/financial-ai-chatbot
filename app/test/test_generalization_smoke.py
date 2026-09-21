import requests

API_URL = "http://127.0.0.1:8000/api/ai/analyze"

CASES = [
    {
        "name": "expense_food_new",
        "message": "Sáng nay mình mua bánh mì với ly cà phê, hết 37 nghìn",
        "expected_intent": "add_expense",
    },
    {
        "name": "expense_transport_new",
        "message": "Đi xe công nghệ từ nhà tới công ty mất 52k",
        "expected_intent": "add_expense",
    },
    {
        "name": "expense_shopping_new",
        "message": "Hôm qua mình thanh toán 420 nghìn cho đôi giày",
        "expected_intent": "add_expense",
    },
    {
        "name": "income_salary_new",
        "message": "Công ty vừa chuyển khoản cho mình 18 triệu tiền lương",
        "expected_intent": "add_income",
    },
    {
        "name": "income_bonus_new",
        "message": "Mình vừa nhận 3 triệu tiền thưởng cuối tháng",
        "expected_intent": "add_income",
    },
    {
        "name": "income_transfer_new",
        "message": "Hôm nay tài khoản được cộng thêm 2 triệu",
        "expected_intent": "add_income",
    },
    {
        "name": "balance_new",
        "message": "Giờ trong tài khoản của mình còn lại bao nhiêu?",
        "expected_intent": "query_balance",
    },
    {
        "name": "expense_total_new",
        "message": "Từ đầu tháng tới giờ mình đã chi tổng cộng bao nhiêu?",
        "expected_intent": "query_expense",
    },
    {
        "name": "ambiguous_amount_new",
        "message": "Mình vừa mua đồ hết 300",
        "expected_intent": "add_expense",
        "expected_status": "clarification",
    },
    {
        "name": "missing_amount_new",
        "message": "Hôm qua mình đi ăn ở nhà hàng",
        "expected_intent": "add_expense",
        "expected_status": "clarification",
    },
    {
        "name": "unknown_new",
        "message": "Cho mình biết chuyện này với",
        "expected_intent": "unknown",
    },
    {
        "name": "unknown_nonsense",
        "message": "xyz qwerty 123 abc",
        "expected_intent": "unknown",
    },
]


def run_case(case):
    response = requests.post(
        API_URL,
        json={"message": case["message"]},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def test_generalization_smoke():
    print("\n" + "=" * 70)
    print("M7.3.3 — GENERALIZATION SMOKE TEST")
    print("=" * 70)

    for index, case in enumerate(CASES, start=1):
        result = run_case(case)

        intent_ok = result["intent"] == case["expected_intent"]

        status_ok = True
        if "expected_status" in case:
            status_ok = result["status"] == case["expected_status"]

        ok = intent_ok and status_ok

        print()
        print(f"[{index:02d}] {case['name']}")
        print(f"TEXT     : {case['message']}")
        print(
            f"EXPECTED : intent={case['expected_intent']}"
            + (
                f", status={case['expected_status']}"
                if "expected_status" in case
                else ""
            )
        )
        print(
            f"ACTUAL   : intent={result.get('intent')}, "
            f"confidence={result.get('confidence'):.4f}, "
            f"status={result.get('status')}"
        )
        print(f"ENTITIES : {result.get('entities')}")
        print(f"RESULT   : {'PASS' if ok else 'FAIL'}")

        assert intent_ok, (
            f"{case['name']}: expected intent "
            f"{case['expected_intent']}, got {result.get('intent')}"
        )

        assert status_ok, (
            f"{case['name']}: expected status "
            f"{case['expected_status']}, got {result.get('status')}"
        )

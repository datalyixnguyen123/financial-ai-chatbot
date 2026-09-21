
from app.services.financial_engine import (
    calculate_balance,
    calculate_total_income,
    calculate_total_expense,
    calculate_savings,
    calculate_saving_rate,
    aggregate_expense_by_category,
    find_top_expense_category,
    calculate_budget_usage,
    check_budget,
    calculate_required_monthly_saving,
    calculate_category_percentage,
    analyze_category_budget,
    analyze_saving_goal,
)


def test_balance():
    assert calculate_balance(
        10_000_000,
        7_000_000
    ) == 3_000_000


def test_total_income():
    assert calculate_total_income(
        [10_000_000, 2_000_000]
    ) == 12_000_000


def test_total_expense():
    assert calculate_total_expense(
        [500_000, 1_000_000, 200_000]
    ) == 1_700_000


def test_savings():
    assert calculate_savings(
        10_000_000,
        7_000_000
    ) == 3_000_000


def test_saving_rate():
    assert calculate_saving_rate(
        10_000_000,
        7_000_000
    ) == 30.0


def test_saving_rate_zero_income():
    assert calculate_saving_rate(
        0,
        1_000_000
    ) is None


def test_category_aggregation():
    transactions = [
        {"amount": 50_000, "category": "food"},
        {"amount": 100_000, "category": "food"},
        {"amount": 200_000, "category": "transport"},
    ]
    result = aggregate_expense_by_category(
        transactions
    )
    assert result == {
        "food": 150_000,
        "transport": 200_000
    }


def test_top_category():
    totals = {
        "food": 1_500_000,
        "transport": 500_000,
        "shopping": 2_000_000
    }
    assert find_top_expense_category(
        totals
    ) == "shopping"


def test_budget_usage():
    assert calculate_budget_usage(
        1_500_000,
        2_000_000
    ) == 75.0


def test_budget_within_limit():
    result = check_budget(
        1_500_000,
        2_000_000
    )
    assert result["status"] == "within_budget"
    assert result["remaining"] == 500_000


def test_budget_exceeded():
    result = check_budget(
        2_500_000,
        2_000_000
    )
    assert result["status"] == "exceeded"
    assert result["remaining"] == -500_000


def test_saving_goal():
    assert calculate_required_monthly_saving(
        30_000_000,
        6
    ) == 5_000_000

def test_category_percentage():
    totals = {
        "food": 2_000_000,
        "transport": 1_000_000,
        "shopping": 1_000_000,
    }
    result = calculate_category_percentage(totals)

    assert result["food"] == 50.0
    assert result["transport"] == 25.0
    assert result["shopping"] == 25.0


def test_category_percentage_empty():
    assert calculate_category_percentage({}) == {}


def test_analyze_category_budget():
    result = analyze_category_budget(
        actual_expense=1_500_000,
        budget_limit=2_000_000,
    )
    assert result["usage_percent"] == 75.0
    assert result["remaining"] == 500_000
    assert result["status"] == "within_budget"


def test_analyze_category_budget_exceeded():
    result = analyze_category_budget(
        actual_expense=2_500_000,
        budget_limit=2_000_000,
    )
    assert result["usage_percent"] == 125.0
    assert result["remaining"] == -500_000
    assert result["status"] == "exceeded"


def test_analyze_saving_goal():
    result = analyze_saving_goal(
        target_amount=30_000_000,
        duration_months=6,
        current_savings=10_000_000,
    )
    assert result["monthly_required"] == 5_000_000
    assert result["progress_percent"] == 10000000 / 30000000 * 100

def test_balance_can_be_negative():
    result = calculate_balance(
        total_income=5_000_000,
        total_expense=7_000_000,
    )
    assert result == -2_000_000


def test_empty_category_transactions():
    result = aggregate_expense_by_category([])
    assert result == {}


def test_transaction_without_category_is_skipped():
    transactions = [
        {"amount": 100_000},
        {"category": "food", "amount": 200_000},
    ]

    result = aggregate_expense_by_category(transactions)

    assert result == {
        "food": 200_000,
    }


def test_transaction_without_amount_is_skipped():
    transactions = [
        {"category": "food"},
        {"category": "transport", "amount": 300_000},
    ]

    result = aggregate_expense_by_category(transactions)
    assert result == {
        "transport": 300_000,
    }


def test_zero_budget_is_invalid():
    result = check_budget(
        actual_expense=500_000,
        budget_limit=0,
    )
    assert result["status"] == "invalid"
    assert result["usage_percent"] is None
    assert result["remaining"] is None


def test_zero_duration_saving_goal_is_invalid():
    result = calculate_required_monthly_saving(
        target_amount=30_000_000,
        duration_months=0,
    )
    assert result is None


def test_zero_target_saving_goal():
    result = analyze_saving_goal(
        target_amount=0,
        duration_months=6,
        current_savings=0,
    )
    assert result["monthly_required"] == 0.0
    assert result["progress_percent"] is None


def test_saving_goal_can_exceed_100_percent():
    result = analyze_saving_goal(
        target_amount=10_000_000,
        duration_months=5,
        current_savings=12_000_000,
    )
    assert result["monthly_required"] == 2_000_000
    assert result["progress_percent"] == 120.0


def test_multiple_transactions_same_category():
    transactions = [
        {"category": "food", "amount": 100_000},
        {"category": "food", "amount": 200_000},
        {"category": "transport", "amount": 150_000},
    ]
    result = aggregate_expense_by_category(transactions)
    assert result == {
        "food": 300_000,
        "transport": 150_000,
    }
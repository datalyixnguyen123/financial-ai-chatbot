
from typing import Iterable, Optional

# Batch 1 — Specification + core calculations
def calculate_balance(
    total_income: float,
    total_expense: float
) -> float:
    """
    Balance = Total Income - Total Expense
    """
    return total_income - total_expense


def calculate_total_income(
    amounts: Iterable[float]
) -> float:
    return sum(amounts)


def calculate_total_expense(
    amounts: Iterable[float]
) -> float:
    return sum(amounts)


def calculate_savings(
    total_income: float,
    total_expense: float
) -> float:
    """
    Savings = Income - Expense
    """
    return total_income - total_expense


def calculate_saving_rate(
    total_income: float,
    total_expense: float
) -> Optional[float]:
    """
    Saving Rate = Savings / Income * 100

    Returns None when income is zero.
    """
    if total_income == 0:
        return None

    savings = calculate_savings(
        total_income,
        total_expense
    )

    return savings / total_income * 100

# Batch 2 — Category + Budget + Saving Goal
def aggregate_expense_by_category(
    transactions: Iterable[dict]
) -> dict[str, float]:
    """
    Aggregate expense amount by category.

    Expected transaction:
    {
        "amount": 50000,
        "category": "food"
    }
    """

    result = {}

    for transaction in transactions:
        category = transaction.get("category")
        amount = transaction.get("amount")
        if not category or amount is None:
            continue
        result[category] = (
            result.get(category, 0)
            + float(amount)
        )
    return result


def find_top_expense_category(
    category_totals: dict[str, float]
) -> Optional[str]:
    """
    Return category with highest expense.
    """
    if not category_totals:
        return None

    return max(
        category_totals,
        key=category_totals.get
    )

def calculate_category_percentage(
    category_totals: dict[str, float]
) -> dict[str, float]:
    """
    Calculate each category's percentage of total expenses.
    """
    total_expense = sum(category_totals.values())

    if total_expense <= 0:
        return {}
    return {
        category: amount / total_expense * 100
        for category, amount in category_totals.items()
    }

def analyze_category_budget(
    actual_expense: float,
    budget_limit: float
) -> dict:
    """
    Analyze actual expense against a category budget.
    """
    result = check_budget(actual_expense, budget_limit)
    return {
        "actual_expense": actual_expense,
        "budget_limit": budget_limit,
        "usage_percent": result["usage_percent"],
        "remaining": result["remaining"],
        "status": result["status"],
    }

def analyze_saving_goal(
    target_amount: float,
    duration_months: int,
    current_savings: float = 0
) -> dict:
    """
    Analyze a saving goal.
    """
    monthly_required = calculate_required_monthly_saving(
        target_amount,
        duration_months
    )
    if monthly_required is None:
        return {
            "target_amount": target_amount,
            "duration_months": duration_months,
            "current_savings": current_savings,
            "monthly_required": None,
            "progress_percent": None,
        }

    if target_amount <= 0:
        progress_percent = None
    else:
        progress_percent = current_savings / target_amount * 100

    return {
        "target_amount": target_amount,
        "duration_months": duration_months,
        "current_savings": current_savings,
        "monthly_required": monthly_required,
        "progress_percent": progress_percent,
    }


def calculate_budget_usage(
    actual_expense: float,
    budget_limit: float
) -> Optional[float]:
    """
    Budget Usage = Actual Expense / Budget * 100
    """

    if budget_limit <= 0:
        return None
    return actual_expense / budget_limit * 100


def check_budget(
    actual_expense: float,
    budget_limit: float
) -> dict:
    """
    Compare actual expense against budget.
    """

    if budget_limit <= 0:
        return {
            "status": "invalid",
            "usage_percent": None,
            "remaining": None
        }

    usage = calculate_budget_usage(
        actual_expense,
        budget_limit
    )

    remaining = budget_limit - actual_expense

    if actual_expense > budget_limit:
        status = "exceeded"
    elif actual_expense == budget_limit:
        status = "reached"
    else:
        status = "within_budget"

    return {
        "status": status,
        "usage_percent": usage,
        "remaining": remaining
    }


def calculate_required_monthly_saving(
    target_amount: float,
    duration_months: int
) -> Optional[float]:
    """
    Required monthly saving =
    target amount / duration.
    """

    if duration_months <= 0:
        return None
    if target_amount < 0:
        return None
    return target_amount / duration_months


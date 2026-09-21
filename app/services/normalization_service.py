
import re
from typing import Optional
from datetime import date, timedelta

def normalize_amount(value: Optional[str]) -> Optional[float]:
    """
    Convert Vietnamese natural-language money expressions to VND.
    Examples:
        50k -> 50000
        50 nghìn -> 50000
        1 triệu -> 1000000
        2 củ -> 2000000
        1 triệu rưỡi -> 1500000
        5 chục -> 50000
        năm chục -> 50000
    """
    if value is None:
        return None
    text = str(value).strip().lower()
    if not text:
        return None
    text = text.replace(",", ".")
    if text == "năm chục":
        return 50_000

    # Special case: "rưỡi"
    match = re.fullmatch(
        r"(\d+(?:\.\d+)?)\s*triệu\s*rưỡi",
        text
    )
    if match:
        number = float(match.group(1))
        return number * 1_500_000

    # "1 triệu 500 nghìn"
    match = re.fullmatch(
        r"(\d+(?:\.\d+)?)\s*triệu\s+"
        r"(\d+(?:\.\d+)?)\s*(?:nghìn|ngàn)",
        text
    )
    if match:
        millions = float(match.group(1))
        thousands = float(match.group(2))
        return millions * 1_000_000 + thousands * 1_000

    # "50k"
    match = re.fullmatch(
        r"(\d+(?:\.\d+)?)\s*k",
        text
    )
    if match:
        return float(match.group(1)) * 1_000

    # "50 nghìn" / "50 ngàn"
    match = re.fullmatch(
        r"(\d+(?:\.\d+)?)\s*(?:nghìn|ngàn)",
        text
    )

    if match:
        return float(match.group(1)) * 1_000

    # "50 triệu"
    match = re.fullmatch(
        r"(\d+(?:\.\d+)?)\s*triệu",
        text
    )
    if match:
        return float(match.group(1)) * 1_000_000

    # "2 củ"
    match = re.fullmatch(
        r"(\d+(?:\.\d+)?)\s*củ",
        text
    )
    if match:
        return float(match.group(1)) * 1_000_000

    # "5 chục"
    match = re.fullmatch(
        r"(\d+(?:\.\d+)?)\s*chục",
        text
    )
    if match:
        return float(match.group(1)) * 10_000

    # "50.000"
    if re.fullmatch(r"\d{1,3}(?:\.\d{3})+", text):
        return float(text.replace(".", ""))
    # Plain number
    if re.fullmatch(r"\d+(?:\.\d+)?", text):
        return float(text)
    return None

def normalize_date(
    value: Optional[str],
    reference_date: Optional[date] = None
) -> Optional[str]:
    """
    Normalize Vietnamese date expressions to ISO format: YYYY-MM-DD.
    Examples:
        today / hôm nay / nay -> reference date
        yesterday / hôm qua -> reference date - 1 day
        tomorrow / ngày mai -> reference date + 1 day
        2026-09-18 -> 2026-09-18
        18/09/2026 -> 2026-09-18
        18-09-2026 -> 2026-09-18
    """
    if value is None:
        return None
    text = str(value).strip().lower()
    if not text:
        return None
    if reference_date is None:
        reference_date = date.today()
    if text in {
        "today",
        "hôm nay",
        "hom nay",
        "nay",
    }:
        return reference_date.isoformat()
    if text in {
        "yesterday",
        "hôm qua",
        "hom qua",
    }:
        return (reference_date - timedelta(days=1)).isoformat()
    if text in {
        "tomorrow",
        "ngày mai",
        "ngay mai",
    }:
        return (reference_date + timedelta(days=1)).isoformat()
    # ISO: YYYY-MM-DD
    match = re.fullmatch(
        r"(\d{4})-(\d{1,2})-(\d{1,2})",
        text
    )
    if match:
        year, month, day = map(int, match.groups())
        try:
            return date(year, month, day).isoformat()
        except ValueError:
            return None

    # Vietnamese/common: DD/MM/YYYY or DD-MM-YYYY
    match = re.fullmatch(
        r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})",
        text
    )
    if match:
        day, month, year = map(int, match.groups())
        try:
            return date(year, month, day).isoformat()
        except ValueError:
            return None
    return None


def normalize_period(value: Optional[str]) -> Optional[str]:
    """
    Normalize time-period expressions.
    Examples:
        tháng này -> this_month
        tháng trước -> last_month
        mỗi tháng -> monthly
        hàng tháng -> monthly
        tuần này -> this_week
        tuần trước -> last_week
        7 ngày -> 7_days
        6 tháng -> 6_months
    """
    if value is None:
        return None
    text = str(value).strip().lower()
    if not text:
        return None
    text = re.sub(r"\s+", " ", text)
    mapping = {
        "tháng này": "this_month",
        "thang nay": "this_month",
        "tháng trước": "last_month",
        "thang truoc": "last_month",
        "mỗi tháng": "monthly",
        "moi thang": "monthly",
        "hàng tháng": "monthly",
        "hang thang": "monthly",
        "tuần này": "this_week",
        "tuan nay": "this_week",
        "tuần trước": "last_week",
        "tuan truoc": "last_week",
    }
    if text in mapping:
        return mapping[text]
    # "7 ngày", "30 ngày", ...
    match = re.fullmatch(r"(\d+)\s*ngày", text)
    if match:
        return f"{match.group(1)}_days"
    # "6 tháng", "12 tháng", ...
    match = re.fullmatch(r"(\d+)\s*tháng", text)
    if match:
        return f"{match.group(1)}_months"
    return None

def normalize_transaction(
    amount: Optional[str] = None,
    category: Optional[str] = None,
    date_value: Optional[str] = None,
    merchant: Optional[str] = None,
    description: Optional[str] = None,
    payment_method: Optional[str] = None,
    period: Optional[str] = None,
    reference_date: Optional[date] = None,
) -> dict:
    """
    Convert NLU/NER entity output into normalized transaction data.
    Financial values are normalized deterministically.
    """
    return {
        "amount": normalize_amount(amount),
        "category": category,
        "date": normalize_date(
            date_value,
            reference_date=reference_date
        ),
        "merchant": merchant,
        "description": description,
        "payment_method": payment_method,
        "period": normalize_period(period),
    }

def normalize_ner_entities(
    entities: list,
    description: Optional[str] = None,
    reference_date: Optional[date] = None,
) -> dict:
    """
    Convert raw NER entities into normalized financial fields.
    NER entity format:
        {
            "type": "AMOUNT",
            "text": "650k",
            "start": 18,
            "end": 22
        }
    """
    normalized = {
        "amount": None,
        "category": None,
        "date": None,
        "merchant": None,
        "description": description,
        "payment_method": None,
        "duration": None,
        "target_amount": None,
        "period": None,
        "budget_limit": None,
    }
    if not isinstance(entities, list):
        return normalized
    for entity in entities:
        if not isinstance(entity, dict):
            continue
        entity_type = entity.get("type")
        entity_text = entity.get("text")
        if not entity_type or not entity_text:
            continue
        if entity_type == "AMOUNT":
            if normalized["amount"] is None:
                normalized["amount"] = normalize_amount(entity_text)
        elif entity_type == "MERCHANT":
            if normalized["merchant"] is None:
                normalized["merchant"] = entity_text
        elif entity_type == "PAYMENT_METHOD":
            if normalized["payment_method"] is None:
                normalized["payment_method"] = entity_text
        elif entity_type == "PERIOD":
            if normalized["period"] is None:
                normalized["period"] = normalize_period(entity_text)
        elif entity_type == "BUDGET_LIMIT":
            if normalized["budget_limit"] is None:
                normalized["budget_limit"] = normalize_amount(entity_text)
        elif entity_type == "DURATION":
            if normalized["duration"] is None:
                normalized["duration"] = entity_text
        elif entity_type == "TARGET_AMOUNT":
            if normalized["target_amount"] is None:
                normalized["target_amount"] = normalize_amount(entity_text)
    return normalized


if __name__ == "__main__":
    print("===== M7 NORMALIZATION TEST =====")
    amount_tests = {
        "50k": 50_000,
        "50 nghìn": 50_000,
        "50 ngàn": 50_000,
        "1 triệu": 1_000_000,
        "2 củ": 2_000_000,
        "1 triệu rưỡi": 1_500_000,
        "5 chục": 50_000,
        "năm chục": 50_000,
        "50.000": 50_000,
        "0.05 triệu": 50_000,
    }
    for text, expected in amount_tests.items():
        result = normalize_amount(text)
        assert result == expected, (
            f"Amount failed: {text} "
            f"-> {result}, expected {expected}"
        )
    print("Amount normalization: PASS")

    reference = date(2026, 9, 18)
    date_tests = {
        "hôm nay": "2026-09-18",
        "nay": "2026-09-18",
        "hôm qua": "2026-09-17",
        "ngày mai": "2026-09-19",
        "2026-09-18": "2026-09-18",
        "18/09/2026": "2026-09-18",
        "18-09-2026": "2026-09-18",
    }
    for text, expected in date_tests.items():
        result = normalize_date(
            text,
            reference_date=reference
        )
        assert result == expected, (
            f"Date failed: {text} "
            f"-> {result}, expected {expected}"
        )
    print("Date normalization: PASS")
    period_tests = {
        "tháng này": "this_month",
        "tháng trước": "last_month",
        "mỗi tháng": "monthly",
        "hàng tháng": "monthly",
        "tuần này": "this_week",
        "tuần trước": "last_week",
        "7 ngày": "7_days",
        "6 tháng": "6_months",
    }
    for text, expected in period_tests.items():
        result = normalize_period(text)
        assert result == expected, (
            f"Period failed: {text} "
            f"-> {result}, expected {expected}"
        )
    print("Period normalization: PASS")
    print()
    print("===== M7.2 PASSED =====")

    reference = date(2026, 9, 18)
    transaction = normalize_transaction(
        amount="50k",
        category="food",
        date_value="hôm nay",
        merchant="Phở Hà Nội",
        description="ăn phở",
        payment_method="cash",
        period="tháng này",
        reference_date=reference,
    )
    expected = {
        "amount": 50_000,
        "category": "food",
        "date": "2026-09-18",
        "merchant": "Phở Hà Nội",
        "description": "ăn phở",
        "payment_method": "cash",
        "period": "this_month",
    }
    assert transaction == expected, (
        f"Transaction failed:\n"
        f"Got: {transaction}\n"
        f"Expected: {expected}"
    )
    print("Transaction normalization: PASS")
    print()
    print("===== M7.3 PASSED =====")

    ner_entities = [
        {
            "type": "MERCHANT",
            "text": "AEON",
            "start": 11,
            "end": 15,
        },
        {
            "type": "AMOUNT",
            "text": "650k",
            "start": 21,
            "end": 25,
        },
    ]
    normalized_ner = normalize_ner_entities(
        ner_entities,
        description="Mua đồ tại AEON hết 650k",
    )
    expected_ner = {
        "amount": 650_000,
        "category": None,
        "date": None,
        "merchant": "AEON",
        "description": "Mua đồ tại AEON hết 650k",
        "payment_method": None,
        "duration": None,
        "target_amount": None,
        "period": None,
        "budget_limit": None,
    }
    assert normalized_ner == expected_ner, (
        f"NER normalization failed:\n"
        f"Got: {normalized_ner}\n"
        f"Expected: {expected_ner}"
    )
    print("NER normalization: PASS")

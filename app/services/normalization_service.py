
import re
from typing import Optional


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


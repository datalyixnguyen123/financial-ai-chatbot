
from typing import Any
import re


CONTEXT_SECTIONS = {"profile", "goals", "study", "time", "current",}

def empty_context_updates() -> dict[str, dict[str, Any]]:
    return {
        "profile": {},
        "goals": {},
        "study": {},
        "time": {},
        "current": {},
    }


def build_context_extraction(
    *,
    profile: dict[str, Any] | None = None,
    goals: dict[str, Any] | None = None,
    study: dict[str, Any] | None = None,
    time: dict[str, Any] | None = None,
    current: dict[str, Any] | None = None,
    confidence: float = 0.0,
    reason: str | None = None,
) -> dict[str, Any]:

    updates = empty_context_updates()
    values = {
        "profile": profile,
        "goals": goals,
        "study": study,
        "time": time,
        "current": current,
    }
    for section, data in values.items():
        if data:
            updates[section].update(data)
    detected = any(bool(data) for data in updates.values())
    return {
        "updates": updates,
        "confidence": float(confidence),
        "detected": detected,
        "reason": reason if detected else None,
    }

def extract_context(text: str, *, intent: str | None = None, entities: dict[str, Any] | None = None,) -> dict[str, Any]:
    text = (text or "").strip()
    if not text:
        return build_context_extraction()
    lower = text.lower()

    profile: dict[str, Any] = {}
    for pattern in (
        "sinh viên năm 1",
        "sinh viên năm 2",
        "sinh viên năm 3",
        "sinh viên năm 4",
    ):
        if pattern in lower:
            profile["student_year"] = int(pattern[-1])
            break


    study: dict[str, Any] = {}
    study_keywords = {
        "ielts": "IELTS",
        "toeic": "TOEIC",
        "tiếng anh": "English",
        "hsk": "HSK",
        "jlpt": "JLPT",
        "chứng chỉ": "Certificate",
        "bằng cấp": "Degree",
        "thạc sĩ": "Master",
        "cử nhân": "Bachelor",
        "tiến sĩ": "Doctor"
    }
    for keyword, value in study_keywords.items():
        if keyword in lower and (
            "học" in lower
            or "đang học" in lower
            or "mục tiêu" in lower
        ):
            study["study_goal"] = value
            break


    time_context: dict[str, Any] = {}
    if "tiếng để học" in lower or "giờ để học" in lower:
        match = re.search(
            r"(\d+(?:[.,]\d+)?)\s*(?:tiếng|giờ)",
            lower,
        )
        if match and "tuần" in lower:
            hours = float(match.group(1).replace(",", "."))
            if hours.is_integer():
                hours = int(hours)
            time_context["available_hours_per_week"] = hours


    # FINANCIAL CONTEXT
    profile_financial: dict[str, Any] = {}
    goals: dict[str, Any] = {}
    current_financial: dict[str, Any] = {}

    def parse_vnd_amount(value: str, unit: str | None,) -> float:
        number = float(value.replace(",", ".").replace(" ", ""))
        if unit in ("triệu", "tr", "củ"):
            return number * 1_000_000
        if unit in ("nghìn", "ngàn", "k"):
            return number * 1_000
        return number

    amount_pattern = (r"(\d+(?:[.,]\d+)?)\s*" r"(triệu|tr|nghìn|ngàn|k)?")
    if (
        "ngân sách hàng tháng" in lower
        or "ngân sách mỗi tháng" in lower
        or "budget hàng tháng" in lower
        or "budget mỗi tháng" in lower
    ):
        match = re.search(amount_pattern, lower)
        if match:
            amount = parse_vnd_amount(match.group(1), match.group(2),)
            profile_financial["monthly_budget"] = amount

    if "tháng này" in lower and ("chỉ có" in lower or "có" in lower):
        match = re.search(amount_pattern, lower)
        if match:
            amount = parse_vnd_amount(match.group(1), match.group(2),)
            current_financial["monthly_budget"] = amount
            current_financial["scope"] = "temporary"
            current_financial["period"] = "current_month"

    if ("muốn tiết kiệm" in lower or "muốn dành dụm" in lower or "mục tiêu tiết kiệm" in lower):
        match = re.search(amount_pattern, lower)
        if match:
            amount = parse_vnd_amount(match.group(1), match.group(2),)
            saving_goal: dict[str, Any] = {
                "amount": amount,
            }
            if ("mỗi tháng" in lower or "hàng tháng" in lower):
                saving_goal["period"] = "monthly"
            goals["saving_goal"] = saving_goal


    # Transaction guard
    is_transaction = (
        "tiêu " in lower
        or "tiêu hết" in lower
        or "đã tiêu" in lower
        or "mua " in lower
        or "mua hết" in lower
        or "chi " in lower
        or "tiêu tốn " in lower
        or "tiêu hao " in lower
    )
    if is_transaction:
        profile_financial = {}
        current_financial = {}
        goals = {}
    has_context = any((profile, profile_financial, goals, study, time_context, current_financial,))
    return build_context_extraction(
        profile={**profile, **profile_financial,},
        goals = goals,
        study = study,
        time = time_context,
        current = current_financial,
        confidence = 0.95 if has_context else 0.0,
        reason = ("explicit_user_information" if has_context else None),
    )
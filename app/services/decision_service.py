
from typing import Any, Dict, Optional

ACCEPT_THRESHOLD = 0.85
LOW_CONFIDENCE_THRESHOLD = 0.60


def _is_clear_amount(raw_amount: Optional[str]) -> bool:
    """
    Amount is considered clear when it contains an explicit unit.
    Pure numeric strings such as '200' remain ambiguous.
    """
    if raw_amount is None:
        return False

    text = str(raw_amount).strip().lower()
    if not text:
        return False
    explicit_units = (
        "k",
        "nghìn",
        "ngàn",
        "triệu",
        "củ",
        "trăm",
    )
    if any(unit in text for unit in explicit_units):
        return True
    return False


def _has_required_evidence(
    intent: str,
    entities: Dict[str, Any],
) -> bool:
    """
    Check whether the minimum evidence required by the current
    M7.3.3 decision design is present.
    """
    if intent in {"add_expense", "add_income"}:
        return entities.get("amount") is not None
    if intent in {"query_balance", "query_expense"}:
        return True
    if intent == "query_category":
        return entities.get("category") is not None
    if intent == "set_budget":
        return entities.get("budget_limit") is not None
    if intent == "saving_goal":
        return (
            entities.get("target_amount") is not None
            and entities.get("duration") is not None
        )
    if intent == "financial_advice":
        return True

    return False


def _has_strong_context(
    intent: str,
    message: str,
) -> bool:
    """
    Supporting contextual evidence.
    This does not override a weak/incorrect intent prediction.
    """
    text = message.strip().lower()
    if intent == "add_income":
        keywords = (
            "nhận lương",
            "nhận tiền",
            "được thưởng",
            "thu nhập",
        )
        return any(keyword in text for keyword in keywords)
    if intent == "add_expense":
        keywords = (
            "mua",
            "ăn",
            "chi",
            "trả",
            "thanh toán",
        )
        return any(keyword in text for keyword in keywords)
    if intent == "query_balance":
        keywords = (
            "số dư",
            "còn bao nhiêu",
            "còn lại",
        )
        return any(keyword in text for keyword in keywords)
    if intent == "query_expense":
        keywords = (
            "tiêu bao nhiêu",
            "chi bao nhiêu",
            "tổng chi",
        )
        return any(keyword in text for keyword in keywords)
    return False


def decide(
    *,
    message: str,
    intent: str,
    confidence: float,
    entities: Dict[str, Any],
    raw_amount: Optional[str] = None,
) -> Dict[str, Any]:
    """
    M7.3.3 Evidence-Based Decision Layer V1.
    Returns:
        decision:
            accept | clarification | unknown
        reason:
            machine-readable decision reason
        needs_clarification:
            bool
        clarification_question:
            optional user-facing question
    """
    intent = intent or "unknown"
    confidence = float(confidence or 0.0)
    if intent == "unknown":
        return {
            "decision": "unknown",
            "reason": "unknown_intent",
            "needs_clarification": True,
            "clarification_question": (
                "Mình chưa hiểu rõ yêu cầu của bạn. "
                "Bạn có thể diễn đạt lại giúp mình nhé?"
            ),
        }

    if intent in {"add_expense", "add_income"}:
        if raw_amount is not None and not _is_clear_amount(raw_amount):
            return {
                "decision": "clarification",
                "reason": "ambiguous_amount",
                "needs_clarification": True,
                "clarification_question": (
                    f"Mình chưa rõ số tiền {raw_amount} là đơn vị gì. "
                    "Bạn xác nhận giúp mình là đồng, nghìn hay triệu nhé?"
                ),
            }

    # ------------------------------------------------------------
    # Very low-confidence intent should be treated as unknown.
    if confidence < LOW_CONFIDENCE_THRESHOLD:
        return {
            "decision": "unknown",
            "reason": "low_intent_confidence",
            "needs_clarification": True,
            "clarification_question": (
                "Mình chưa hiểu rõ yêu cầu của bạn. "
                "Bạn có thể diễn đạt lại giúp mình nhé?"
            ),
        }
    # Critical required evidence.
    # ------------------------------------------------------------
    if not _has_required_evidence(intent, entities):
        return {
            "decision": "clarification",
            "reason": "missing_required_evidence",
            "needs_clarification": True,
            "clarification_question": (
                "Mình còn thiếu một vài thông tin để xử lý chính xác. "
                "Bạn bổ sung giúp mình nhé?"
            ),
        }

    # ------------------------------------------------------------
    # High-confidence prediction.
    # ------------------------------------------------------------
    if confidence >= ACCEPT_THRESHOLD:
        return {
            "decision": "accept",
            "reason": "high_confidence",
            "needs_clarification": False,
            "clarification_question": None,
        }

    # ------------------------------------------------------------
    # Medium-confidence prediction:
    # accept when contextual/entity evidence is sufficiently strong.
    # ------------------------------------------------------------
    if confidence >= LOW_CONFIDENCE_THRESHOLD:
        strong_context = _has_strong_context(intent, message)

        if intent in {"add_income", "add_expense"}:
            amount_clear = (
                raw_amount is not None
                and _is_clear_amount(raw_amount)
            )

            if amount_clear and strong_context:
                return {
                    "decision": "accept",
                    "reason": "strong_entity_and_context_evidence",
                    "needs_clarification": False,
                    "clarification_question": None,
                }

        if intent in {
            "query_balance",
            "query_expense",
            "query_category",
            "set_budget",
            "saving_goal",
            "financial_advice",
        }:
            return {
                "decision": "accept",
                "reason": "sufficient_context_and_entity_evidence",
                "needs_clarification": False,
                "clarification_question": None,
            }

        return {
            "decision": "clarification",
            "reason": "insufficient_evidence",
            "needs_clarification": True,
            "clarification_question": (
                "Thông tin mình nhận được chưa đủ rõ để xử lý chính xác. "
                "Bạn xác nhận lại giúp mình nhé?"
            ),
        }

    # ------------------------------------------------------------
    # Low confidence.
    # ------------------------------------------------------------
    return {
        "decision": "unknown",
        "reason": "low_intent_confidence",
        "needs_clarification": True,
        "clarification_question": (
            "Mình chưa đủ chắc chắn về yêu cầu này. "
            "Bạn có thể nói rõ hơn giúp mình nhé?"
        ),
    }


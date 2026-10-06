
from typing import Any


CONVERSATIONAL_TYPES = {
    "greeting",
    "thanks",
    "goodbye",
    "general_chat",
    "correction",
    "clarification",
    "reference",
    "continuation",
    "none",
}


def detect_conversational_context(message: str, previous_message: str | None = None,) -> dict[str, Any]:
    text = (message or "").strip().lower()
    if not text:
        return {
            "conversation_type": "none",
            "financial_relevance": "none",
            "should_route_to_financial_nlu": False,
            "should_route_to_llm": False,
            "should_resolve_context": False,
            "reason": "empty_message",
        }

    # Greeting
    greeting_patterns = [
        "chào bạn",
        "xin chào",
        "hello",
        "hi bạn",
        "hi bạn",
        "hey",
        "hí lô",
        "alo",
        "ê mày"
    ]
    if any(pattern in text for pattern in greeting_patterns):
        return {
            "conversation_type": "greeting",
            "financial_relevance": "none",
            "should_route_to_financial_nlu": False,
            "should_route_to_llm": True,
            "should_resolve_context": False,
            "reason": "greeting_detected",
        }

    # Thanks
    thanks_patterns = [
        "cảm ơn",
        "thanks",
        "thank you",
        "cám ơn",
        "cảm ơn bà nha",
        "đội ơn"
    ]
    if any(pattern in text for pattern in thanks_patterns):
        return {
            "conversation_type": "thanks",
            "financial_relevance": "none",
            "should_route_to_financial_nlu": False,
            "should_route_to_llm": True,
            "should_resolve_context": False,
            "reason": "thanks_detected",
        }

    # Goodbye
    goodbye_patterns = [
        "tạm biệt",
        "bye",
        "hẹn gặp lại",
        "goodbye",
        "chào tạm biệt",
        "bái bai"
    ]
    if any(pattern in text for pattern in goodbye_patterns):
        return {
            "conversation_type": "goodbye",
            "financial_relevance": "none",
            "should_route_to_financial_nlu": False,
            "should_route_to_llm": True,
            "should_resolve_context": False,
            "reason": "goodbye_detected",
        }

    # Correction
    correction_patterns = [
        "không, ý mình là",
        "không phải",
        "ý mình là",
        "mình nói nhầm",
        "mình nói sai",
        "sửa lại",
        "không, mình muốn nói",
        "ý là",
        "hong phải",
        "hong",
        "khum",
        "hok"
    ]
    if any(pattern in text for pattern in correction_patterns):
        return {
            "conversation_type": "correction",
            "financial_relevance": "mixed",
            "should_route_to_financial_nlu": True,
            "should_route_to_llm": False,
            "should_resolve_context": True,
            "reason": "correction_detected",
        }

    # Clarification
    clarification_patterns = [
        "ý là sao",
        "nghĩa là gì",
        "giải thích thêm",
        "giải thích rõ hơn",
        "nói gì vậy",
        "mình chưa hiểu",
        "ý là không hiểu",
        "nói gì không hiểu",
        "là sao bà",
        "nói gì chưa hiểu",
        "ch hiểu"
    ]
    if any(pattern in text for pattern in clarification_patterns):
        return {
            "conversation_type": "clarification",
            "financial_relevance": "mixed",
            "should_route_to_financial_nlu": False,
            "should_route_to_llm": True,
            "should_resolve_context": True,
            "reason": "clarification_detected",
        }

    # Reference / anaphora
    reference_patterns = [
        "cái đó",
        "khoản đó",
        "số tiền đó",
        "việc đó",
        "phần đó",
        "nó thì sao",
        "cái này thì sao",
        "khoản này thì sao",
        "cái đó thì sao"
    ]
    if any(pattern in text for pattern in reference_patterns):
        return {
            "conversation_type": "reference",
            "financial_relevance": "mixed",
            "should_route_to_financial_nlu": True,
            "should_route_to_llm": False,
            "should_resolve_context": True,
            "reason": "reference_detected",
        }

    # Continuation / follow-up
    continuation_patterns = [
        "còn ",
        "thế còn",
        "vậy còn",
        "sau đó",
        "tiếp theo",
        "vậy thì",
        "thế thì",
        "tiếp theo là",
        "nối tiếp",
        "kế tiếp",
        "sau đó là"
    ]
    if any(pattern in text for pattern in continuation_patterns):
        return {
            "conversation_type": "continuation",
            "financial_relevance": "mixed",
            "should_route_to_financial_nlu": True,
            "should_route_to_llm": False,
            "should_resolve_context": True,
            "reason": "continuation_detected",
        }

    # General conversational text
    general_patterns = [
        "mình thấy",
        "mình nghĩ",
        "mình cảm thấy",
        "mình đang",
        "mình hơi",
        "mình khá",
        "mình rất",
        "tui nghĩ",
        "tui thấy là",
        "mình thấy là",
        "mình cảm nhận"
    ]
    if any(pattern in text for pattern in general_patterns):
        return {
            "conversation_type": "general_chat",
            "financial_relevance": "mixed",
            "should_route_to_financial_nlu": True,
            "should_route_to_llm": True,
            "should_resolve_context": False,
            "reason": "general_conversational_statement",
        }

    # Default
    return {
        "conversation_type": "none",
        "financial_relevance": "financial",
        "should_route_to_financial_nlu": True,
        "should_route_to_llm": True,
        "should_resolve_context": False,
        "reason": "no_conversational_pattern_detected",
    }
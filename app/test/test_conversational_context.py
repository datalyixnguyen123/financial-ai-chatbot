
from app.services.conversational_context import (
    detect_conversational_context,
)


def test_greeting():
    result = detect_conversational_context("Chào bạn, bạn là trợ lý tài chính của mình. Hãy giúp đỡ mình nhé!")
    assert result["conversation_type"] == "greeting"
    assert result["financial_relevance"] == "none"
    assert result["should_route_to_financial_nlu"] is False


def test_thanks():
    result = detect_conversational_context("Cảm ơn bạn nhé")
    assert result["conversation_type"] == "thanks"
    assert result["should_route_to_financial_nlu"] is False


def test_correction():
    result = detect_conversational_context("Không, ý mình là 400k")
    assert result["conversation_type"] == "correction"
    assert result["should_resolve_context"] is True


def test_reference():
    result = detect_conversational_context(
        "Còn khoản đó thì sao?"
    )
    assert result["conversation_type"] == "reference"
    assert result["should_resolve_context"] is True


def test_continuation():
    result = detect_conversational_context(
        "Thế còn tháng trước?"
    )
    assert result["conversation_type"] == "continuation"
    assert result["should_resolve_context"] is True


def test_normal_financial_input():
    result = detect_conversational_context(
        "Hôm nay mình ăn trưa hết 80 nghìn"
    )
    assert result["conversation_type"] == "none"
    assert result["financial_relevance"] == "financial"
    assert result["should_route_to_financial_nlu"] is True


def test_natural_statement_with_financial_content():
    result = detect_conversational_context(
        "Mình học dở quá, hiện mình thấy có khóa học giá 800k online"
    )
    assert result["conversation_type"] == "general_chat"
    assert result["should_route_to_financial_nlu"] is True
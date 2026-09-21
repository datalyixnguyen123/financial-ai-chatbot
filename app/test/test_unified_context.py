
from app.services.context_builder import build_context


def test_unified_context():
    conversation_history = [
        {
            "role": "user",
            "content": "Tháng này tôi tiêu khá nhiều.",
        },
        {
            "role": "assistant",
            "content": "Mình có thể xem thử khoản nào đang chi nhiều nhất cho bạn.",
        },
        {
            "role": "user",
            "content": "Ừ, xem giúp mình nhé.",
        },
    ]
    financial_result = {
        "total_income": 5000000,
        "total_expense": 7000000,
        "balance": -2000000,
    }
    retrieved_documents = [
        {
            "topic": "budgeting",
            "title": "Making a Budget",
            "text": (
                "A budget helps track income and expenses "
                "and identify areas that can be adjusted."
            ),
        }
    ]
    context = build_context(
        conversation_history=conversation_history,
        financial_result=financial_result,
        retrieved_documents=retrieved_documents,
    )

    assert "Conversation history:" in context
    assert "Tháng này tôi tiêu khá nhiều." in context
    assert "Ừ, xem giúp mình nhé." in context
    assert "Financial data:" in context
    assert "total_income: 5000000" in context
    assert "total_expense: 7000000" in context
    assert "balance: -2000000" in context
    assert "Financial knowledge:" in context
    assert "Making a Budget" in context
    assert "budgeting" in context

    print("Unified context:")
    print(context)
    print("\nUnified context test passed.")


if __name__ == "__main__":
    test_unified_context()
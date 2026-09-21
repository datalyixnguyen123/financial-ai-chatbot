
from app.services.context_builder import build_context
from app.services.conversation_service import add_message
from app.services.llm_service import generate_response

import os
import pytest
pytestmark = pytest.mark.llm

SYSTEM_INSTRUCTION = """
Bạn là trợ lý tài chính cá nhân của người dùng.
Hãy trả lời bằng tiếng Việt, theo phong cách tự nhiên, gần gũi và giống một cuộc trò chuyện đời thường.

Quy tắc:
1. Xưng hô "mình" và "bạn".
2. Không phán xét tình hình tài chính của người dùng.
3. Financial data là số liệu chính thức từ hệ thống.
4. Không tự thay đổi hoặc bịa số liệu.
5. Không tự tạo giao dịch.
6. Sử dụng conversation history để hiểu các câu hỏi tiếp theo.
7. Không hỏi lại thông tin đã có trong conversation history.
8. Nếu câu hỏi có nhiều cách hiểu và việc đoán có thể ảnh hưởng đến dữ liệu tài chính, hãy hỏi lại.
9. Financial knowledge chỉ được dùng để giải thích kiến thức tài chính.
10. Không nói rằng bạn đã truy cập nguồn bên ngoài nếu không có context.
11. Có thể dùng "nha", "nhé" và emoji một cách tiết chế.
12. Ưu tiên câu trả lời tự nhiên, ngắn gọn và dễ hiểu.

Financial Engine quyết định số liệu. RAG cung cấp kiến thức. Conversation history cung cấp ngữ cảnh.
Bạn chịu trách nhiệm diễn đạt chúng thành câu trả lời tự nhiên.
"""


def test_contextual_chat():
    history = []
    user_message_1 = "Tháng này tôi tiêu hơi nhiều."
    add_message(
        history,
        "user",
        user_message_1,
    )
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
    context_1 = build_context(
        conversation_history=history,
        financial_result=financial_result,
        retrieved_documents=retrieved_documents,
    )
    response_1 = generate_response(
        user_message=user_message_1,
        system_instruction=SYSTEM_INSTRUCTION,
        context=context_1,
    )
    assert response_1
    assert isinstance(response_1, str)
    add_message(
        history,
        "assistant",
        response_1,
    )

    print("=" * 70)
    print("TURN 1")
    print("=" * 70)
    print(f"User: {user_message_1}")
    print(f"AI: {response_1}")

    
    user_message_2 = "Hơi quá tay nhỉ?"
    add_message(
        history,
        "user",
        user_message_2,
    )
    context_2 = build_context(
        conversation_history=history,
        financial_result=financial_result,
        retrieved_documents=retrieved_documents,
    )
    assert "Tháng này tôi tiêu hơi nhiều." in context_2
    assert response_1 in context_2
    assert "Hơi quá tay nhỉ?" in context_2
    assert "balance: -2000000" in context_2
    response_2 = generate_response(
        user_message=user_message_2,
        system_instruction=SYSTEM_INSTRUCTION,
        context=context_2,
    )
    assert response_2
    assert isinstance(response_2, str)
    print("\n" + "=" * 70)
    print("TURN 2")
    print("=" * 70)
    print(f"User: {user_message_2}")
    print(f"AI: {response_2}")
    print("\nContextual chat test passed.")


if __name__ == "__main__":
    test_contextual_chat()
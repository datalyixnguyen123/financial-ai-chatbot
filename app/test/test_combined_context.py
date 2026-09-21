

from app.services.context_builder import build_context
from app.services.llm_service import generate_response
from knowledge.retrieve import retrieve

import os
import pytest
pytestmark = pytest.mark.llm

SYSTEM_INSTRUCTION = """
Bạn là trợ lý tài chính cá nhân. Hãy trả lời bằng tiếng Việt.
Quy tắc:
1. Số liệu trong Financial data là dữ liệu chính thức từ hệ thống.
2. Không tự tính lại hoặc thay đổi các số liệu tài chính.
3. Chỉ sử dụng Financial knowledge được cung cấp khi giải thích kiến thức tài chính.
4. Không tự tạo số liệu hoặc nguồn thông tin.
5. Phân biệt rõ dữ liệu cá nhân và kiến thức tài chính chung.
6. Nếu context không đủ để trả lời, hãy nói rõ.
7. Trả lời ngắn gọn, dễ hiểu.
"""


def test_combined_context():
    user_message = (
        "Tôi đang thâm hụt tài chính, "
        "tôi nên quản lý tiền như thế nào?"
    )
    financial_result = {
        "total_income": 100000,
        "total_expense": 400000,
        "balance": -300000,
    }
    retrieved_documents = retrieve(
        user_message,
        top_k = 3,
    )
    assert retrieved_documents
    context = build_context(
        financial_result=financial_result,
        retrieved_documents=retrieved_documents,
    )
    assert "total_income: 100000" in context
    assert "total_expense: 400000" in context
    assert "balance: -300000" in context
    assert "Financial knowledge:" in context
    response = generate_response(
        user_message=user_message,
        system_instruction=SYSTEM_INSTRUCTION,
        context=context,
    )

    assert response
    assert isinstance(response, str)
    print("Retrieved documents:")
    for document in retrieved_documents:
        print(
            f"- {document.get('topic')} "
            f"| score={document.get('score'):.4f}"
        )
    print("\nCombined context:")
    print(context)
    print("\nGenerated response:")
    print(response)


if __name__ == "__main__":
    test_combined_context()
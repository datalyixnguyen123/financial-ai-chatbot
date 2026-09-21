
from app.services.context_builder import build_context
from app.services.llm_service import generate_response

import os
import pytest
pytestmark = pytest.mark.llm

SYSTEM_INSTRUCTION = """
Bạn là trợ lý tài chính cá nhân. Hãy trả lời bằng tiếng Việt.
Quy tắc:
1. Chỉ sử dụng số liệu trong Financial data được cung cấp.
2. Không tự tính lại hoặc thay đổi số liệu.
3. Không tự tạo số liệu mới.
4. Nếu balance âm, giải thích rõ rằng chi tiêu đang lớn hơn thu nhập.
5. Trả lời ngắn gọn, dễ hiểu.
"""


def test_financial_llm():
    financial_result = {
        "total_income": 100000,
        "total_expense": 400000,
        "balance": -300000,
    }
    user_message = (
        "Tình hình tài chính của tôi hiện tại như thế nào?"
    )
    context = build_context(
        financial_result=financial_result,
    )
    assert "100000" in context
    assert "400000" in context
    assert "-300000" in context
    response = generate_response(user_message=user_message, system_instruction=SYSTEM_INSTRUCTION, context=context,)
    assert response
    assert isinstance(response, str)

    print("Financial context:")
    print(context)
    print("\nGenerated response:")
    print(response)

if __name__ == "__main__":
    test_financial_llm()
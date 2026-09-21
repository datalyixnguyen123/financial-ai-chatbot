
from app.services.llm_service import generate_response

import os
import pytest
pytestmark = pytest.mark.llm

SYSTEM_INSTRUCTION = """
Bạn là trợ lý tài chính cá nhân.

Hãy trả lời bằng tiếng Việt.
Không tự tạo số liệu tài chính.
Nếu context không đủ dữ liệu, hãy nói rõ.
"""

def test_llm_response():
    response = generate_response(
        user_message="Quỹ khẩn cấp là gì?",
        system_instruction=SYSTEM_INSTRUCTION,
        context=(
            "Quỹ khẩn cấp là khoản tiền dành cho "
            "những chi phí bất ngờ hoặc trường hợp khẩn cấp."
        ),
    )
    assert response
    assert isinstance(response, str)
    print("LLM response:")
    print(response)


if __name__ == "__main__":
    test_llm_response()
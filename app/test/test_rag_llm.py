
from app.services.context_builder import build_context
from app.services.llm_service import generate_response
from knowledge.retrieve import retrieve

import os
import pytest
pytestmark = pytest.mark.llm

SYSTEM_INSTRUCTION = """
Bạn là trợ lý tài chính cá nhân. Hãy trả lời bằng tiếng Việt.
Quy tắc:
1. Chỉ sử dụng thông tin trong Financial knowledge được cung cấp.
2. Không tự tạo số liệu hoặc nguồn thông tin.
3. Nếu context không đủ để trả lời, hãy nói rõ.
4. Không nói rằng bạn đã tự truy cập hoặc đọc nguồn bên ngoài.
5. Trả lời ngắn gọn, dễ hiểu.
"""

def test_rag_llm():
    user_message = "Quỹ khẩn cấp là gì?"
    retrieved_documents = retrieve(
        user_message,
        top_k=3,
    )
    assert retrieved_documents
    assert retrieved_documents[0]["topic"] == "emergency_fund"
    context = build_context(
        retrieved_documents=retrieved_documents,
    )
    assert "emergency_fund" in context
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
    print("\nGenerated response:")
    print(response)


if __name__ == "__main__":
    test_rag_llm()
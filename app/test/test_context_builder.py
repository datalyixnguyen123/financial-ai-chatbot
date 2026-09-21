

from app.services.context_builder import build_context

def test_financial_context():
    context = build_context(
        financial_result={
            "total_income": 10000000,
            "total_expense": 7200000,
            "balance": 2800000,
        }
    )
    assert "10000000" in context
    assert "7200000" in context
    assert "2800000" in context
    print("Financial context:")
    print(context)


def test_knowledge_context():
    context = build_context(
        retrieved_documents=[
            {
                "topic": "emergency_fund",
                "title": "Emergency Fund",
                "text": "Emergency savings help cover unexpected expenses.",
            }
        ]
    )
    assert "emergency_fund" in context
    assert "Emergency Fund" in context
    print("\nKnowledge context:")
    print(context)


def test_combined_context():
    context = build_context(
        financial_result={
            "balance": 2800000,
        },
        retrieved_documents=[
            {
                "topic": "saving",
                "title": "Saving",
                "text": "Saving regularly can help achieve financial goals.",
            }
        ],
    )
    assert "2800000" in context
    assert "saving" in context
    print("\nCombined context:")
    print(context)


if __name__ == "__main__":
    test_financial_context()
    test_knowledge_context()
    test_combined_context()
    print("\nAll context builder tests passed.")
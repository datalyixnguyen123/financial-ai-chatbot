
from retrieve import retrieve

TEST_CASES = [
    {
        "query": "Làm thế nào để lập ngân sách cá nhân?",
        "expected_topic": "budgeting",
    },
    {
        "query": "Quỹ khẩn cấp dùng để làm gì?",
        "expected_topic": "emergency_fund",
    },
    {
        "query": "Làm sao để tiết kiệm tiền hiệu quả?",
        "expected_topic": "saving",
    },
    {
        "query": "Làm thế nào để giảm nợ?",
        "expected_topic": "debt_management",
    },
    {
        "query": "Quy tắc 50/30/20 là gì?",
        "expected_topic": "50_30_20",
    },
]


def main():
    correct = 0
    for case in TEST_CASES:
        results = retrieve(
            case["query"],
            top_k=1,
        )
        top_result = results[0]
        predicted_topic = top_result["topic"]
        is_correct = (
            predicted_topic == case["expected_topic"]
        )

        if is_correct:
            correct += 1
        print(
            f"\nQuery: {case['query']}"
        )
        print(
            f"Expected: {case['expected_topic']}"
        )
        print(
            f"Predicted: {predicted_topic}"
        )
        print(
            f"Score: {top_result['score']:.4f}"
        )
        print(
            f"PASS: {is_correct}"
        )

    accuracy = correct / len(TEST_CASES)
    print("\n====================")
    print(f"Top-1 Accuracy: {accuracy:.4f}")
    print(
        f"Correct: {correct}/{len(TEST_CASES)}"
    )

if __name__ == "__main__":
    main()
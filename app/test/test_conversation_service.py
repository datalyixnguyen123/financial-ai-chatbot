
from app.services.conversation_service import (
    add_message,
    build_conversation_context,
    get_recent_history,
)

def test_add_message():
    history = []
    add_message(
        history,
        "user",
        "Tôi vừa mua đôi giày 800k",
    )
    add_message(
        history,
        "assistant",
        "Mình ghi nhận 800k cho khoản mua sắm nha.",
    )
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"


def test_recent_history():
    history = []
    for index in range(5):
        add_message(
            history,
            "user",
            f"Message {index}",
        )
    recent = get_recent_history(
        history,
        max_messages=3,
    )
    assert len(recent) == 3
    assert recent[0]["content"] == "Message 2"
    assert recent[-1]["content"] == "Message 4"


def test_build_conversation_context():
    history = [
        {
            "role": "user",
            "content": "Tôi vừa mua đôi giày 800k",
        },
        {
            "role": "assistant",
            "content": "Mình ghi nhận 800k cho khoản mua sắm nha.",
        },
        {
            "role": "user",
            "content": "Hơi quá tay nhỉ?",
        },
    ]
    context = build_conversation_context(history)
    assert "Conversation history:" in context
    assert "User: Tôi vừa mua đôi giày 800k" in context
    assert (
        "Assistant: Mình ghi nhận 800k cho khoản mua sắm nha."
        in context
    )
    assert "User: Hơi quá tay nhỉ?" in context


def test_empty_history():
    context = build_conversation_context([])
    assert context == ""


def test_invalid_role():
    history = []
    try:
        add_message(
            history,
            "system",
            "Invalid message",
        )
        assert False
    except ValueError:
        assert True


def test_empty_message():
    history = []
    try:
        add_message(
            history,
            "user",
            "   ",
        )
        assert False
    except ValueError:
        assert True

if __name__ == "__main__":
    test_add_message()
    test_recent_history()
    test_build_conversation_context()
    test_empty_history()
    test_invalid_role()
    test_empty_message()
    print("All conversation service tests passed.")
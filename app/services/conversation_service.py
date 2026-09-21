
from typing import Any


def add_message(
    history: list[dict[str, str]],
    role: str,
    content: str,
) -> list[dict[str, str]]:
    """
    Add one message to conversation history.
    role should normally be:
    - user
    - assistant
    """
    if role not in {"user", "assistant"}:
        raise ValueError("Invalid conversation role")
    if not content or not content.strip():
        raise ValueError("Message content cannot be empty")
    history.append(
        {
            "role": role,
            "content": content.strip(),
        }
    )
    return history


def get_recent_history(
    history: list[dict[str, str]],
    max_messages: int = 10,
) -> list[dict[str, str]]:
    """
    Return the most recent conversation messages.
    """
    if max_messages <= 0:
        return []
    return history[-max_messages:]


def build_conversation_context(
    history: list[dict[str, str]],
    max_messages: int = 10,
) -> str:
    """
    Convert conversation history into text context for the LLM.
    """
    recent_history = get_recent_history(
        history,
        max_messages=max_messages,
    )
    if not recent_history:
        return ""
    lines = ["Conversation history:"]

    for message in recent_history:
        role = message["role"]
        content = message["content"]
        if role == "user":
            speaker = "User"
        else:
            speaker = "Assistant"
        lines.append(
            f"{speaker}: {content}"
        )
    return "\n".join(lines)
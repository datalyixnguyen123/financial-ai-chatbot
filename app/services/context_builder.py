
def build_financial_context(financial_result: dict | None = None,) -> str:
    if not financial_result:
        return ""
    lines = [
        "Financial data:",
    ]
    for key, value in financial_result.items():
        if value is not None:
            lines.append(f"- {key}: {value}")
    return "\n".join(lines)


def build_knowledge_context(retrieved_documents: list[dict] | None = None,) -> str:
    if not retrieved_documents:
        return ""
    sections = [
        "Financial knowledge:",
    ]
    for index, document in enumerate(
        retrieved_documents,
        start=1,
    ):
        topic = document.get("topic")
        title = document.get("title")
        text = document.get("text")
        sections.append(f"\n[{index}]")
        if topic:
            sections.append(f"Topic: {topic}")
        if title:
            sections.append(f"Title: {title}")
        if text:
            sections.append(f"Content: {text}")

    return "\n".join(sections)


def build_conversation_context(conversation_history: list[dict[str, str]] | None = None,) -> str:
    if not conversation_history:
        return ""
    lines = ["Conversation history:", ]
    for message in conversation_history:
        role = message.get("role")
        content = message.get("content")
        if not content:
            continue
        if role == "user":
            speaker = "User"
        elif role == "assistant":
            speaker = "Assistant"
        else:
            continue
        lines.append(f"{speaker}: {content}")
    if len(lines) == 1:
        return ""
    return "\n".join(lines)


def build_context(
    financial_result: dict | None = None,
    retrieved_documents: list[dict] | None = None,
    conversation_history: list[dict[str, str]] | None = None,
) -> str:
    parts = []
    conversation_context = build_conversation_context(
        conversation_history
    )
    if conversation_context:
        parts.append(conversation_context)
    financial_context = build_financial_context(
        financial_result
    )
    if financial_context:
        parts.append(financial_context)
    knowledge_context = build_knowledge_context(
        retrieved_documents
    )
    if knowledge_context:
        parts.append(knowledge_context)
    return "\n\n".join(parts)
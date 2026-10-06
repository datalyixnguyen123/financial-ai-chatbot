
import os
import requests
from dotenv import load_dotenv

load_dotenv()

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11435",)
OLLAMA_MODEL = os.getenv("LLM_MODEL", "qwen2.5:3b",)


def generate_response(user_message: str, system_instruction: str, context: str | None = None,) -> str:
    prompt_parts = [f"User message:\n{user_message}"]
    if context:
        prompt_parts.append(f"Context:\n{context}")
    user_input = "\n\n".join(prompt_parts)
    payload = {
        "model": OLLAMA_MODEL,
        "system": system_instruction,
        "prompt": user_input,
        "stream": False,
    }
    response = requests.post(f"{OLLAMA_HOST}/api/generate", json = payload, timeout = 120,)
    response.raise_for_status()
    result = response.json()
    return result.get("response", "").strip()

def generate_chat_response(
    user_message: str,
    system_instruction: str,
    conversation_history: list[dict] | None = None,
    context: str | None = None,
) -> str:
    messages = [
        {"role": "system", "content": system_instruction},
    ]
    
    # Add conversation history
    if conversation_history:
        recent_history = conversation_history[-10:]
        for msg in recent_history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content,})

    # Build the current user message with optional context
    current_content = user_message
    if context:
        current_content = (
            f"{user_message}\n\n"
            f"[Context]\n{context}"
        )
    messages.append({"role": "user", "content": current_content,})

    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
    }
    response = requests.post(f"{OLLAMA_HOST}/api/chat", json = payload, timeout = 120,)
    response.raise_for_status()
    result = response.json()
    return result.get("message", {}).get("content", "").strip()

def generate_chat_response_stream(
    user_message: str,
    system_instruction: str,
    conversation_history: list[dict] | None = None,
    context: str | None = None,
):
    import json
    messages = [{"role": "system", "content": system_instruction},]
    if conversation_history:
        recent_history = conversation_history[-10:]
        for msg in recent_history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content,})

    current_content = user_message
    if context:
        current_content = (
            f"{user_message}\n\n"
            f"[Context]\n{context}"
        )
    messages.append({"role": "user", "content": current_content,})
    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": True,
    }
    try:
        response = requests.post(f"{OLLAMA_HOST}/api/chat", json = payload, timeout = 120, stream = True,)
        response.raise_for_status()
        for line in response.iter_lines():
            if line:
                chunk = json.loads(line)
                yield chunk.get("message", {}).get("content", "")
    except Exception as e:
        print(f"[OLLAMA STREAM ERROR] {e}", flush=True)
        yield "..."
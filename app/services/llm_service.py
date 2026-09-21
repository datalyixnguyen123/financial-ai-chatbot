
import os
from openai import OpenAI

MODEL_NAME = os.getenv("LLM_MODEL", "gpt-5.6-luna")

def generate_response(
    user_message: str,
    system_instruction: str,
    context: str | None = None,
) -> str:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")
    client = OpenAI(api_key=api_key)
    prompt_parts = [
        f"User message:\n{user_message}",
    ]
    if context:
        prompt_parts.append(
            f"Context:\n{context}"
        )
    user_input = "\n\n".join(prompt_parts)
    response = client.responses.create(
        model=MODEL_NAME,
        instructions=system_instruction,
        input=user_input,
    )
    return response.output_text
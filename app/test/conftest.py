import os
import pytest


def pytest_collection_modifyitems(config, items):
    has_openai_key = bool(os.getenv("OPENAI_API_KEY"))

    if has_openai_key:
        return

    skip_llm = pytest.mark.skip(
        reason="OPENAI_API_KEY is not configured"
    )

    for item in items:
        if "llm" in item.keywords:
            item.add_marker(skip_llm)

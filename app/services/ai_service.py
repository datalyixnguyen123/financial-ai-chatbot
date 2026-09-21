
import os
import requests
from app.services.normalization_service import normalize_ner_entities

INFERENCE_API_URL = os.getenv(
    "INFERENCE_API_URL",
    ""
)

ENTITY_FIELDS = [
    "amount",
    "category",
    "date",
    "merchant",
    "description",
    "payment_method",
    "duration",
    "target_amount",
    "period",
    "budget_limit",
]

NER_TO_ENTITY_FIELD = {
    "AMOUNT": "amount",
    "MERCHANT": "merchant",
    "PAYMENT_METHOD": "payment_method",
    "DURATION": "duration",
    "TARGET_AMOUNT": "target_amount",
    "PERIOD": "period",
    "BUDGET_LIMIT": "budget_limit",
}

def _build_entities(message: str, result: dict) -> dict:
    entities = {
        field: None
        for field in ENTITY_FIELDS
    }
    entities["description"] = message
    ner_entities = result.get("entities", [])
    if not isinstance(ner_entities, list):
        return entities
    for entity in ner_entities:
        if not isinstance(entity, dict):
            continue
        entity_type = entity.get("type")
        entity_text = entity.get("text")
        field = NER_TO_ENTITY_FIELD.get(entity_type)
        if field is None:
            continue
        if entity_text is None:
            continue
        if entities[field] is None:
            entities[field] = entity_text
    return entities


def analyze_message(message: str) -> dict:
    if not INFERENCE_API_URL:
        raise RuntimeError(
            "INFERENCE_API_URL is not configured"
        )
    response = requests.post(
        f"{INFERENCE_API_URL}/predict",
        json={
            "text": message
        },
        timeout=30,
    )
    response.raise_for_status()
    result = response.json()
    raw_entities = result.get("entities", [])
    normalized_entities = normalize_ner_entities(
    raw_entities,
    description=message,
    )

    return {
    "intent": result.get(
        "intent",
        "unknown"
    ),
    "confidence": result.get(
        "confidence",
        0.0
    ),
    "entities": normalized_entities,
    "raw_entities": raw_entities,
}

def extract_entities(message: str) -> list:
    if not INFERENCE_API_URL:
        raise RuntimeError(
            "INFERENCE_API_URL is not configured"
        )
    response = requests.post(
        f"{INFERENCE_API_URL}/predict",
        json={
            "text": message
        },
        timeout=30,
    )
    response.raise_for_status()
    result = response.json()
    entities = result.get("entities", [])
    if not isinstance(entities, list):
        raise ValueError(
            "Invalid entity response from inference API"
        )
    return entities

def extract_and_normalize_entities(message: str) -> dict:
    raw_entities = extract_entities(message)
    return normalize_ner_entities(
        raw_entities,
        description=message,
    )




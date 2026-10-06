
import json
import re
import pandas as pd


INPUT_FILE = "data/processed/entity_dataset_clean.csv"
OUTPUT_FILE = "data/processed/entity_bio_dataset.csv"

SPAN_ENTITY_TYPES = [
    "amount",
    "merchant",
    "payment_method",
    "duration",
    "target_amount",
    "period",
    "budget_limit",
]
BIO_ENTITY_TYPES = SPAN_ENTITY_TYPES

def normalize_text(text):
    """
    Chuẩn hóa nhẹ để tìm entity.
    Không thay đổi text gốc dùng cho output.
    """
    return str(text).strip().lower()


def find_entity_span(text, entity_value):
    """
    Tìm vị trí entity trong text.

    Trả về:
        (start, end)

    Nếu không tìm thấy:
        None
    """

    if entity_value is None:
        return None
    value = str(entity_value).strip()
    if not value:
        return None
    text_lower = normalize_text(text)
    value_lower = value.lower()

    # finding exact substring
    start = text_lower.find(value_lower)
    if start == -1:
        return None
    end = start + len(value)
    return start, end


def char_to_bio(text, spans):
    """
    Convert character spans -> BIO labels.

    spans:
        [
            (start, end, entity_type),
            ...
        ]
    """

    labels = ["O"] * len(text)

    for start, end, entity_type in spans:
        if start < 0 or end > len(text) or start >= end:
            raise ValueError(f"Invalid span: {(start, end, entity_type)}")
        for i in range(start, end):
            if labels[i] != "O":
                raise ValueError(
                    f"Overlapping entities at position {i}: "
                    f"{text[i]}"
                )
            if i == start:
                labels[i] = f"B-{entity_type.upper()}"
            else:
                labels[i] = f"I-{entity_type.upper()}"
    return labels


df = pd.read_csv(INPUT_FILE)
print("===== M6.3.2 BUILD BIO DATASET =====")
print("Input rows:", len(df))


records = []
total_entities = 0
converted_entities = 0
skipped_entities = 0
skip_examples = []

for _, row in df.iterrows():
    text = str(row["text"])
    entities = json.loads(row["entities"])
    spans = []
    for entity_type in SPAN_ENTITY_TYPES:
        value = entities.get(entity_type)
        if value is None:
            continue
        total_entities += 1
        span = find_entity_span(text, value)
        if span is None:
            skipped_entities += 1
            if len(skip_examples) < 30:
                skip_examples.append(
                    {
                        "id": int(row["id"]),
                        "text": text,
                        "entity_type": entity_type,
                        "value": value,
                    }
                )
            continue
        start, end = span
        spans.append((start, end, entity_type))
        converted_entities += 1

    spans.sort(key=lambda x: (x[0], x[1]))
    labels = char_to_bio(text, spans)
    records.append(
        {
            "id": int(row["id"]),
            "text": text,
            "labels": json.dumps(
                labels,
                ensure_ascii=False
            ),
        }
    )


bio_df = pd.DataFrame(records)
bio_df.to_csv(OUTPUT_FILE, index = False)


print("\n===== RESULT =====")
print("Rows:", len(bio_df))
print("Total span entities:", total_entities)
print("Converted entities:", converted_entities)
print("Skipped entities:", skipped_entities)

print("\n===== SKIPPED EXAMPLES =====")
for item in skip_examples:
    print(item)

if len(bio_df) != 800:
    raise ValueError(f"Expected 800 rows, got {len(bio_df)}")

for _, row in bio_df.iterrows():
    labels = json.loads(row["labels"])
    if len(labels) != len(row["text"]):
        raise ValueError(f"Label length mismatch at ID {row['id']}")

print("\nSaved:", OUTPUT_FILE)
print("===== M6.3.2 PASSED =====")
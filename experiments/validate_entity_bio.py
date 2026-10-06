
import pandas as pd
import json
from collections import Counter

FILE = "data/processed/entity_bio_dataset.csv"

df = pd.read_csv(FILE)

print("===== M6.3.3 BIO VALIDATION =====")
print("Rows:", len(df))

allowed_prefixes = {
    "O",
    "B-AMOUNT",
    "I-AMOUNT",
    "B-MERCHANT",
    "I-MERCHANT",
    "B-PAYMENT_METHOD",
    "I-PAYMENT_METHOD",
    "B-DURATION",
    "I-DURATION",
    "B-TARGET_AMOUNT",
    "I-TARGET_AMOUNT",
    "B-PERIOD",
    "I-PERIOD",
    "B-BUDGET_LIMIT",
    "I-BUDGET_LIMIT",
}

errors = []
label_counter = Counter()

for _, row in df.iterrows():

    sample_id = int(row["id"])
    text = str(row["text"])
    labels = json.loads(row["labels"])

    # 1. Character/label length
    if len(text) != len(labels):
        errors.append(
            f"ID {sample_id}: "
            f"text length={len(text)}, "
            f"labels length={len(labels)}"
        )
        continue

    # 2. Label vocabulary
    for label in labels:
        label_counter[label] += 1
        if label not in allowed_prefixes:
            errors.append(
                f"ID {sample_id}: invalid label {label}"
            )

    # 3. BIO transition validation
    previous = "O"
    for label in labels:
        if label.startswith("I-"):
            current_type = label[2:]
            if previous == "O":
                errors.append(
                    f"ID {sample_id}: "
                    f"I- label follows O: {label}"
                )
            elif not previous.endswith(current_type):
                errors.append(
                    f"ID {sample_id}: "
                    f"invalid transition "
                    f"{previous} -> {label}"
                )
        previous = label


print("\n===== LABEL DISTRIBUTION =====")

for label, count in sorted(label_counter.items()):
    print(f"{label}: {count}")


print("\n===== VALIDATION RESULT =====")
print("Errors:", len(errors))

if errors:
    print("\nFirst errors:")
    for error in errors[:20]:
        print(error)
    raise ValueError(f"BIO validation failed with {len(errors)} errors.")

print("\n===== M6.3.3 PASSED =====")
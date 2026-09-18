

import pandas as pd
import numpy as np

from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments,
)
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
)


# =========================
# 1. CONFIG
# =========================

MODEL_DIR = "experiments/phobert_model"
TEST_FILE = "data/processed/test.csv"

MAX_LENGTH = 64


# =========================
# 2. LOAD TEST DATA
# =========================

test_df = pd.read_csv(TEST_FILE)

required_columns = ["id", "text", "intent"]

if list(test_df.columns) != required_columns:
    raise ValueError(
        f"Test columns không đúng: {list(test_df.columns)}"
    )

print("\n===== TEST DATASET =====")
print(f"Test samples: {len(test_df)}")


# =========================
# 3. LOAD LABEL MAPPING
# =========================

model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_DIR
)

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_DIR
)

id2label = model.config.id2label

# Transformers có thể lưu key dưới dạng string
id2label = {
    int(key): value
    for key, value in id2label.items()
}

label2id = {
    label: idx
    for idx, label in id2label.items()
}

print("\n===== LABEL MAPPING =====")

for idx in sorted(id2label):
    print(f"{idx}: {id2label[idx]}")


# =========================
# 4. CHECK TEST LABELS
# =========================

unknown_labels = set(test_df["intent"]) - set(label2id)

if unknown_labels:
    raise ValueError(
        f"Test chứa label không có trong model: {unknown_labels}"
    )

test_df["label"] = test_df["intent"].map(label2id)


# =========================
# 5. CONVERT TO DATASET
# =========================

test_dataset = Dataset.from_pandas(
    test_df[["text", "label"]],
    preserve_index=False
)


# =========================
# 6. TOKENIZATION
# =========================

def tokenize_function(examples):
    return tokenizer(
        examples["text"],
        truncation=True,
        padding="max_length",
        max_length=MAX_LENGTH,
    )


test_dataset = test_dataset.map(
    tokenize_function,
    batched=True
)


# =========================
# 7. EVALUATION CONFIG
# =========================

evaluation_args = TrainingArguments(
    output_dir="experiments/phobert_test_eval",

    per_device_eval_batch_size=4,

    report_to="none",
)


# =========================
# 8. TRAINER
# =========================

trainer = Trainer(
    model=model,
    args=evaluation_args,

    eval_dataset=test_dataset,

    processing_class=tokenizer,
)


# =========================
# 9. PREDICTION
# =========================

print("\n===== START PHOBERT TEST EVALUATION =====")

prediction_output = trainer.predict(
    test_dataset
)

logits = prediction_output.predictions
y_true = prediction_output.label_ids

y_pred = np.argmax(
    logits,
    axis=-1
)


# =========================
# 10. METRICS
# =========================

accuracy = accuracy_score(
    y_true,
    y_pred
)

precision, recall, f1, _ = precision_recall_fscore_support(
    y_true,
    y_pred,
    average="macro",
    zero_division=0
)


# =========================
# 11. PRINT MAIN RESULTS
# =========================

print("\n===== PHOBERT TEST RESULT =====")

print(f"Accuracy:         {accuracy:.4f}")
print(f"Macro Precision:  {precision:.4f}")
print(f"Macro Recall:     {recall:.4f}")
print(f"Macro F1:         {f1:.4f}")


# =========================
# 12. CLASSIFICATION REPORT
# =========================

labels = list(range(len(id2label)))

target_names = [
    id2label[idx]
    for idx in labels
]

print("\n===== CLASSIFICATION REPORT =====")

print(
    classification_report(
        y_true,
        y_pred,
        labels=labels,
        target_names=target_names,
        digits=4,
        zero_division=0
    )
)


# =========================
# 13. CONFUSION MATRIX
# =========================

cm = confusion_matrix(
    y_true,
    y_pred,
    labels=labels
)

print("\n===== CONFUSION MATRIX =====")

print("Rows = Actual")
print("Columns = Predicted")

print("\nLabels:")

for idx, label in id2label.items():
    print(f"{idx}: {label}")

print("\nMatrix:")

print(cm)


# =========================
# 14. ERROR COUNT
# =========================

error_count = int(
    np.sum(y_true != y_pred)
)

correct_count = len(y_true) - error_count

print("\n===== PREDICTION SUMMARY =====")

print(f"Correct: {correct_count}/{len(y_true)}")
print(f"Errors:  {error_count}/{len(y_true)}")


print("\n===== TEST EVALUATION COMPLETED =====")
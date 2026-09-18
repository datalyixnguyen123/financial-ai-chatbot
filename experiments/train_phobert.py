
import pandas as pd
import numpy as np
import torch

from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
)
from sklearn.metrics import accuracy_score, precision_recall_fscore_support


# =========================
# 1. CONFIG
# =========================

MODEL_NAME = "vinai/phobert-base-v2"

TRAIN_FILE = "data/processed/train.csv"
VALIDATION_FILE = "data/processed/validation.csv"

OUTPUT_DIR = "experiments/phobert_model"

MAX_LENGTH = 64
RANDOM_STATE = 42


# =========================
# 2. LOAD DATA
# =========================

train_df = pd.read_csv(TRAIN_FILE)
validation_df = pd.read_csv(VALIDATION_FILE)

required_columns = ["text", "intent"]

if list(train_df.columns) != ["id", "text", "intent"]:
    raise ValueError(
        f"Train columns không đúng: {list(train_df.columns)}"
    )

if list(validation_df.columns) != ["id", "text", "intent"]:
    raise ValueError(
        f"Validation columns không đúng: {list(validation_df.columns)}"
    )


# =========================
# 3. LABEL MAPPING
# =========================

labels = sorted(train_df["intent"].unique())

label2id = {
    label: idx
    for idx, label in enumerate(labels)
}

id2label = {
    idx: label
    for label, idx in label2id.items()
}

print("\n===== LABEL MAPPING =====")

for label, idx in label2id.items():
    print(f"{idx}: {label}")


train_df["label"] = train_df["intent"].map(label2id)
validation_df["label"] = validation_df["intent"].map(label2id)


# =========================
# 4. CONVERT TO DATASET
# =========================

train_dataset = Dataset.from_pandas(
    train_df[["text", "label"]],
    preserve_index=False
)

validation_dataset = Dataset.from_pandas(
    validation_df[["text", "label"]],
    preserve_index=False
)


# =========================
# 5. TOKENIZER
# =========================

print("\n===== LOADING TOKENIZER =====")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)


def tokenize_function(examples):
    return tokenizer(
        examples["text"],
        truncation=True,
        padding="max_length",
        max_length=MAX_LENGTH,
    )


train_dataset = train_dataset.map(
    tokenize_function,
    batched=True
)

validation_dataset = validation_dataset.map(
    tokenize_function,
    batched=True
)


# =========================
# 6. LOAD MODEL
# =========================

print("\n===== LOADING PHOBERT =====")

model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=len(labels),
    id2label=id2label,
    label2id=label2id,
)


# =========================
# 7. METRICS
# =========================

def compute_metrics(eval_pred):

    logits, labels_true = eval_pred

    predictions = np.argmax(logits, axis=-1)

    accuracy = accuracy_score(
        labels_true,
        predictions
    )

    precision, recall, f1, _ = precision_recall_fscore_support(
        labels_true,
        predictions,
        average="macro",
        zero_division=0
    )

    return {
        "accuracy": accuracy,
        "macro_precision": precision,
        "macro_recall": recall,
        "macro_f1": f1,
    }


# =========================
# 8. TRAINING ARGUMENTS
# =========================

training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,

    eval_strategy="epoch",
    save_strategy="epoch",

    learning_rate=2e-5,

    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,

    num_train_epochs=3,

    weight_decay=0.01,

    load_best_model_at_end=True,

    metric_for_best_model="macro_f1",

    greater_is_better=True,

    logging_steps=20,

    report_to="none",

    seed=RANDOM_STATE,
)


# =========================
# 9. TRAINER
# =========================

trainer = Trainer(
    model=model,
    args=training_args,

    train_dataset=train_dataset,
    eval_dataset=validation_dataset,

    processing_class=tokenizer,

    compute_metrics=compute_metrics,
)


# =========================
# 10. TRAIN
# =========================

print("\n===== START PHOBERT TRAINING =====")

trainer.train()


# =========================
# 11. VALIDATION
# =========================

print("\n===== FINAL VALIDATION RESULT =====")

result = trainer.evaluate()

for key, value in result.items():

    if isinstance(value, float):
        print(f"{key}: {value:.4f}")
    else:
        print(f"{key}: {value}")


# =========================
# 12. SAVE MODEL
# =========================

trainer.save_model(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

print("\n===== MODEL SAVED =====")
print(f"Output: {OUTPUT_DIR}")
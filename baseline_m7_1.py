
# ============================================================
# M7.1 — INTENT CLASSIFICATION BASELINE
# TF-IDF + Logistic Regression
# ============================================================

from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    classification_report,
    confusion_matrix,
)


# ============================================================
# 1. CONFIG
# ============================================================
SEED = 42
PROJECT_ROOT = Path.cwd()
DATA_DIR = PROJECT_ROOT / "data" / "processed"
TRAIN_PATH = DATA_DIR / "intent_train.csv"
VAL_PATH = DATA_DIR / "intent_validation.csv"
TEST_PATH = DATA_DIR / "intent_test.csv"
EXPERIMENT_DIR = PROJECT_ROOT / "experiments" / "m7_1_baseline"
MODEL_DIR = PROJECT_ROOT / "models" / "intent_classifier"
EXPERIMENT_DIR.mkdir(parents=True, exist_ok=True)
MODEL_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. LOAD DATA
# ============================================================

def load_dataset(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")
    df = pd.read_csv(path, encoding="utf-8")
    required_columns = {"id", "text", "intent"}
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(
            f"{path.name} missing columns: {sorted(missing)}"
        )
    if df["text"].isna().any():
        raise ValueError(f"{path.name} contains null text")
    if df["intent"].isna().any():
        raise ValueError(f"{path.name} contains null intent")
    df["text"] = df["text"].astype(str)
    df["intent"] = df["intent"].astype(str)
    return df

train_df = load_dataset(TRAIN_PATH)
val_df = load_dataset(VAL_PATH)
test_df = load_dataset(TEST_PATH)

# ============================================================
# 3. DATASET AUDIT
# ============================================================

print("=" * 70)
print("M7.1 — DATASET AUDIT")
print("=" * 70)
print(f"Train:      {train_df.shape}")
print(f"Validation: {val_df.shape}")
print(f"Test:       {test_df.shape}")
print("\nLabel distribution:")
print("\nTRAIN")
print(train_df["intent"].value_counts().sort_index())
print("\nVALIDATION")
print(val_df["intent"].value_counts().sort_index())
print("\nTEST")
print(test_df["intent"].value_counts().sort_index())


# ============================================================
# 4. LEAKAGE CHECK
# ============================================================

train_texts = set(train_df["text"])
val_texts = set(val_df["text"])
test_texts = set(test_df["text"])

train_val_overlap = train_texts & val_texts
train_test_overlap = train_texts & test_texts
val_test_overlap = val_texts & test_texts

print("\n" + "=" * 70)
print("LEAKAGE CHECK")
print("=" * 70)
print("train ∩ validation:", len(train_val_overlap))
print("train ∩ test:", len(train_test_overlap))
print("validation ∩ test:", len(val_test_overlap))
if train_val_overlap or train_test_overlap or val_test_overlap:
    raise ValueError(
        "Exact-text leakage detected between dataset splits."
    )
print("PASS — no exact-text leakage.")


# ============================================================
# 5. PREPARE X / Y
# ============================================================

X_train = train_df["text"]
y_train = train_df["intent"]
X_val = val_df["text"]
y_val = val_df["intent"]
X_test = test_df["text"]
y_test = test_df["intent"]


# ============================================================
# 6. TF-IDF
# ============================================================

print("\n" + "=" * 70)
print("TF-IDF")
print("=" * 70)
vectorizer = TfidfVectorizer(
    lowercase=False,
    analyzer="word",
    ngram_range=(1, 2),
    min_df=1,
    max_df=0.95,
    sublinear_tf=True,
)
X_train_tfidf = vectorizer.fit_transform(X_train)
X_val_tfidf = vectorizer.transform(X_val)
X_test_tfidf = vectorizer.transform(X_test)
print("Train TF-IDF shape:", X_train_tfidf.shape)
print("Validation TF-IDF shape:", X_val_tfidf.shape)
print("Test TF-IDF shape:", X_test_tfidf.shape)


# ============================================================
# 7. MODEL
# ============================================================

print("\n" + "=" * 70)
print("LOGISTIC REGRESSION")
print("=" * 70)
model = LogisticRegression(
    max_iter=2000,
    class_weight=None,
    random_state=SEED,
    solver="lbfgs",
)


# ============================================================
# 8. TRAIN
# ============================================================

print("Training...")
model.fit(
    X_train_tfidf,
    y_train,
)
print("Training completed.")


# ============================================================
# 9. EVALUATION FUNCTION
# ============================================================

def evaluate_model(
    model,
    X,
    y,
    split_name: str,
):
    predictions = model.predict(X)

    accuracy = accuracy_score(y, predictions)

    precision, recall, f1, _ = precision_recall_fscore_support(
        y,
        predictions,
        average="macro",
        zero_division=0,
    )

    labels = sorted(
        set(y.tolist()) | set(predictions.tolist())
    )

    report = classification_report(
        y,
        predictions,
        labels=labels,
        target_names=labels,
        digits=4,
        zero_division=0,
    )

    cm = confusion_matrix(
        y,
        predictions,
        labels=labels,
    )

    metrics = {
        "split": split_name,
        "accuracy": float(accuracy),
        "macro_precision": float(precision),
        "macro_recall": float(recall),
        "macro_f1": float(f1),
        "num_samples": int(len(y)),
        "labels": labels,
    }
    return metrics, report, cm, predictions


# ============================================================
# 10. VALIDATION EVALUATION
# ============================================================

val_metrics, val_report, val_cm, val_predictions = evaluate_model(
    model,
    X_val_tfidf,
    y_val,
    "validation",
)
print("\n" + "=" * 70)
print("VALIDATION RESULTS")
print("=" * 70)
print(f"Accuracy:        {val_metrics['accuracy']:.4f}")
print(
    f"Macro Precision: {val_metrics['macro_precision']:.4f}"
)
print(
    f"Macro Recall:    {val_metrics['macro_recall']:.4f}"
)
print(
    f"Macro F1:        {val_metrics['macro_f1']:.4f}"
)
print("\nClassification Report:")
print(val_report)


# ============================================================
# 11. TEST EVALUATION
# ============================================================

# IMPORTANT:
# Test is evaluated only after the baseline configuration
# has been fixed using the training/validation setup.

test_metrics, test_report, test_cm, test_predictions = evaluate_model(
    model,
    X_test_tfidf,
    y_test,
    "test",
)
print("\n" + "=" * 70)
print("TEST RESULTS")
print("=" * 70)

print(
    f"Accuracy:        {test_metrics['accuracy']:.4f}"
)

print(
    f"Macro Precision: {test_metrics['macro_precision']:.4f}"
)

print(
    f"Macro Recall:    {test_metrics['macro_recall']:.4f}"
)

print(
    f"Macro F1:        {test_metrics['macro_f1']:.4f}"
)

print("\nClassification Report:")
print(test_report)


# ============================================================
# 12. CONFUSION MATRIX
# ============================================================

labels = test_metrics["labels"]

cm_df = pd.DataFrame(
    test_cm,
    index=labels,
    columns=labels,
)

cm_path = EXPERIMENT_DIR / "confusion_matrix_test.csv"

cm_df.to_csv(
    cm_path,
    encoding="utf-8",
)

print("\nConfusion matrix saved:")
print(cm_path)


# ============================================================
# 13. SAVE MODEL ARTIFACT
# ============================================================

model_artifact = {
    "model": model,
    "vectorizer": vectorizer,
    "labels": labels,
    "seed": SEED,
    "model_type": "TF-IDF + Logistic Regression",
}

model_path = MODEL_DIR / "intent_tfidf_lr_m7_1.joblib"

joblib.dump(
    model_artifact,
    model_path,
)

print("\nModel artifact saved:")
print(model_path)


# ============================================================
# 14. SAVE METRICS
# ============================================================

metrics = {
    "experiment_id": "M7.1",
    "objective": "Intent classification baseline",
    "dataset": {
        "train": str(TRAIN_PATH),
        "validation": str(VAL_PATH),
        "test": str(TEST_PATH),
        "train_samples": len(train_df),
        "validation_samples": len(val_df),
        "test_samples": len(test_df),
    },
    "model": {
        "type": "TF-IDF + Logistic Regression",
        "tfidf": {
            "analyzer": "word",
            "ngram_range": [1, 2],
            "lowercase": False,
            "min_df": 1,
            "max_df": 0.95,
            "sublinear_tf": True,
        },
        "logistic_regression": {
            "solver": "lbfgs",
            "max_iter": 2000,
            "class_weight": None,
            "random_state": SEED,
        },
    },
    "validation": val_metrics,
    "test": test_metrics,
}

metrics_path = EXPERIMENT_DIR / "metrics.json"
with open(
    metrics_path,
    "w",
    encoding="utf-8",
) as f:
    json.dump(
        metrics,
        f,
        ensure_ascii=False,
        indent=2,
    )
print("Metrics saved:")
print(metrics_path)


# ============================================================
# 15. SAVE CLASSIFICATION REPORT
# ============================================================

report_path = EXPERIMENT_DIR / "classification_report.txt"
with open(
    report_path,
    "w",
    encoding="utf-8",
) as f:
    f.write("M7.1 — TF-IDF + Logistic Regression\n")
    f.write("=" * 70 + "\n\n")
    f.write("VALIDATION\n")
    f.write("=" * 70 + "\n")
    f.write(val_report)
    f.write("\n\n")
    f.write("TEST\n")
    f.write("=" * 70 + "\n")
    f.write(test_report)
print("Classification report saved:")

print(report_path)


# ============================================================
# 16. INFERENCE FUNCTION
# ============================================================

def predict_intent(text: str):
    """
    Predict intent and confidence for one new message.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    text = text.strip()
    if not text:
        return {
            "intent": "unknown",
            "confidence": 0.0,
        }

    X = vectorizer.transform([text])
    intent = model.predict(X)[0]
    probabilities = model.predict_proba(X)[0]
    confidence = float(np.max(probabilities))
    return {
        "intent": intent,
        "confidence": confidence,
    }


# ============================================================
# 17. SAMPLE INFERENCE
# ============================================================

print("\n" + "=" * 70)
print("SAMPLE INFERENCE")
print("=" * 70)

sample_texts = [
    "Tôi vừa mua đồ ăn hết 200 nghìn",
    "Tháng này tài khoản còn bao nhiêu tiền?",
    "Tôi muốn tiết kiệm 30 triệu trong 6 tháng",
    "Nên bắt đầu quản lý tài chính cá nhân từ đâu?",
    "Tôi muốn đặt ngân sách ăn uống 2 triệu mỗi tháng",
]

for text in sample_texts:
    result = predict_intent(text)
    print("\nText:", text)
    print("Intent:", result["intent"])
    print("Confidence:", f"{result['confidence']:.4f}")


# ============================================================
# 18. FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("M7.1 BASELINE COMPLETED")
print("=" * 70)
print("Experiment ID: M7.1")
print("Model: TF-IDF + Logistic Regression")
print(
    f"Validation Macro-F1: "
    f"{val_metrics['macro_f1']:.4f}"
)
print(
    f"Test Macro-F1: "
    f"{test_metrics['macro_f1']:.4f}"
)
print("\nArtifacts:")
print("-", model_path)
print("-", metrics_path)
print("-", report_path)
print("-", cm_path)


# ============================================================
# TEST ERROR ANALYSIS
# ============================================================

error_df = test_df.copy()
error_df["predicted_intent"] = test_predictions
error_df["correct"] = (
    error_df["intent"] == error_df["predicted_intent"]
)
errors = error_df[~error_df["correct"]].copy()
print("\n" + "=" * 70)
print("TEST ERROR ANALYSIS")
print("=" * 70)
print(f"Errors: {len(errors)} / {len(test_df)}")

if len(errors) > 0:
    print(
        errors[
            ["id", "text", "intent", "predicted_intent"]
        ].to_string(index=False)
    )
else:
    print("No test errors.")

    
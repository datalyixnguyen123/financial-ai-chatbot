

import pandas as pd

from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    classification_report,
    confusion_matrix,
)

DATA_DIR = Path("data/processed/expense")

train_df = pd.read_csv(DATA_DIR / "train.csv")
val_df = pd.read_csv(DATA_DIR / "validation.csv")
test_df = pd.read_csv(DATA_DIR / "test.csv")


print("===== M8.4 EXPENSE BASELINE =====")
print(f"Train: {len(train_df)}")
print(f"Validation: {len(val_df)}")
print(f"Test: {len(test_df)}")


# -------------------------
# TF-IDF
# -------------------------

vectorizer = TfidfVectorizer(
    lowercase=True,
    ngram_range=(1, 2),
    min_df=1,
)
X_train = vectorizer.fit_transform(train_df["text"])
X_val = vectorizer.transform(val_df["text"])
X_test = vectorizer.transform(test_df["text"])


# -------------------------
# Logistic Regression
# -------------------------

model = LogisticRegression(max_iter = 1000, random_state = 42,)
model.fit(X_train, train_df["category"])


# -------------------------
# Evaluation function
# -------------------------

def evaluate(name, X, y):
    predictions = model.predict(X)
    accuracy = accuracy_score(y,predictions)
    macro_precision, macro_recall, macro_f1, _ = (
        precision_recall_fscore_support(
            y,
            predictions,
            average="macro",
            zero_division=0,
        )
    )
    print(f"\n===== {name} =====")
    print(f"Accuracy:         {accuracy:.4f}")
    print(f"Macro Precision:  {macro_precision:.4f}")
    print(f"Macro Recall:     {macro_recall:.4f}")
    print(f"Macro F1:         {macro_f1:.4f}")

    print("\nClassification Report:")
    print(classification_report(y, predictions, zero_division = 0))
    return predictions

# -------------------------
# Validation
# -------------------------

val_predictions = evaluate("VALIDATION", X_val, val_df["category"])


# -------------------------
# Test
# -------------------------

test_predictions = evaluate("TEST", X_test, test_df["category"])


# -------------------------
# Confusion Matrix
# -------------------------

labels = sorted(train_df["category"].unique())
cm = confusion_matrix(test_df["category"], test_predictions, labels = labels)
print("\n===== CONFUSION MATRIX =====")
print("Labels:")
print(labels)
print(cm)

# -------------------------
# Error Analysis
# -------------------------

errors = test_df[test_df["category"].values != test_predictions].copy()
errors["predicted"] = test_predictions[test_df["category"].values != test_predictions]

print("\n===== TEST ERRORS =====")
print(f"Errors: {len(errors)} / {len(test_df)}")

if len(errors) > 0:
    print(errors[["id", "text", "category", "predicted"]].to_string(index = False))

print("\n===== M8.4 COMPLETE =====")
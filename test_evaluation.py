

import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report


# =========================
# 1. Load datasets
# =========================

train_df = pd.read_csv("data/processed/train.csv")
test_df = pd.read_csv("data/processed/test.csv")

X_train = train_df["text"]
y_train = train_df["intent"]

X_test = test_df["text"]
y_test = test_df["intent"]


# =========================
# 2. TF-IDF
# =========================

vectorizer = TfidfVectorizer(
    lowercase=True,
    ngram_range=(1, 2),
    max_features=10000
)

X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)


# =========================
# 3. Logistic Regression
# =========================

model = LogisticRegression(
    max_iter=1000,
    random_state=42
)

model.fit(X_train_tfidf, y_train)


# =========================
# 4. Prediction
# =========================

y_pred = model.predict(X_test_tfidf)


# =========================
# 5. Evaluation
# =========================

accuracy = accuracy_score(y_test, y_pred)

print("\n===== TEST BASELINE RESULT =====")
print(f"Accuracy: {accuracy:.4f}")

print("\n===== CLASSIFICATION REPORT =====")
print(
    classification_report(
        y_test,
        y_pred,
        digits=4
    )
)
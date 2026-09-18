
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report


# =========================
# 1. Load dataset
# =========================

train_df = pd.read_csv("data/processed/train.csv")
validation_df = pd.read_csv("data/processed/validation.csv")

X_train = train_df["text"]
y_train = train_df["intent"]

X_validation = validation_df["text"]
y_validation = validation_df["intent"]


# =========================
# 2. TF-IDF
# =========================

vectorizer = TfidfVectorizer(
    lowercase=True,
    ngram_range=(1, 2),
    max_features=10000
)

X_train_tfidf = vectorizer.fit_transform(X_train)
X_validation_tfidf = vectorizer.transform(X_validation)


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

y_pred = model.predict(X_validation_tfidf)


# =========================
# 5. Evaluation
# =========================

accuracy = accuracy_score(y_validation, y_pred)

print("\n===== BASELINE RESULT =====")
print(f"Accuracy: {accuracy:.4f}")

print("\n===== CLASSIFICATION REPORT =====")
print(
    classification_report(
        y_validation,
        y_pred,
        digits=4
    )
)
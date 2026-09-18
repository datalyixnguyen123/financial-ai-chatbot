
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix


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
# 3. Train model
# =========================

model = LogisticRegression(
    max_iter=1000,
    random_state=42
)

model.fit(X_train_tfidf, y_train)


# =========================
# 4. Predict
# =========================

y_pred = model.predict(X_validation_tfidf)


# =========================
# 5. Show errors
# =========================

result_df = validation_df.copy()
result_df["predicted_intent"] = y_pred

errors = result_df[
    result_df["intent"] != result_df["predicted_intent"]
]

print("\n===== MISCLASSIFIED SAMPLES =====")
print(f"Number of errors: {len(errors)}")

if len(errors) > 0:
    for _, row in errors.iterrows():
        print("\nText:", row["text"])
        print("Actual:", row["intent"])
        print("Predicted:", row["predicted_intent"])


# =========================
# 6. Confusion Matrix
# =========================

labels = sorted(y_validation.unique())

cm = confusion_matrix(
    y_validation,
    y_pred,
    labels=labels
)

print("\n===== CONFUSION MATRIX =====")
print("Labels:")
print(labels)
print(cm)
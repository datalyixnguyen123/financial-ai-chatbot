

from pathlib import Path
import joblib
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    classification_report,
    confusion_matrix,
)

PROJECT_ROOT = Path.cwd()
MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "intent_classifier"
    / "intent_tfidf_lr_m7_1.joblib"
)
OUTPUT_DIR = (
    PROJECT_ROOT
    / "experiments"
    / "m7_1_baseline"
)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
EVAL_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "intent_long_query_eval.csv"
)


# ============================================================
# 1. LONG QUERY DATASET
# ============================================================

LONG_QUERY_DATA = [
    {
        "id": "LQ01",
        "text": (
            "Sau khi trừ toàn bộ các khoản mình đã chi trong "
            "tháng này thì hiện tại tài khoản còn lại bao nhiêu tiền?"
        ),
        "intent": "query_balance",
    },
    {
        "id": "LQ02",
        "text": (
            "Từ đầu tháng tới giờ mình đã tiêu tổng cộng bao nhiêu "
            "tiền cho tất cả các khoản?"
        ),
        "intent": "query_expense",
    },
    {
        "id": "LQ03",
        "text": (
            "Trong tháng này mình đã chi bao nhiêu tiền riêng cho "
            "việc ăn uống và đi lại?"
        ),
        "intent": "query_category",
    },
    {
        "id": "LQ04",
        "text": (
            "Thu nhập mỗi tháng của mình khoảng 15 triệu nhưng "
            "thường cuối tháng không còn nhiều tiền, mình nên bắt "
            "đầu quản lý tài chính như thế nào?"
        ),
        "intent": "financial_advice",
    },
    {
        "id": "LQ05",
        "text": (
            "Mình muốn dành dụm 30 triệu trong vòng 6 tháng tới "
            "thì mỗi tháng cần tiết kiệm khoảng bao nhiêu?"
        ),
        "intent": "saving_goal",
    },
    {
        "id": "LQ06",
        "text": (
            "Từ tháng này mình muốn giới hạn chi tiêu cho ăn uống "
            "tối đa 2 triệu mỗi tháng và theo dõi khoản đó."
        ),
        "intent": "set_budget",
    },
    {
        "id": "LQ07",
        "text": (
            "Hôm qua mình đi siêu thị mua đồ ăn và một số vật dụng "
            "trong nhà, tổng cộng thanh toán hết khoảng 850 nghìn."
        ),
        "intent": "add_expense",
    },
    {
        "id": "LQ08",
        "text": (
            "Tháng này công ty vừa chuyển cho mình tiền lương "
            "khoảng 18 triệu vào tài khoản."
        ),
        "intent": "add_income",
    },

    {
        "id": "LQ09",
        "text": (
            "Mình muốn kiểm tra xem sau tất cả những khoản mua sắm "
            "và thanh toán trong tháng này thì số dư hiện tại còn "
            "lại bao nhiêu."
        ),
        "intent": "query_balance",
    },
    {
        "id": "LQ10",
        "text": (
            "Bạn có thể thống kê giúp mình từ đầu tháng đến giờ "
            "tổng cộng mình đã chi bao nhiêu tiền không?"
        ),
        "intent": "query_expense",
    },
    {
        "id": "LQ11",
        "text": (
            "Mình muốn biết tháng này riêng khoản tiền điện, tiền "
            "ăn uống và tiền đi lại đã tiêu hết bao nhiêu."
        ),
        "intent": "query_category",
    },
    {
        "id": "LQ12",
        "text": (
            "Mình có thu nhập tương đối ổn định nhưng thường xuyên "
            "chi tiêu vượt kế hoạch, bạn có thể hướng dẫn mình cách "
            "quản lý tiền hiệu quả hơn không?"
        ),
        "intent": "financial_advice",
    },
    {
        "id": "LQ13",
        "text": (
            "Mục tiêu của mình là tiết kiệm được 50 triệu trong "
            "10 tháng tới, vậy mình nên dành ra bao nhiêu tiền "
            "mỗi tháng?"
        ),
        "intent": "saving_goal",
    },
    {
        "id": "LQ14",
        "text": (
            "Mình muốn đặt ngân sách cho việc mua sắm trong tháng "
            "này không vượt quá 3 triệu và muốn theo dõi mức sử dụng."
        ),
        "intent": "set_budget",
    },
    {
        "id": "LQ15",
        "text": (
            "Cuối tuần vừa rồi mình đi ăn uống với bạn bè và mua "
            "thêm vài món đồ cá nhân, tổng số tiền đã thanh toán "
            "là khoảng 600 nghìn."
        ),
        "intent": "add_expense",
    },
    {
        "id": "LQ16",
        "text": (
            "Mình vừa nhận được tiền lương tháng này từ công ty "
            "chuyển vào tài khoản với số tiền khoảng 20 triệu."
        ),
        "intent": "add_income",
    },
]


eval_df = pd.DataFrame(LONG_QUERY_DATA)
eval_df.to_csv(EVAL_PATH,index=False,encoding="utf-8",)
print("=" * 70)
print("M7.1.1 — LONG QUERY EVALUATION")
print("=" * 70)
print(f"Samples: {len(eval_df)}")
print(f"Saved dataset: {EVAL_PATH}")
print("\nIntent distribution:")
print(eval_df["intent"].value_counts().sort_index())


if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Model not found: {MODEL_PATH}"
    )
artifact = joblib.load(MODEL_PATH)
model = artifact["model"]
vectorizer = artifact["vectorizer"]

X = vectorizer.transform(eval_df["text"])
predictions = model.predict(X)
probabilities = model.predict_proba(X)
confidences = probabilities.max(axis=1)
eval_df["predicted_intent"] = predictions
eval_df["confidence"] = confidences
eval_df["correct"] = (eval_df["intent"]== eval_df["predicted_intent"])


accuracy = accuracy_score(eval_df["intent"], eval_df["predicted_intent"],)
precision, recall, f1, _ = (
    precision_recall_fscore_support(
        eval_df["intent"],
        eval_df["predicted_intent"],
        average="macro",
        zero_division=0,
    )
)

print("\n" + "=" * 70)
print("LONG QUERY RESULTS")
print("=" * 70)
print(f"Accuracy:        {accuracy:.4f}")
print(f"Macro Precision: {precision:.4f}")
print(f"Macro Recall:    {recall:.4f}")
print(f"Macro F1:        {f1:.4f}")


labels = sorted(set(eval_df["intent"]) | set(eval_df["predicted_intent"]))
report = classification_report(
    eval_df["intent"],
    eval_df["predicted_intent"],
    labels=labels,
    target_names=labels,
    digits=4,
    zero_division=0,
)
print("\nClassification Report:")
print(report)


print("\n" + "=" * 70)
print("SAMPLE RESULTS")
print("=" * 70)
for _, row in eval_df.iterrows():
    status = "PASS" if row["correct"] else "ERROR"
    print(
        f"\n[{status}] {row['id']}"
    )
    print(
        "Text:",
        row["text"]
    )
    print(
        "Gold:",
        row["intent"]
    )
    print(
        "Pred:",
        row["predicted_intent"]
    )
    print(
        "Confidence:",
        f"{row['confidence']:.4f}"
    )


errors = eval_df[~eval_df["correct"]].copy()
print("\n" + "=" * 70)
print("LONG QUERY ERROR ANALYSIS")
print("=" * 70)
print(f"Errors: {len(errors)} / {len(eval_df)}")

if len(errors) > 0:
    print(errors[[ "id","text","intent","predicted_intent","confidence",]].to_string(index=False))
else:
    print("No errors.")


RESULT_PATH = (
    OUTPUT_DIR
    / "long_query_results.csv"
)
eval_df.to_csv(
    RESULT_PATH,
    index=False,
    encoding="utf-8",
)
print("\nResults saved:")
print(RESULT_PATH)


metrics = {"experiment_id": "M7.1.1","objective": ("Evaluate baseline intent classifier ""on long user queries"),
    "evaluation_only": True,
    "num_samples": int(len(eval_df)),
    "accuracy": float(accuracy),
    "macro_precision": float(precision),
    "macro_recall": float(recall),
    "macro_f1": float(f1),
    "errors": int(len(errors)),
}
METRICS_PATH = (OUTPUT_DIR/ "long_query_metrics.json")

import json
with open(METRICS_PATH,"w",encoding="utf-8",) as f:
    json.dump(metrics,f,ensure_ascii=False,indent=2,)
print(METRICS_PATH)
print("\n" + "=" * 70)
print("M7.1.1 COMPLETED")
print("=" * 70)
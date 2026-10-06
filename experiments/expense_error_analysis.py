
import pandas as pd
from pathlib import Path


DATA_DIR = Path("data/processed/expense")

test_df = pd.read_csv(DATA_DIR / "test.csv")

errors = pd.DataFrame([
    {
        "id": 338,
        "text": "Mua giày hết 1 triệu 1",
        "true_category": "shopping",
        "predicted_category": "food",
        "error_type": "shopping_to_food",
    },
    {
        "id": 536,
        "text": "Đi xe ôm công nghệ hết 40 nghìn",
        "true_category": "transport",
        "predicted_category": "food",
        "error_type": "transport_to_food",
    },
    {
        "id": 335,
        "text": "Mua tài liệu học tập hết 180 nghìn",
        "true_category": "education",
        "predicted_category": "food",
        "error_type": "education_to_food",
    },
    {
        "id": 344,
        "text": "Mua quà cho bạn hết 250k",
        "true_category": "other",
        "predicted_category": "food",
        "error_type": "other_to_food",
    },
    {
        "id": 231,
        "text": "Tối qua đi karaoke hết 600k",
        "true_category": "entertainment",
        "predicted_category": "food",
        "error_type": "entertainment_to_food",
    },
    {
        "id": 48,
        "text": "Vừa mua tai nghe hết 1 triệu",
        "true_category": "shopping",
        "predicted_category": "food",
        "error_type": "shopping_to_food",
    },
    {
        "id": 229,
        "text": "Sáng nay đi bus mất 15k",
        "true_category": "transport",
        "predicted_category": "food",
        "error_type": "transport_to_food",
    },
    {
        "id": 135,
        "text": "Mua vở với bút hết 150k",
        "true_category": "education",
        "predicted_category": "food",
        "error_type": "education_to_food",
    },
    {
        "id": 334,
        "text": "Tháng này trả tiền thuê nhà 5 củ",
        "true_category": "rent",
        "predicted_category": "food",
        "error_type": "rent_to_food",
    },
])


print("===== M8.5 ERROR ANALYSIS =====")

print(f"Test samples: {len(test_df)}")
print(f"Errors: {len(errors)}")

print("\n===== ERROR TYPES =====")

print(errors["error_type"].value_counts())

print("\n===== ERROR TABLE =====")
print(errors[["id", "text", "true_category", "predicted_category",]].to_string(index = False))


print("\n===== MAIN FINDING =====")

food_errors = (errors["predicted_category"] == "food").sum()

print(f"{food_errors}/{len(errors)} errors ""were predicted as food.")

assert len(errors) == 9
assert food_errors == 9

print("\n===== M8.5 PASS =====")
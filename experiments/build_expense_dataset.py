
import pandas as pd
import re
from pathlib import Path


INPUT = Path("data/raw/intent_dataset.csv")
OUTPUT = Path("data/raw/expense_dataset.csv")

CATEGORY_KEYWORDS = {
    "food": [
        "ăn",
        "phở",
        "cơm",
        "bánh mì",
        "bánh ngọt",
        "bún",
        "mì",
        "xôi",
        "lẩu",
        "cafe",
        "cà phê",
        "trà sữa",
        "đồ ăn",
        "ăn vặt",
        "nhà hàng",
        "nhậu",
    ],

    "transport": [
        "xăng",
        "grab",
        "taxi",
        "xe ôm",
        "grabbike",
        "bus",
        "xe buýt",
        "vé tàu",
        "vé xe",
    ],

    "education": [
        "sách",
        "vở",
        "bút",
        "giáo trình",
        "tài liệu học tập",
        "khóa học",
        "học phí",
        "tiền học",
        "đồ dùng học tập",
    ],

    "shopping": [
        "giày",
        "dép",
        "áo",
        "quần",
        "quần áo",
        "balo",
        "mỹ phẩm",
        "tai nghe",
        "shopee",
        "siêu thị",
        "mua đồ",
    ],

    "entertainment": [
        "xem phim",
        "vé xem phim",
        "karaoke",
        "concert",
        "đi chơi",
    ],

    "health": [
        "thuốc",
        "hiệu thuốc",
        "nhà thuốc",
    ],

    "bills": [
        "tiền điện",
        "tiền nước",
        "điện nước",
        "hóa đơn điện",
        "hóa đơn nước",
        "internet",
        "wifi",
        "tiền mạng",
        "hóa đơn mạng",
        "điện thoại",
    ],

    "rent": [
        "tiền thuê nhà",
        "thuê nhà",
        "tiền nhà",
        "tiền phòng",
        "phòng tháng",
    ],

    "other": [
        "quà",
        "bánh sinh nhật",
    ],
}

def classify_expense(text: str):
    text_lower = text.lower()
    matched = []
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                matched.append(category)
                break

    matched = list(dict.fromkeys(matched))
    if len(matched) == 1:
        return matched[0]
    if len(matched) == 0:
        return None
    return "AMBIGUOUS"

def main():
    df = pd.read_csv(INPUT)
    # Only expense utterances
    expense_df = df[df["intent"] == "add_expense"].copy()
    print("===== M8.1 EXPENSE DATASET BUILD =====")
    print(f"Input rows: {len(df)}")
    print(f"Expense rows: {len(expense_df)}")
    expense_df["category"] = expense_df["text"].apply(classify_expense)

    print("\n===== CATEGORY DISTRIBUTION =====")
    print(expense_df["category"].value_counts(dropna=False))
    review = expense_df[expense_df["category"].isna() | (expense_df["category"] == "AMBIGUOUS")]

    print("\n===== MANUAL REVIEW =====")

    if len(review) == 0:
        print("No ambiguous samples.")
    else:
        print(review[["id", "text", "category"]].to_string(index=False))

    # Save only samples with a single clear category
    clean_df = expense_df[expense_df["category"].notna() & (expense_df["category"] != "AMBIGUOUS")
    ][["id", "text", "category"]]
    OUTPUT.parent.mkdir(parents = True, exist_ok = True)
    clean_df.to_csv(OUTPUT, index = False, encoding = "utf-8-sig")

    print("\n===== RESULT =====")
    print(f"Saved rows: {len(clean_df)}")
    print(f"Saved: {OUTPUT}")

    print("\n===== M8.1 CHECK =====")
    expected_columns = [
        "id",
        "text",
        "category"
    ]
    assert list(clean_df.columns) == expected_columns
    assert len(clean_df) > 0
    assert clean_df["category"].notna().all()

    print("Schema: PASS")
    print("No unresolved rows: PASS")
    print("M8.1 BUILD: PASS")
    

if __name__ == "__main__":
    main()
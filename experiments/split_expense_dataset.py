
import pandas as pd
from sklearn.model_selection import train_test_split
from pathlib import Path


INPUT = Path("data/raw/expense_dataset.csv")
OUTPUT_DIR = Path("data/processed/expense")

df = pd.read_csv(INPUT)

print("===== M8.3 EXPENSE DATASET SPLIT =====")
print(f"Total: {len(df)}")

# 70% train, 30% temporary
train_df, temp_df = train_test_split(
    df,
    test_size=0.30,
    random_state=42,
    stratify=df["category"],
)

# 15% validation, 15% test
val_df, test_df = train_test_split(
    temp_df,
    test_size=0.50,
    random_state=42,
    stratify=temp_df["category"],
)

OUTPUT_DIR.mkdir(parents = True, exist_ok = True)

train_df.to_csv(
    OUTPUT_DIR / "train.csv",
    index=False,
    encoding="utf-8-sig"
)

val_df.to_csv(
    OUTPUT_DIR / "validation.csv",
    index=False,
    encoding="utf-8-sig"
)

test_df.to_csv(
    OUTPUT_DIR / "test.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\n===== SPLIT =====")
print(f"Train:      {len(train_df)}")
print(f"Validation: {len(val_df)}")
print(f"Test:       {len(test_df)}")

print("\n===== DISTRIBUTION =====")

for name, data in [
    ("TRAIN", train_df),
    ("VALIDATION", val_df),
    ("TEST", test_df),
]:
    print(f"\n{name}")
    print(data["category"].value_counts())

print("\n===== CHECK =====")

assert len(train_df) + len(val_df) + len(test_df) == len(df)

assert set(train_df["text"]).isdisjoint(set(val_df["text"]))

assert set(train_df["text"]).isdisjoint(set(test_df["text"]))

assert set(val_df["text"]).isdisjoint(set(test_df["text"]))

assert train_df["category"].notna().all()
assert val_df["category"].notna().all()
assert test_df["category"].notna().all()

print("No overlap: PASS")
print("Labels valid: PASS")
print("M8.3 PASS")
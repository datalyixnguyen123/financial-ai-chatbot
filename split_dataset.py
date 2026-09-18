
import pandas as pd
from sklearn.model_selection import train_test_split

INPUT_FILE = "data/raw/intent_dataset.csv"

TRAIN_FILE = "data/processed/train.csv"
VALIDATION_FILE = "data/processed/validation.csv"
TEST_FILE = "data/processed/test.csv"

RANDOM_STATE = 42

df = pd.read_csv(INPUT_FILE)

required_columns = ["id", "text", "intent"]

if list(df.columns) != required_columns:
    raise ValueError(
        f"Columns không đúng. Expected: {required_columns}, "
        f"Found: {list(df.columns)}"
    )

if len(df) != 800:
    raise ValueError(
        f"Dataset phải có 800 rows, nhưng hiện có {len(df)} rows."
    )

train_df, temp_df = train_test_split(
    df,
    test_size=0.30,
    random_state=RANDOM_STATE,
    shuffle=True
)

validation_df, test_df = train_test_split(
    temp_df,
    test_size=0.50,
    random_state=RANDOM_STATE,
    shuffle=True
)

train_df = train_df[required_columns]
validation_df = validation_df[required_columns]
test_df = test_df[required_columns]

train_df.to_csv(TRAIN_FILE, index=False)
validation_df.to_csv(VALIDATION_FILE, index=False)
test_df.to_csv(TEST_FILE, index=False)

print("Dataset split completed.")
print(f"Train:      {len(train_df)} rows")
print(f"Validation: {len(validation_df)} rows")
print(f"Test:       {len(test_df)} rows")
print(f"Total:      {len(train_df) + len(validation_df) + len(test_df)} rows")
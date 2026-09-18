
import pandas as pd

files = [
    "data/processed/train.csv",
    "data/processed/validation.csv",
    "data/processed/test.csv"
]

for file in files:
    df = pd.read_csv(file)

    print("\n" + file)
    print("Rows:", len(df))
    print(df["intent"].value_counts().sort_index())
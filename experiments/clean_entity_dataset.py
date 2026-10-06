
import json
import pandas as pd

INPUT_FILE = "data/raw/entity_dataset.csv"
OUTPUT_FILE = "data/processed/entity_dataset_clean.csv"

df = pd.read_csv(INPUT_FILE)

print("===== ENTITY DATASET CLEANING =====")
print("Before:", len(df))

# 1. Remove duplicated header rows
df = df[df["entities"].astype(str).str.strip() != "entities"].copy()
print("After removing headers:", len(df))

# 2. Fix duration -> period for query time-range examples
fix_ids = [86, 187, 281, 380, 480, 580, 680, 780]
changed_duration = 0

for idx, row in df.iterrows():
    row_id = int(row["id"])
    if row_id not in fix_ids:
        continue
    entities = json.loads(row["entities"])
    duration_value = entities.get("duration")
    if duration_value is not None:
        entities["period"] = duration_value
        entities["duration"] = None
        df.at[idx, "entities"] = json.dumps(entities, ensure_ascii = False)
        changed_duration += 1

# 3. Normalize string "null"/"None" -> actual JSON null
changed_null = 0
for idx, row in df.iterrows():
    entities = json.loads(row["entities"])
    for key, value in entities.items():
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in ["null", "none", ""]:
                entities[key] = None
                changed_null += 1
    df.at[idx, "entities"] = json.dumps(entities, ensure_ascii = False)


# 4. Validate row count
if len(df) != 800:
    raise ValueError(f"Expected 800 rows, got {len(df)}")

# 5. Validate JSON
invalid_json = []
for _, row in df.iterrows():
    try:
        entities = json.loads(row["entities"])
        if not isinstance(entities, dict):
            invalid_json.append(int(row["id"]))
    except Exception:
        invalid_json.append(int(row["id"]))

if invalid_json:
    raise ValueError(f"Invalid JSON rows: {invalid_json}")

# 6. Validate no fake null strings remain
fake_nulls = []
for _, row in df.iterrows():
    entities = json.loads(row["entities"])
    for key, value in entities.items():
        if isinstance(value, str) and value.strip().lower() in [
            "null",
            "none"
        ]:
            fake_nulls.append(
                (int(row["id"]), key, value)
            )

if fake_nulls:
    raise ValueError(f"Fake null values remain: {fake_nulls}")

# 7. Save
df.to_csv(OUTPUT_FILE, index = False)


print("\n===== RESULT =====")
print("Final rows:", len(df))
print("Duration → Period fixes:", changed_duration)
print("Null normalization:", changed_null)
print("Invalid JSON:", len(invalid_json))
print("Fake null values:", len(fake_nulls))

print("\nSaved:")
print(OUTPUT_FILE)

print("\n===== M6.2.2 COMPLETE =====")
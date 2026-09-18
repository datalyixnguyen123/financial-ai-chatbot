
from app.services.normalization_service import normalize_amount


TEST_CASES = [
    ("50k", 50_000),
    ("50 nghìn", 50_000),
    ("50 ngàn", 50_000),
    ("50.000", 50_000),
    ("1 triệu", 1_000_000),
    ("2 củ", 2_000_000),
    ("4 củ", 4_000_000),
    ("1 triệu rưỡi", 1_500_000),
    ("1 triệu 500 nghìn", 1_500_000),
    ("750k", 750_000),
    ("800 nghìn", 800_000),
    ("5 triệu", 5_000_000),
    ("0.05 triệu", 50_000),
    ("5 chục", 50_000),
    ("năm chục", 50_000),
]


for raw_value, expected in TEST_CASES:
    result = normalize_amount(raw_value)

    assert result == expected, (
        f"FAILED: {raw_value} "
        f"expected={expected}, got={result}"
    )

    print(f"PASS: {raw_value} -> {result}")


print("\nAll normalization tests passed.")
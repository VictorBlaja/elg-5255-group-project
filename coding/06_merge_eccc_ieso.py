
from pathlib import Path
import pandas as pd

# ============================================================
# 1. Directories
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "processed"

# ============================================================
# 2. Load prepared datasets
# ============================================================

ieso = pd.read_csv(
    DATA_DIR / "ieso_ottawa_hourly_features.csv",
    parse_dates=["Date", "Target_Date"]
)

weather = pd.read_csv(
    DATA_DIR / "eccc_ottawa_hourly_2020_2025.csv",
    parse_dates=["DateTime_LST"]
)

# ============================================================
# 3. Construct IESO hour-ending timestamps
# ============================================================

ieso["DateTime_EST"] = (
    ieso["Date"]
    + pd.to_timedelta(ieso["Hour"], unit="h")
)

# ============================================================
# 4. Merge weather with electricity demand
# ============================================================

merged = ieso.merge(
    weather[
        [
            "DateTime_LST",
            "Temperature_C",
            "Was_Imputed"
        ]
    ].rename(columns={
        "Was_Imputed": "Weather_Was_Imputed"
    }),
    left_on="DateTime_EST",
    right_on="DateTime_LST",
    how="left",
    validate="one_to_one"
)

# ============================================================
# 5. Check merge quality
# ============================================================

print("\nMerged dataset shape:")
print(merged.shape)

print("\nMissing temperatures after merge:")
print(merged["Temperature_C"].isna().sum())

print("\nFirst observations:")
print(
    merged[
        [
            "Date",
            "Hour",
            "DateTime_EST",
            "Ottawa",
            "Temperature_C"
        ]
    ].head(10).to_string(index=False)
)

print("\nLast observations:")
print(
    merged[
        [
            "Date",
            "Hour",
            "DateTime_EST",
            "Ottawa",
            "Temperature_C"
        ]
    ].tail(5).to_string(index=False)
)

# ============================================================
# 6. Save merged dataset
# ============================================================

output_file = DATA_DIR / "ieso_eccc_ottawa_merged.csv"

merged.to_csv(output_file, index=False)

print(f"\nMerged dataset saved: {output_file}")


# ============================================================
# 7. Check merged dataset
# ============================================================

from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent

file_path = (
    BASE_DIR
    / "data"
    / "processed"
    / "ieso_eccc_ottawa_merged.csv"
)

df = pd.read_csv(file_path, low_memory=False)

df["Weather_Was_Imputed"] = (
    df["Weather_Was_Imputed"]
    .astype("boolean")
)

print("Dataset shape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nMissing values:")
print(df.isna().sum())

print("\nDuplicate IESO timestamps:")
print(df.duplicated(["Date", "Hour"]).sum())

print("\nDemand statistics:")
print(df["Ottawa"].describe())

print("\nTemperature statistics:")
print(df["Temperature_C"].describe())
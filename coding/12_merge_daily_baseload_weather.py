
from pathlib import Path
import pandas as pd

# ============================================================
# 1. File paths
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "processed"

baseload_file = DATA_DIR / "ieso_ottawa_daily_baseload.csv"
weather_file = DATA_DIR / "eccc_ottawa_daily_2020_2025.csv"

output_file = DATA_DIR / "daily_baseload_weather_merged.csv"

# ============================================================
# 2. Load datasets
# ============================================================

baseload = pd.read_csv(baseload_file)
weather = pd.read_csv(weather_file)

print("\nBASELOAD COLUMNS:")
print(baseload.columns.tolist())

print("\nWEATHER COLUMNS:")
print(weather.columns.tolist())

# ============================================================
# 3. Convert dates
# ============================================================

baseload["Date"] = pd.to_datetime(baseload["Date"])
weather["Date"] = pd.to_datetime(weather["Date"])

# ============================================================
# 4. Merge on the current day's date
# ============================================================

merged = baseload.merge(
    weather[
        [
            "Date",
            "Temperature_Mean_C",
            "Temperature_Min_C",
            "Temperature_Max_C",
            "Hourly_Observations",
            "Imputed_Hours"
        ]
    ],
    on="Date",
    how="left",
    validate="one_to_one"
)

# ============================================================
# 5. Validate
# ============================================================

print("\nMERGE SUMMARY")
print("=" * 50)

print(f"Baseload rows: {len(baseload)}")
print(f"Merged rows:   {len(merged)}")

print(
    "Missing daily temperatures:",
    merged["Temperature_Mean_C"].isna().sum()
)

print("\nFirst 5 rows:")
print(merged.head().to_string(index=False))

print("\nLast 5 rows:")
print(merged.tail().to_string(index=False))

# ============================================================
# 6. Save
# ============================================================

merged.to_csv(output_file, index=False)

print("\nSaved to:")
print(output_file)

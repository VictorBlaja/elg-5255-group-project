
from pathlib import Path
import pandas as pd

# ============================================================
# 1. File paths
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "processed"

input_file = DATA_DIR / "daily_baseload_weather_merged.csv"

# ============================================================
# 2. Load and sort
# ============================================================

df = pd.read_csv(input_file)

df["Date"] = pd.to_datetime(df["Date"])
df["Target_Date"] = pd.to_datetime(df["Target_Date"])

df = df.sort_values("Date").reset_index(drop=True)

# ============================================================
# 3. Select model features
# ============================================================

features = [
    "Baseload_d",
    "Baseload_d_minus_1",
    "Baseload_d_minus_7",
    "Temperature_Mean_C",
    "Temperature_Min_C",
    "Temperature_Max_C",
    "DayOfWeek",
    "Month",
    "IsWeekend"
]

target = "Target_Next_Day_Baseload"

# ============================================================
# 4. Exclude imputed observations
# ============================================================

df["Was_Imputed"] = (
    df["Was_Imputed"]
    .astype(str)
    .str.lower()
    .eq("true")
)

# Exclude current, lagged, and target days with imputed demand
demand_affected = (
    df["Was_Imputed"]
    | df["Was_Imputed"].shift(1, fill_value=False)
    | df["Was_Imputed"].shift(7, fill_value=False)
    | df["Was_Imputed"].shift(-1, fill_value=False)
)

# Exclude days with interpolated weather
weather_affected = df["Imputed_Hours"] > 0

df = df.loc[
    ~(demand_affected | weather_affected)
].copy()

# ============================================================
# 5. Remove rows missing required values
# ============================================================

df = df.dropna(subset=features + [target])

# ============================================================
# 6. Chronological split by target date
# ============================================================

train = df[df["Target_Date"].dt.year <= 2023].copy()
validation = df[df["Target_Date"].dt.year == 2024].copy()
test = df[df["Target_Date"].dt.year == 2025].copy()

# ============================================================
# 7. Save datasets
# ============================================================

train.to_csv(
    DATA_DIR / "daily_train.csv",
    index=False
)

validation.to_csv(
    DATA_DIR / "daily_validation.csv",
    index=False
)

test.to_csv(
    DATA_DIR / "daily_test.csv",
    index=False
)

# ============================================================
# 8. Summary
# ============================================================

print("\nDAILY BASELOAD DATASET SUMMARY")
print("=" * 50)

print(f"Training rows:   {len(train)}")
print(f"Validation rows: {len(validation)}")
print(f"Test rows:       {len(test)}")

print("\nTarget date ranges:")

for name, data in [
    ("Training", train),
    ("Validation", validation),
    ("Test", test)
]:
    print(
        f"{name}: "
        f"{data['Target_Date'].min().date()} to "
        f"{data['Target_Date'].max().date()}"
    )

print("\nFeatures:")
for feature in features:
    print("-", feature)

print("\nDatasets saved successfully.")

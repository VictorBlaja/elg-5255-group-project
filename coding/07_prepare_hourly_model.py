
from pathlib import Path
import pandas as pd

# ============================================================
# 1. Directories
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "processed"

# ============================================================
# 2. Load merged dataset
# ============================================================

df = pd.read_csv(
    DATA_DIR / "ieso_eccc_ottawa_merged.csv",
    low_memory=False,
    parse_dates=["Date", "Target_Date", "DateTime_EST"]
)

# ============================================================
# 3. Select forecasting features
# ============================================================

features = [
    "Demand_t",
    "Demand_t_minus_1",
    "Demand_t_minus_24",
    "Demand_t_minus_168",
    "Temperature_C",
    "Target_Hour",
    "DayOfWeek",
    "Month",
    "IsWeekend"
]

target = "Target_Next_Hour"

# ============================================================
# 4. Exclude rows affected by imputed data
# ============================================================

# IESO demand imputation flags
demand_imputed = (
    df["Was_Imputed"]
    .astype("boolean")
    .fillna(False)
)

# Weather imputation flags
weather_imputed = (
    df["Weather_Was_Imputed"]
    .astype("boolean")
    .fillna(False)
)

# Check current and lagged demand observations,
# plus the next-hour target.
affected_demand = (
    demand_imputed
    | demand_imputed.shift(1, fill_value=False)
    | demand_imputed.shift(24, fill_value=False)
    | demand_imputed.shift(168, fill_value=False)
    | demand_imputed.shift(-1, fill_value=False)
)

# Exclude interpolated weather observations
affected_rows = affected_demand | weather_imputed

print("Rows affected by imputation:")
print(affected_rows.sum())

# ============================================================
# 5. Remove incomplete or affected observations
# ============================================================

model_df = df.loc[
    ~affected_rows,
    ["Date", "Target_Date", "DateTime_EST"] + features + [target]
].copy()

rows_before = len(model_df)

model_df = model_df.dropna(
    subset=features + [target]
)

print("\nRows removed due to missing values:")
print(rows_before - len(model_df))

# ============================================================
# 6. Chronological split
# ============================================================

train = model_df[
    model_df["Target_Date"].dt.year.between(2020, 2023)
].copy()

validation = model_df[
    model_df["Target_Date"].dt.year == 2024
].copy()

test = model_df[
    model_df["Target_Date"].dt.year == 2025
].copy()

print("\nTraining observations (2020-2023):")
print(len(train))

print("\nValidation observations (2024):")
print(len(validation))

print("\nTest observations (2025):")
print(len(test))

print("\nTotal usable observations:")
print(len(train) + len(validation) + len(test))

# ============================================================
# 7. Save datasets
# ============================================================

train.to_csv(
    DATA_DIR / "hourly_train.csv",
    index=False
)

validation.to_csv(
    DATA_DIR / "hourly_validation.csv",
    index=False
)

test.to_csv(
    DATA_DIR / "hourly_test.csv",
    index=False
)

print("\nHourly forecasting datasets saved.")

print("\nOriginal electricity imputation values:")
print(df["Was_Imputed"].value_counts(dropna=False))

print("\nOriginal weather imputation values:")
print(df["Weather_Was_Imputed"].value_counts(dropna=False))

print("\nConverted weather imputation values:")
print(weather_imputed.value_counts(dropna=False))


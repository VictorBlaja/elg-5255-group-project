
from pathlib import Path
import pandas as pd

# ============================================================
# 1. Directories
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
ECCC_DIR = BASE_DIR / "data" / "ECCC"
OUTPUT_DIR = BASE_DIR / "data" / "processed"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# 2. Find all monthly weather files
# ============================================================

files = sorted(
    ECCC_DIR.glob("en_climate_hourly_ON_6106001_*.csv")
)

print(f"Files found: {len(files)}")

if len(files) != 72:
    raise ValueError("Expected 72 monthly weather files.")

# ============================================================
# 3. Combine monthly datasets
# ============================================================

dataframes = []

for file in files:
    df = pd.read_csv(file, low_memory=False)

    dataframes.append(df)

weather = pd.concat(dataframes, ignore_index=True)

# ============================================================
# 4. Keep required columns
# ============================================================

weather = weather[
    [
        "Date/Time (LST)",
        "Temp (°C)"
    ]
].copy()

weather = weather.rename(
    columns={
        "Date/Time (LST)": "DateTime_LST",
        "Temp (°C)": "Temperature_C"
    }
)

# Convert data types
weather["DateTime_LST"] = pd.to_datetime(
    weather["DateTime_LST"]
)

weather["Temperature_C"] = pd.to_numeric(
    weather["Temperature_C"],
    errors="coerce"
)

# Sort chronologically
weather = weather.sort_values(
    "DateTime_LST"
).reset_index(drop=True)

# ============================================================
# 5. Check data quality
# ============================================================

print("\nDataset shape:")
print(weather.shape)

print("\nDate range:")
print(weather["DateTime_LST"].min())
print(weather["DateTime_LST"].max())

print("\nMissing values:")
print(weather.isna().sum())

print("\nDuplicate timestamps:")
print(weather.duplicated("DateTime_LST").sum())

print("\nTemperature statistics:")
print(weather["Temperature_C"].describe())

# ============================================================
# 6. Save combined weather dataset
# ============================================================

output_file = OUTPUT_DIR / "eccc_ottawa_hourly_2020_2025.csv"

weather.to_csv(output_file, index=False)

print(f"\nCombined weather dataset saved: {output_file}")

# ============================================================
# 6. Investigate missing temperature readings
# ============================================================

missing = weather[weather["Temperature_C"].isna()]

print("\nMissing temperature observations:")
print(missing.to_string(index=False))

# Check consecutive missing readings
missing_groups = weather["Temperature_C"].isna()

group_ids = (
    missing_groups != missing_groups.shift()
).cumsum()

missing_runs = (
    weather[missing_groups]
    .groupby(group_ids[missing_groups])
    .agg(
        Start=("DateTime_LST", "min"),
        End=("DateTime_LST", "max"),
        Hours=("DateTime_LST", "count")
    )
)

print("\nConsecutive missing-temperature periods:")
print(missing_runs.to_string(index=False))

# ============================================================
# 7. Fill missing temperature observations
# ============================================================

# Preserve information about original missing values
weather["Was_Imputed"] = weather["Temperature_C"].isna()

# Interpolate using surrounding hourly observations
weather["Temperature_C"] = weather["Temperature_C"].interpolate(
    method="linear",
    limit_direction="both"
)

# Verify results
print("\nTemperature observations imputed:")
print(weather["Was_Imputed"].sum())

print("\nRemaining missing temperatures:")
print(weather["Temperature_C"].isna().sum())

print("\nImputed temperature observations:")
print(
    weather.loc[
        weather["Was_Imputed"],
        ["DateTime_LST", "Temperature_C", "Was_Imputed"]
    ].to_string(index=False)
)

# ============================================================
# Save cleaned weather dataset
# ============================================================

output_file = OUTPUT_DIR / "eccc_ottawa_hourly_2020_2025.csv"

weather.to_csv(output_file, index=False)

print("\nColumns saved:")
print(weather.columns.tolist())

print(f"\nSaved: {output_file}")
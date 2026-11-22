from pathlib import Path
import pandas as pd

# Project directories
BASE_DIR = Path(__file__).resolve().parent
IESO_DIR = BASE_DIR / "data" / "IESO"

# Find all annual IESO CSV files
files = sorted(IESO_DIR.glob("PUB_DemandZonal_*.csv"))

if not files:
    raise FileNotFoundError(f"No IESO CSV files found in {IESO_DIR}")

# Load each file
dataframes = []

for file in files:
    df = pd.read_csv(file, skiprows=3)

    print(f"{file.name}: {len(df)} rows")

    dataframes.append(df)

# Combine all years
ieso = pd.concat(dataframes, ignore_index=True)

# Keep the columns needed for Ottawa forecasting
ieso = ieso[["Date", "Hour", "Ottawa"]].copy()

# Convert data types
ieso["Date"] = pd.to_datetime(ieso["Date"])
ieso["Hour"] = pd.to_numeric(ieso["Hour"])
ieso["Ottawa"] = pd.to_numeric(ieso["Ottawa"])

# Sort chronologically
ieso = ieso.sort_values(["Date", "Hour"]).reset_index(drop=True)

# Display results
print("\nCombined dataset:")
print(ieso.head())

print("\nLast observations:")
print(ieso.tail())

print("\nDataset shape:", ieso.shape)

print("\nMissing values:")
print(ieso.isna().sum())

print("\nDuplicate date-hour records:",
      ieso.duplicated(subset=["Date", "Hour"]).sum())

# Check expected hours for each day
daily_counts = (
    ieso.groupby("Date")["Hour"]
    .count()
    .reset_index(name="Hours")
)

print("\nDays without exactly 24 observations:")
print(daily_counts[daily_counts["Hours"] != 24])

# Identify missing date-hour combinations
expected = pd.MultiIndex.from_product(
    [
        pd.date_range("2020-01-01", "2025-12-31", freq="D"),
        range(1, 25)
    ],
    names=["Date", "Hour"]
)

actual = pd.MultiIndex.from_frame(ieso[["Date", "Hour"]])

date = pd.Timestamp("2025-05-01")

existing_hours = set(
    ieso.loc[ieso["Date"] == date, "Hour"]
)

missing_hours = sorted(set(range(1, 25)) - existing_hours)

print("Missing hours:", missing_hours)

print("\nAvailable observations:")
print(ieso.loc[ieso["Date"] == date].to_string(index=False))

# Create the complete expected date-hour index
expected = pd.MultiIndex.from_product(
    [
        pd.date_range("2020-01-01", "2025-12-31", freq="D"),
        range(1, 25)
    ],
    names=["Date", "Hour"]
)

# Reindex to restore missing rows
ieso = (
    ieso.set_index(["Date", "Hour"])
    .reindex(expected)
    .reset_index()
)

# Mark observations that were missing in the original data
ieso["Was_Imputed"] = ieso["Ottawa"].isna()

# Interpolate missing electricity demand
ieso["Ottawa"] = ieso["Ottawa"].interpolate(
    method="linear",
    limit=1
)

# Verify
print("\nDataset shape:", ieso.shape)

print("\nImputed observations:")
print(ieso[ieso["Was_Imputed"]])

print("\nRemaining missing values:")
print(ieso.isna().sum())

# Create a folder for processed datasets
PROCESSED_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Save the cleaned dataset
output_file = PROCESSED_DIR / "ieso_ottawa_2020_2025_clean.csv"

ieso.to_csv(output_file, index=False)

print(f"\nCleaned dataset saved to: {output_file}")
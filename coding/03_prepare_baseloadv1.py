from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = (
    BASE_DIR / "data" / "processed" /
    "ieso_ottawa_2020_2025_clean.csv"
)

df = pd.read_csv(INPUT_FILE, parse_dates=["Date"])

# Aggregate hourly demand into daily statistics
daily = (
    df.groupby("Date")
    .agg(
        Baseload=("Ottawa", "min"),
        Average_Demand=("Ottawa", "mean"),
        Maximum_Demand=("Ottawa", "max"),
        Was_Imputed=("Was_Imputed", "max")
    )
    .reset_index()
    .sort_values("Date")
    .reset_index(drop=True)
)

# Create next-day baseload prediction target
daily["Target_Next_Day_Baseload"] = daily["Baseload"].shift(-1)

# Create historical baseload features
daily["Baseload_d"] = daily["Baseload"]
daily["Baseload_d_minus_1"] = daily["Baseload"].shift(1)
daily["Baseload_d_minus_7"] = daily["Baseload"].shift(7)

print("\nDaily baseload dataset:")
print(daily.head(10).to_string(index=False))

print("\nDataset shape:", daily.shape)

print("\nMissing values:")
print(daily.isna().sum())

# Calendar date of the prediction target
daily["Target_Date"] = daily["Date"] + pd.Timedelta(days=1)

# Next-day calendar features
daily["DayOfWeek"] = daily["Target_Date"].dt.dayofweek
daily["Month"] = daily["Target_Date"].dt.month
daily["IsWeekend"] = (daily["DayOfWeek"] >= 5).astype(int)

# Display results
print("\nNext-day calendar features:")
print(
    daily[
        [
            "Date",
            "Baseload",
            "Target_Date",
            "Target_Next_Day_Baseload",
            "DayOfWeek",
            "Month",
            "IsWeekend"
        ]
    ].head(10).to_string(index=False)
)



OUTPUT_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

output_file = OUTPUT_DIR / "ieso_ottawa_daily_baseload.csv"

daily.to_csv(output_file, index=False)

print(f"\nDaily baseload dataset saved: {output_file}")
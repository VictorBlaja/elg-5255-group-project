from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "data" / "processed" / "ieso_ottawa_2020_2025_clean.csv"

df = pd.read_csv(INPUT_FILE, parse_dates=["Date"])

# Ensure chronological order
df = df.sort_values(["Date", "Hour"]).reset_index(drop=True)

# Create the target: electricity demand in the next hour
df["Target_Next_Hour"] = df["Ottawa"].shift(-1)

print(df[["Date", "Hour", "Ottawa", "Target_Next_Hour"]].head(10))

print("\nMissing target values:")
print(df["Target_Next_Hour"].isna().sum())

# Create lagged electricity-demand features
df["Demand_t"] = df["Ottawa"]
df["Demand_t_minus_1"] = df["Ottawa"].shift(1)
df["Demand_t_minus_24"] = df["Ottawa"].shift(24)
df["Demand_t_minus_168"] = df["Ottawa"].shift(168)

# Display results
print("\nLagged demand features:")
print(
    df[
        [
            "Date",
            "Hour",
            "Demand_t",
            "Demand_t_minus_1",
            "Demand_t_minus_24",
            "Demand_t_minus_168",
            "Target_Next_Hour"
        ]
    ].iloc[168:178].to_string(index=False)
)

print("\nMissing values:")
print(
    df[
        [
            "Demand_t",
            "Demand_t_minus_1",
            "Demand_t_minus_24",
            "Demand_t_minus_168",
            "Target_Next_Hour"
        ]
    ].isna().sum()
)




# Calendar features for the next-hour forecast

# Hour is numbered 1–24 in the IESO dataset
df["Target_Hour"] = (df["Hour"] % 24) + 1

# Date corresponding to the predicted hour
df["Target_Date"] = df["Date"] + pd.to_timedelta(
    (df["Hour"] == 24).astype(int),
    unit="D"
)

# Calendar features of the hour being predicted
df["DayOfWeek"] = df["Target_Date"].dt.dayofweek
df["Month"] = df["Target_Date"].dt.month
df["IsWeekend"] = (df["DayOfWeek"] >= 5).astype(int)

print("\nCalendar features:")
print(
    df[
        [
            "Date",
            "Hour",
            "Target_Date",
            "Target_Hour",
            "DayOfWeek",
            "Month",
            "IsWeekend"
        ]
    ].head(26).to_string(index=False)
)

OUTPUT_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

output_file = OUTPUT_DIR / "ieso_ottawa_hourly_features.csv"

df.to_csv(output_file, index=False)

print(f"\nHourly dataset saved: {output_file}")
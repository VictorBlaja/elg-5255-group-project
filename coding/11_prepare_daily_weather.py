
from pathlib import Path
import pandas as pd

# ============================================================
# 1. File paths
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "processed"

weather_file = DATA_DIR / "eccc_ottawa_hourly_2020_2025.csv"
output_file = DATA_DIR / "eccc_ottawa_daily_2020_2025.csv"

# ============================================================
# 2. Load hourly weather
# ============================================================

weather = pd.read_csv(weather_file)

weather["DateTime_LST"] = pd.to_datetime(
    weather["DateTime_LST"]
)

weather["Date"] = weather["DateTime_LST"].dt.normalize()

# ============================================================
# 3. Aggregate hourly temperature by day
# ============================================================

daily_weather = (
    weather.groupby("Date")
    .agg(
        Temperature_Mean_C=("Temperature_C", "mean"),
        Temperature_Min_C=("Temperature_C", "min"),
        Temperature_Max_C=("Temperature_C", "max"),
        Hourly_Observations=("Temperature_C", "count"),
        Imputed_Hours=("Was_Imputed", "sum")
    )
    .reset_index()
)

# ============================================================
# 4. Check daily coverage
# ============================================================

print("\nDAILY WEATHER SUMMARY")
print("=" * 50)

print(f"Total days: {len(daily_weather)}")

print(
    "Date range:",
    daily_weather["Date"].min(),
    "to",
    daily_weather["Date"].max()
)

incomplete = daily_weather[
    daily_weather["Hourly_Observations"] != 24
]

print(f"Days without 24 observations: {len(incomplete)}")

print("\nFirst 5 days:")
print(daily_weather.head().to_string(index=False))

print("\nLast 5 days:")
print(daily_weather.tail().to_string(index=False))

# ============================================================
# 5. Save
# ============================================================

daily_weather.to_csv(output_file, index=False)

print("\nSaved to:")
print(output_file)

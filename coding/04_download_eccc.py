
from pathlib import Path
import requests
import pandas as pd
import time

# ============================================================
# 1. Project directories
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
ECCC_DIR = BASE_DIR / "data" / "ECCC"

ECCC_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# 2. ECCC station configuration
# ============================================================

CLIMATE_ID = "6106001"
BASE_URL = "https://climate.weather.gc.ca/climate_data/bulk_data_e.html"

START_YEAR = 2020
END_YEAR = 2025

session = requests.Session()

# ============================================================
# 3. Download monthly hourly weather data
# ============================================================

downloaded = 0
skipped = 0
failed = []

for year in range(START_YEAR, END_YEAR + 1):

    for month in range(1, 13):

        filename = (
            f"en_climate_hourly_ON_{CLIMATE_ID}_"
            f"{month:02d}-{year}_P1H.csv"
        )

        output_file = ECCC_DIR / filename

        # Skip files already downloaded
        if output_file.exists():
            print(f"Already exists: {filename}")
            skipped += 1
            continue

        params = {
            "format": "csv",
            "climate_id": CLIMATE_ID,
            "Year": year,
            "Month": month,
            "Day": 1,
            "time": "LST",
            "timeframe": 1,
            "submit": "Download Data"
        }

        try:
            response = session.get(
                BASE_URL,
                params=params,
                timeout=60
            )

            response.raise_for_status()

            # Validate the downloaded CSV
            from io import BytesIO

            test_df = pd.read_csv(BytesIO(response.content))

            required_columns = [
                "Climate ID",
                "Date/Time (LST)",
                "Temp (°C)"
            ]

            if not all(
                col in test_df.columns
                for col in required_columns
            ):
                raise ValueError("Unexpected CSV format")

            if test_df.empty:
                raise ValueError("Downloaded CSV is empty")

            if not (
                test_df["Climate ID"].astype(str) == CLIMATE_ID
            ).all():
                raise ValueError("Climate ID mismatch")

            # Save validated file
            output_file.write_bytes(response.content)

            downloaded += 1
            print(f"Downloaded: {filename} ({len(test_df)} rows)")

            # Avoid sending requests too quickly
            time.sleep(0.5)

        except Exception as error:
            print(f"FAILED: {filename} — {error}")
            failed.append(filename)

# ============================================================
# 4. Download summary
# ============================================================

print("\n========================================")
print("ECCC DOWNLOAD SUMMARY")
print("========================================")

print(f"Downloaded: {downloaded}")
print(f"Skipped existing files: {skipped}")
print(f"Failed: {len(failed)}")

if failed:
    print("\nFailed files:")
    for filename in failed:
        print(filename)

print(f"\nData directory: {ECCC_DIR}")
print("\nDownload process completed.")

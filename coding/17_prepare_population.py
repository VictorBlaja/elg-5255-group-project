
from pathlib import Path
import pandas as pd

# ============================================================
# 1. File paths
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "processed"

population_file = DATA_DIR / "ottawa_ontario_population_2020_2025.csv"

# ============================================================
# 2. Load population
# ============================================================

population = pd.read_csv(population_file)

print("\nPOPULATION DATA")
print("=" * 50)
print(population.to_string(index=False))

assert {"Year", "Population"}.issubset(population.columns)

population["Year"] = population["Year"].astype(int)
population["Population"] = pd.to_numeric(
    population["Population"]
)

assert population["Year"].is_unique

# ============================================================
# 3. Merge into hourly and daily datasets
# ============================================================

datasets = [
    "hourly_train",
    "hourly_validation",
    "hourly_test",
    "daily_train",
    "daily_validation",
    "daily_test"
]

for dataset_name in datasets:

    df = pd.read_csv(
        DATA_DIR / f"{dataset_name}.csv"
    )

    # Use the year of the prediction target
    df["Year"] = pd.to_datetime(
        df["Target_Date"]
    ).dt.year

    merged = df.merge(
        population[["Year", "Population"]],
        on="Year",
        how="left",
        validate="many_to_one"
    )

    missing = merged["Population"].isna().sum()

    if missing:
        raise ValueError(
            f"{dataset_name}: {missing} rows "
            "have missing population values."
        )

    output_file = (
        DATA_DIR / f"{dataset_name}_population.csv"
    )

    merged.to_csv(output_file, index=False)

    print(
        f"{dataset_name}: "
        f"{len(merged)} rows, "
        f"{missing} missing population values"
    )

print("\nAll population datasets saved successfully.")


from pathlib import Path
import pandas as pd
import numpy as np

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

# ============================================================
# 1. Configuration
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "processed"

TASKS = {
    "Hourly": {
        "features": [
            "Demand_t",
            "Demand_t_minus_1",
            "Demand_t_minus_24",
            "Demand_t_minus_168",
            "Temperature_C",
            "Target_Hour",
            "DayOfWeek",
            "Month",
            "IsWeekend"
        ],
        "target": "Target_Next_Hour",
        "baseline": "Demand_t"
    },

    "Daily": {
        "features": [
            "Baseload_d",
            "Baseload_d_minus_1",
            "Baseload_d_minus_7",
            "Temperature_Mean_C",
            "Temperature_Min_C",
            "Temperature_Max_C",
            "DayOfWeek",
            "Month",
            "IsWeekend"
        ],
        "target": "Target_Next_Day_Baseload",
        "baseline": "Baseload_d"
    }
}

# ============================================================
# 2. Evaluation metrics
# ============================================================

def calculate_metrics(actual, predicted):

    mae = mean_absolute_error(actual, predicted)
    rmse = np.sqrt(
        mean_squared_error(actual, predicted)
    )
    r2 = r2_score(actual, predicted)

    nmae = mae / np.mean(actual) * 100

    return {
        "MAE_MW": mae,
        "RMSE_MW": rmse,
        "R2": r2,
        "NMAE_Percent": nmae
    }

# ============================================================
# 3. Evaluate models
# ============================================================

all_results = []

for task_name, config in TASKS.items():

    prefix = task_name.lower()

    train = pd.read_csv(
        DATA_DIR / f"{prefix}_train_population.csv"
    )

    validation = pd.read_csv(
        DATA_DIR / f"{prefix}_validation_population.csv"
    )

    test = pd.read_csv(
        DATA_DIR / f"{prefix}_test_population.csv"
    )

    target = config["target"]

    for population_option in ["Without", "With"]:

        features = config["features"].copy()

        if population_option == "With":
            features.append("Population")

        # Train models only on 2020-2023
        models = {
            "Linear Regression": LinearRegression(),

            "Random Forest": RandomForestRegressor(
                n_estimators=100,
                max_depth=15,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
        }

        for model in models.values():
            model.fit(train[features], train[target])

        # Evaluate both 2024 and 2025
        for period_name, dataset in [
            ("2024 Validation", validation),
            ("2025 Test", test)
        ]:

            actual = dataset[target]

            predictions = {
                "Persistence Baseline":
                    dataset[config["baseline"]],

                "Linear Regression":
                    models["Linear Regression"].predict(
                        dataset[features]
                    ),

                "Random Forest":
                    models["Random Forest"].predict(
                        dataset[features]
                    )
            }

            for model_name, predicted in predictions.items():

                metrics = calculate_metrics(
                    actual,
                    predicted
                )

                all_results.append({
                    "Task": task_name,
                    "Period": period_name,
                    "Population": population_option,
                    "Model": model_name,
                    "Observations": len(dataset),
                    **metrics
                })

# ============================================================
# 4. Display results
# ============================================================

results_df = pd.DataFrame(all_results)

for task_name in TASKS:

    for period in ["2024 Validation", "2025 Test"]:

        print("\n" + "=" * 90)
        print(f"{task_name.upper()} — {period.upper()}")
        print("=" * 90)

        subset = results_df[
            (results_df["Task"] == task_name) &
            (results_df["Period"] == period)
        ]

        print(
            subset[
                [
                    "Population",
                    "Model",
                    "Observations",
                    "MAE_MW",
                    "RMSE_MW",
                    "R2",
                    "NMAE_Percent"
                ]
            ].round(4).to_string(index=False)
        )

# ============================================================
# 5. Save all results
# ============================================================

output_file = DATA_DIR / "complete_model_comparison.csv"

results_df.to_csv(output_file, index=False)

print("\n" + "=" * 90)
print("All 24 comparisons completed successfully.")
print(f"Results saved to: {output_file}")

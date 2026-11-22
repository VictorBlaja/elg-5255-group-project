
from pathlib import Path
import pandas as pd
import numpy as np

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "processed"

train = pd.read_csv(DATA_DIR / "hourly_train_population.csv")
validation = pd.read_csv(DATA_DIR / "hourly_validation_population.csv")

base_features = [
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

def evaluate(name, model, features):
    model.fit(train[features], train[target])
    predicted = model.predict(validation[features])
    actual = validation[target]

    mae = mean_absolute_error(actual, predicted)
    rmse = np.sqrt(mean_squared_error(actual, predicted))
    r2 = r2_score(actual, predicted)
    nmae = mae / actual.mean() * 100

    return {
        "Model": name,
        "MAE_MW": mae,
        "RMSE_MW": rmse,
        "R2": r2,
        "NMAE_Percent": nmae
    }

results = []

for use_population in [False, True]:

    features = base_features.copy()

    if use_population:
        features.append("Population")

    label = "With Population" if use_population else "Without Population"

    results.append(
        evaluate(
            f"Linear Regression — {label}",
            LinearRegression(),
            features
        )
    )

    results.append(
        evaluate(
            f"Random Forest — {label}",
            RandomForestRegressor(
                n_estimators=100,
                max_depth=15,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            ),
            features
        )
    )

results_df = pd.DataFrame(results)

print("\n2024 HOURLY VALIDATION — POPULATION COMPARISON")
print("=" * 65)
print(results_df.round(4).to_string(index=False))

results_df.to_csv(
    DATA_DIR / "hourly_population_comparison.csv",
    index=False
)

print("\nResults saved successfully.")

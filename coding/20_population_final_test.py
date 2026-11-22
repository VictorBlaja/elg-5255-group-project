
from pathlib import Path
import pandas as pd
import numpy as np

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "processed"

hourly_features = [
    "Demand_t", "Demand_t_minus_1",
    "Demand_t_minus_24", "Demand_t_minus_168",
    "Temperature_C", "Target_Hour",
    "DayOfWeek", "Month", "IsWeekend"
]

daily_features = [
    "Baseload_d", "Baseload_d_minus_1",
    "Baseload_d_minus_7", "Temperature_Mean_C",
    "Temperature_Min_C", "Temperature_Max_C",
    "DayOfWeek", "Month", "IsWeekend"
]

def evaluate_dataset(name, features, target):

    train = pd.read_csv(
        DATA_DIR / f"{name}_train_population.csv"
    )
    test = pd.read_csv(
        DATA_DIR / f"{name}_test_population.csv"
    )

    results = []

    for use_population in [False, True]:

        selected = features.copy()

        if use_population:
            selected.append("Population")

        for model_name, model in [
            ("Linear Regression", LinearRegression()),
            ("Random Forest", RandomForestRegressor(
                n_estimators=100,
                max_depth=15,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            ))
        ]:

            model.fit(train[selected], train[target])
            predicted = model.predict(test[selected])
            actual = test[target]

            mae = mean_absolute_error(actual, predicted)
            rmse = np.sqrt(
                mean_squared_error(actual, predicted)
            )

            results.append({
                "Task": name,
                "Model": model_name,
                "Population": (
                    "With" if use_population else "Without"
                ),
                "MAE_MW": mae,
                "RMSE_MW": rmse,
                "R2": r2_score(actual, predicted),
                "NMAE_Percent": mae / actual.mean() * 100
            })

    return results


results = []

results += evaluate_dataset(
    "hourly",
    hourly_features,
    "Target_Next_Hour"
)

results += evaluate_dataset(
    "daily",
    daily_features,
    "Target_Next_Day_Baseload"
)

results_df = pd.DataFrame(results)

for task in ["hourly", "daily"]:
    print(f"\n2025 {task.upper()} FINAL TEST")
    print("=" * 75)
    print(
        results_df[results_df["Task"] == task]
        .round(4)
        .to_string(index=False)
    )

results_df.to_csv(
    DATA_DIR / "population_final_test_results.csv",
    index=False
)

print("\nResults saved successfully.")

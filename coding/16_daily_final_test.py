
from pathlib import Path
import pandas as pd
import numpy as np

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "processed"

train = pd.read_csv(DATA_DIR / "daily_train.csv")
test = pd.read_csv(DATA_DIR / "daily_test.csv")

features = [
    "Baseload_d",
    "Baseload_d_minus_1",
    "Baseload_d_minus_7",
    "Temperature_Mean_C",
    "Temperature_Min_C",
    "Temperature_Max_C",
    "DayOfWeek",
    "Month",
    "IsWeekend"
]

target = "Target_Next_Day_Baseload"

X_train = train[features]
y_train = train[target]

X_test = test[features]
y_test = test[target]

# Train models
linear_model = LinearRegression()
linear_model.fit(X_train, y_train)

forest_model = RandomForestRegressor(
    n_estimators=100,
    max_depth=15,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)
forest_model.fit(X_train, y_train)

predictions = {
    "Persistence": test["Baseload_d"].to_numpy(),
    "Linear Regression": linear_model.predict(X_test),
    "Random Forest": forest_model.predict(X_test)
}

# Evaluate
results = []

print("\nFINAL NEXT-DAY BASELOAD TEST — 2025")
print("=" * 55)
print(f"Test observations: {len(test)}")
print(f"Mean actual baseload: {y_test.mean():.2f} MW")

for name, predicted in predictions.items():
    mae = mean_absolute_error(y_test, predicted)
    rmse = np.sqrt(mean_squared_error(y_test, predicted))
    r2 = r2_score(y_test, predicted)
    nmae = mae / y_test.mean() * 100

    results.append({
        "Model": name,
        "MAE_MW": mae,
        "RMSE_MW": rmse,
        "R2": r2,
        "NMAE_Percent": nmae
    })

    print(f"\n{name}")
    print(f"MAE:  {mae:.2f} MW")
    print(f"RMSE: {rmse:.2f} MW")
    print(f"R²:   {r2:.4f}")
    print(f"NMAE: {nmae:.2f}%")

results_df = pd.DataFrame(results)

results_df.to_csv(
    DATA_DIR / "daily_final_test_results.csv",
    index=False
)

print("\nComparison:")
print(results_df.round(4).to_string(index=False))

print("\nResults saved successfully.")


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
# 1. Load datasets
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "processed"

train = pd.read_csv(DATA_DIR / "hourly_train.csv")
test = pd.read_csv(DATA_DIR / "hourly_test.csv")

# ============================================================
# 2. Select features and target
# ============================================================

features = [
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

X_train = train[features]
y_train = train[target]

X_test = test[features]
y_test = test[target]

# ============================================================
# 3. Train Linear Regression
# ============================================================

linear_model = LinearRegression()
linear_model.fit(X_train, y_train)

linear_predictions = linear_model.predict(X_test)

# ============================================================
# 4. Train Random Forest
# ============================================================

forest_model = RandomForestRegressor(
    n_estimators=100,
    max_depth=15,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)

forest_model.fit(X_train, y_train)

forest_predictions = forest_model.predict(X_test)

# ============================================================
# 5. Persistence baseline
# ============================================================

baseline_predictions = test["Demand_t"].to_numpy()

# ============================================================
# 6. Evaluate all models
# ============================================================

def evaluate_model(name, actual, predicted):

    mae = mean_absolute_error(actual, predicted)
    rmse = np.sqrt(mean_squared_error(actual, predicted))
    r2 = r2_score(actual, predicted)

    print(f"\n{name}")
    print("-" * 35)
    print(f"MAE:  {mae:.2f} MW")
    print(f"RMSE: {rmse:.2f} MW")
    print(f"R²:   {r2:.4f}")

    return {
        "Model": name,
        "MAE_MW": mae,
        "RMSE_MW": rmse,
        "R2": r2
    }


print("\nFINAL TEST RESULTS — 2025")
print("=" * 45)

results = []

results.append(
    evaluate_model(
        "Persistence Baseline",
        y_test,
        baseline_predictions
    )
)

results.append(
    evaluate_model(
        "Linear Regression",
        y_test,
        linear_predictions
    )
)

results.append(
    evaluate_model(
        "Random Forest",
        y_test,
        forest_predictions
    )
)

# ============================================================
# 7. Save results
# ============================================================

results_df = pd.DataFrame(results)

results_df.to_csv(
    DATA_DIR / "hourly_final_test_results.csv",
    index=False
)

print("\nComparison:")
print(results_df.round(4).to_string(index=False))

print("\nFinal test results saved.")


mean_demand = y_test.mean()

print(f"\nMean actual demand: {mean_demand:.2f} MW")

for result in results:
    percent_mae = result["MAE_MW"] / mean_demand * 100
    print(f"{result['Model']}: {percent_mae:.2f}%")

print("\nChecking next-hour target alignment")
print("-" * 50)

columns = [
    "Demand_t",
    "Target_Next_Hour"
]

print(test[columns].head(10).to_string(index=False))

print("\nChecking target against next row's demand:")

check = test[columns].head(10).copy()
check["Next_Row_Demand"] = test["Demand_t"].shift(-1).head(10)

print(check.to_string(index=False))

print("\nChecking hourly feature alignment")
print("-" * 60)

columns = [
    "Demand_t",
    "Demand_t_minus_1",
    "Demand_t_minus_24",
    "Demand_t_minus_168",
    "Target_Hour",
    "Target_Next_Hour"
]

print(test[columns].head(10).to_string(index=False))

print("\nChecking midnight transitions:")
print(
    test.loc[
        test["Target_Hour"] == 1,
        columns
    ].head(10).to_string(index=False)
)

print("\nChecking all lag values against original data")
print("-" * 55)

original = pd.read_csv(
    DATA_DIR / "ieso_eccc_ottawa_merged.csv",
    low_memory=False
)

original["Date"] = pd.to_datetime(original["Date"])
original["DateTime"] = (
    original["Date"]
    + pd.to_timedelta(original["Hour"], unit="h")
)

test_check = test.copy()
test_check["DateTime"] = pd.to_datetime(test_check["DateTime_EST"])

original_demand = original.set_index("DateTime")["Ottawa"]

for lag in [1, 24, 168]:
    expected = test_check["DateTime"].map(
        original_demand.shift(lag)
    )

    actual = test_check[f"Demand_t_minus_{lag}"]

    matches = np.isclose(
        actual,
        expected,
        equal_nan=True
    )

    print(
        f"{lag}-hour lag: "
        f"{matches.sum()} / {len(matches)} correct"
    )
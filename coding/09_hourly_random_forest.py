
from pathlib import Path
import pandas as pd
import numpy as np

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
validation = pd.read_csv(DATA_DIR / "hourly_validation.csv")

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

X_validation = validation[features]
y_validation = validation[target]

# ============================================================
# 3. Train Random Forest
# ============================================================

model = RandomForestRegressor(
    n_estimators=100,
    max_depth=15,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

# ============================================================
# 4. Validate model
# ============================================================

predictions = model.predict(X_validation)

mae = mean_absolute_error(y_validation, predictions)
rmse = np.sqrt(mean_squared_error(y_validation, predictions))
r2 = r2_score(y_validation, predictions)

print("\nRANDOM FOREST — VALIDATION (2024)")
print("=================================")
print(f"MAE:  {mae:.2f} MW")
print(f"RMSE: {rmse:.2f} MW")
print(f"R²:   {r2:.4f}")

# ============================================================
# 5. Feature importance
# ============================================================

importance = pd.DataFrame({
    "Feature": features,
    "Importance": model.feature_importances_
})

importance = importance.sort_values(
    "Importance",
    ascending=False
)

print("\nFeature importance:")
print(importance.to_string(index=False))

# ============================================================
# 6. Persistence baseline
# ============================================================

baseline_predictions = validation["Demand_t"]

baseline_mae = mean_absolute_error(
    y_validation, baseline_predictions
)

baseline_rmse = np.sqrt(
    mean_squared_error(y_validation, baseline_predictions)
)

baseline_r2 = r2_score(
    y_validation, baseline_predictions
)

print("\nPERSISTENCE BASELINE — VALIDATION (2024)")
print("========================================")
print(f"MAE:  {baseline_mae:.2f} MW")
print(f"RMSE: {baseline_rmse:.2f} MW")
print(f"R²:   {baseline_r2:.4f}")



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

train = pd.read_csv(DATA_DIR / "daily_train.csv")
validation = pd.read_csv(DATA_DIR / "daily_validation.csv")

# ============================================================
# 2. Select features and target
# ============================================================

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

X_val = validation[features]
y_val = validation[target]

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

predictions = model.predict(X_val)

# ============================================================
# 4. Evaluate Random Forest
# ============================================================

mae = mean_absolute_error(y_val, predictions)
rmse = np.sqrt(mean_squared_error(y_val, predictions))
r2 = r2_score(y_val, predictions)

nmae = mae / y_val.mean() * 100

print("\nNEXT-DAY BASELOAD — RANDOM FOREST")
print("=" * 50)

print(f"Validation observations: {len(validation)}")
print(f"\nMAE:  {mae:.2f} MW")
print(f"RMSE: {rmse:.2f} MW")
print(f"R²:   {r2:.4f}")
print(f"NMAE: {nmae:.2f}%")

# ============================================================
# 5. Feature importance
# ============================================================

importance = pd.DataFrame({
    "Feature": features,
    "Importance": model.feature_importances_
}).sort_values("Importance", ascending=False)

print("\nFEATURE IMPORTANCE")
print("-" * 50)
print(importance.to_string(index=False))

# ============================================================
# 6. Persistence baseline
# ============================================================

baseline_predictions = validation["Baseload_d"]

baseline_mae = mean_absolute_error(
    y_val, baseline_predictions
)

baseline_rmse = np.sqrt(
    mean_squared_error(y_val, baseline_predictions)
)

baseline_r2 = r2_score(
    y_val, baseline_predictions
)

baseline_nmae = baseline_mae / y_val.mean() * 100

print("\nPERSISTENCE BASELINE")
print("=" * 50)

print(f"MAE:  {baseline_mae:.2f} MW")
print(f"RMSE: {baseline_rmse:.2f} MW")
print(f"R²:   {baseline_r2:.4f}")
print(f"NMAE: {baseline_nmae:.2f}%")


from pathlib import Path
import pandas as pd
import numpy as np

from sklearn.linear_model import LinearRegression
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
# 3. Train Linear Regression
# ============================================================

model = LinearRegression()
model.fit(X_train, y_train)

predictions = model.predict(X_val)

# ============================================================
# 4. Evaluate
# ============================================================

mae = mean_absolute_error(y_val, predictions)
rmse = np.sqrt(mean_squared_error(y_val, predictions))
r2 = r2_score(y_val, predictions)

mean_baseload = y_val.mean()
nmae = mae / mean_baseload * 100

print("\nNEXT-DAY BASELOAD — LINEAR REGRESSION")
print("=" * 50)

print(f"Validation observations: {len(validation)}")
print(f"Mean actual baseload: {mean_baseload:.2f} MW")

print(f"\nMAE:  {mae:.2f} MW")
print(f"RMSE: {rmse:.2f} MW")
print(f"R²:   {r2:.4f}")
print(f"NMAE: {nmae:.2f}%")

# ============================================================
# 5. Model coefficients
# ============================================================

print("\nMODEL COEFFICIENTS")
print("-" * 50)

for feature, coefficient in zip(
    features, model.coef_
):
    print(f"{feature:25s}: {coefficient:.6f}")

print(f"\nIntercept: {model.intercept_:.2f}")

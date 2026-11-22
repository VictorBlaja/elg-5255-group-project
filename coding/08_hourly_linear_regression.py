
from pathlib import Path
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np

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
# 3. Train Linear Regression
# ============================================================

model = LinearRegression()
model.fit(X_train, y_train)

# ============================================================
# 4. Validate model
# ============================================================

predictions = model.predict(X_validation)

mae = mean_absolute_error(y_validation, predictions)
rmse = np.sqrt(mean_squared_error(y_validation, predictions))
r2 = r2_score(y_validation, predictions)

print("\nLINEAR REGRESSION — VALIDATION (2024)")
print("====================================")
print(f"MAE:  {mae:.2f} MW")
print(f"RMSE: {rmse:.2f} MW")
print(f"R²:   {r2:.4f}")

# ============================================================
# 5. Inspect coefficients
# ============================================================

coefficients = pd.DataFrame({
    "Feature": features,
    "Coefficient": model.coef_
})

print("\nModel coefficients:")
print(coefficients.to_string(index=False))

print(f"\nIntercept: {model.intercept_:.2f}")

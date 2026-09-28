import pandas as pd
import sklearn as sk

data = {
    "year": [
        2010, 2011, 2012, 2013,
        2014, 2015, 2016, 2017,
        2018, 2019, 2020, 2021,
        2022, 2023, 2024, 2025
    ],

    "population": [
        890000, 905000, 920000, 935000,
        950000, 965000, 985000, 1000000,
        1020000, 1040000, 1060000, 1080000,
        1100000, 1120000, 1145000, 1170000
    ],

    "temperature": [
        6.2, 6.5, 7.1, 6.4,
        6.0, 7.3, 7.0, 6.8,
        7.4, 7.0, 7.6, 7.2,
        7.8, 8.0, 7.7, 8.1
    ],

    "data_centers": [
        2, 2, 3, 3,
        3, 4, 4, 5,
        5, 6, 7, 8,
        9, 10, 11, 12
    ],

    "energy_consumption": [
        7400, 7520, 7710, 7760,
        7830, 8050, 8180, 8340,
        8510, 8720, 8910, 9120,
        9360, 9610, 9850, 10120
    ]
}

df = pd.DataFrame(data)

print(df)

X = df[
    ["population", "temperature", "data_centers"]
]

y = df["energy_consumption"]

print(X)
print(y)

from sklearn.linear_model import LinearRegression

model = LinearRegression()

model.fit(X, y)

print("Intercept:", model.intercept_)
print("Weights:", model.coef_)

future = pd.DataFrame({
    "population": [1220000],
    "temperature": [8.3],
    "data_centers": [15]
})
prediction = model.predict(future)

print("Predicted consumption:", prediction[0], "GWh")
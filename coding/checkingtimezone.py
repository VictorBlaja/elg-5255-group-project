

from pathlib import Path
import pandas as pd

# Project directories
BASE_DIR = Path(__file__).resolve().parent
IESO_DIR = BASE_DIR / "data" / "IESO"

file_path = IESO_DIR / "PUB_DemandZonal_2020(1).csv"

with open(file_path, "r", encoding="utf-8-sig") as file:
    for _ in range(3):
        print(file.readline().strip())
        
from pathlib import Path
import pandas as pd

base_dir = Path(__file__).resolve().parent
file_path = base_dir / "data" / "IESO" / "PUB_DemandZonal_2020(1).csv"

df = pd.read_csv(file_path, skiprows=3)

for date in ["2020-03-08", "2020-11-01"]:
    print(f"\n{date}")
    print(
        df.loc[df["Date"] == date, ["Date", "Hour", "Ottawa"]]
        .to_string(index=False)
    )
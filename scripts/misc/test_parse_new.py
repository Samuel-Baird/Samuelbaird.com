import csv
import json
import pandas as pd
import pathlib

funny = pathlib.Path(r"D:\latter-day-stats-data\funny")

def check_csv(file, country_col, val_col):
    res = {}
    with open(file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            c = row.get(country_col)
            if c:
                val = row.get(val_col, "")
                if val.strip():  # Only take non-empty values
                    res[c] = val
    print(f"{file.name}: {len(res)} countries. Example USA: {res.get('United States')}")

def check_json(file):
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if isinstance(data, list):
        print(f"{file.name}: List of {len(data)}. Example 0: {data[0]}")
    elif isinstance(data, dict):
        print(f"{file.name}: Dict of keys {list(data.keys())[:5]}")
        first_key = list(data.keys())[0]
        print(f"Example key 0: {data[first_key][:2] if isinstance(data[first_key], list) else data[first_key]}")

print("--- Debt ---")
check_csv(funny / "debt data.csv", "REF_AREA_LABEL", "OBS_VALUE")

print("--- Gender & CO2 JSON ---")
check_json(funny / "gender data.json")
check_json(funny / "co2 data.json")

print("--- Gender Equality CSV ---")
check_csv(funny / "gender and minority equality.csv", "REF_AREA_LABEL", "OBS_VALUE")

print("--- Forest CSV ---")
check_csv(funny / "FAO_GFRA.csv", "REF_AREA_LABEL", "OBS_VALUE")

print("--- Nuclear ---")
try:
    df = pd.read_excel(funny / "nuclear reactor data.xlsx")
    print(df.head())
    print("Columns:", df.columns)
except Exception as e:
    print("Error reading excel:", e)

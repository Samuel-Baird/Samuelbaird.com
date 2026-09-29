"""Builds docs/datasets/lds-units-by-country/country-stats.json from countries.csv.

Every numeric column for every country, for the Map Explorer tool.
Run from the repo root: python scripts/church-facts-statistics/build_country_stats.py
"""
import csv
import json

FIELDS = ["membership", "congregations", "wards", "branches", "stakes",
          "districts", "missions", "temples", "family_history_centers"]

rows = list(csv.DictReader(open("scripts/church-facts-statistics/countries.csv", encoding="utf-8")))
as_int = lambda v: int(v) if v else 0
countries = {}
for r in rows:
    if not r["year"]:
        continue  # source page returned another country's record
    countries[r["country"]] = {
        "continent": r["continent"],
        "year": int(r["year"]),
        **{("members" if f == "membership" else f): as_int(r[f]) for f in FIELDS},
        "source_url": r["url"],
    }
out = {"as_of": "2025 (per-country data year in each row)", "countries": countries}
with open("docs/datasets/lds-units-by-country/country-stats.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1)
print(len(countries), "countries")

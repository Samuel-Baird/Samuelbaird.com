"""Builds docs/datasets/lds-states/state-stats.json from states.csv (scrape-subnational.mjs).

Run from the repo root: python scripts/church-facts-statistics/build_state_stats.py
"""
import csv
import json
import os

rows = list(csv.DictReader(open("scripts/church-facts-statistics/states.csv", encoding="utf-8")))
as_int = lambda v: int(v) if v else 0  # blank means zero (or unreported) in the source
out = {}
for r in rows:
    out.setdefault(r["country"], {})[r["state"]] = {
        "capital": r["capital"],
        "year": int(r["year"]) if r["year"] else None,
        "members": as_int(r["membership"]),
        "congregations": as_int(r["congregations"]),
        "wards": as_int(r["wards"]),
        "branches": as_int(r["branches"]),
        "stakes": as_int(r["stakes"]),
        "districts": as_int(r["districts"]),
        "missions": as_int(r["missions"]),
        "temples": as_int(r["temples"]),
        "source_url": r["url"],
    }
os.makedirs("docs/datasets/lds-states", exist_ok=True)
with open("docs/datasets/lds-states/state-stats.json", "w", encoding="utf-8") as f:
    json.dump(
        {
            "note": "State/province records from states.csv. The Church publishes these page by page, so most states are absent; blank counts in the source are zero.",
            "countries": out,
        },
        f,
        indent=1,
    )
print({c: len(s) for c, s in out.items()})

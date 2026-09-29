"""Builds docs/datasets/lds-states/state-stats.json: the U.S. states and Canada's provinces.

Sources:
  newsroom-states.csv (scrape-newsroom.mjs) has all 50 states and D.C., including family
    history centers. Preferred.
  states.csv (scrape-subnational.mjs, from churchofjesuschrist.org/learn) adds each
    state's capital, and covers any state the Newsroom page couldn't be read for
    (Hawaii has a different page layout there).

  newsroom-provinces.csv (scrape-newsroom.mjs, from the Canadian Newsroom) has Canada's
    provinces and territories. Nunavut has no figures of its own.

Blank counts in the sources mean zero.
Run from the repo root: python scripts/church-facts-statistics/build_state_stats.py
"""
import csv
import json
import os

DIR = "scripts/church-facts-statistics/"
as_int = lambda v: int(v) if v else 0


def read(name):
    with open(DIR + name, encoding="utf-8") as f:
        return list(csv.DictReader(f))


learn = {r["state"]: r for r in read("states.csv") if r["country"] == "United States"}
states = {}

for r in read("newsroom-states.csv"):
    name = r["name"]
    states[name] = {
        "capital": learn.get(name, {}).get("capital", ""),
        "year": int(r["year"]),
        "members": as_int(r["membership"]),
        "congregations": as_int(r["congregations"]),
        "wards": as_int(r["wards"]),
        "branches": as_int(r["branches"]),
        "stakes": as_int(r["stakes"]),
        "districts": as_int(r["districts"]),
        "missions": as_int(r["missions"]),
        "temples": as_int(r["temples"]),
        "family_history_centers": as_int(r["family_history_centers"]),
        "source_url": r["url"],
    }

for name, r in learn.items():
    if name in states:
        continue
    states[name] = {
        "capital": r["capital"],
        "year": int(r["year"]) if r["year"] else 2025,
        "members": as_int(r["membership"]),
        "congregations": as_int(r["congregations"]),
        "wards": as_int(r["wards"]),
        "branches": as_int(r["branches"]),
        "stakes": as_int(r["stakes"]),
        "districts": as_int(r["districts"]),
        "missions": as_int(r["missions"]),
        "temples": as_int(r["temples"]),
        # This source doesn't publish a count (its field is a template placeholder).
        "family_history_centers": 0,
        "source_url": r["url"],
    }

states = dict(sorted(states.items()))

# The Canadian Newsroom's menu says "Newfoundland"; the map geometry uses the full name.
PROVINCE_NAMES = {"Newfoundland": "Newfoundland and Labrador"}
provinces = {}
for r in read("newsroom-provinces.csv"):
    name = PROVINCE_NAMES.get(r["name"], r["name"])
    provinces[name] = {
        "capital": "",
        "year": int(r["year"]),
        "members": as_int(r["membership"]),
        "congregations": as_int(r["congregations"]),
        "wards": as_int(r["wards"]),
        "branches": as_int(r["branches"]),
        "stakes": as_int(r["stakes"]),
        "districts": as_int(r["districts"]),
        "missions": as_int(r["missions"]),
        "temples": as_int(r["temples"]),
        "family_history_centers": as_int(r["family_history_centers"]),
        "source_url": r["url"],
    }
provinces = dict(sorted(provinces.items()))
os.makedirs("docs/datasets/lds-states", exist_ok=True)
with open("docs/datasets/lds-states/state-stats.json", "w", encoding="utf-8") as f:
    json.dump(
        {
            "note": "U.S. states and D.C., and Canada's provinces and territories (no figures for Nunavut). Newsroom pages carry no as-of date; their charts end at 2025.",
            "countries": {"United States": states, "Canada": provinces},
        },
        f,
        indent=1,
    )
print(len(states), "states; total members", sum(s["members"] for s in states.values()))
print(len(provinces), "provinces; total members", sum(s["members"] for s in provinces.values()), "(Canada reports 211,581)")

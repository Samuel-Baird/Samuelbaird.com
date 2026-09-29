"""Builds the country and continent JSON the Map Explorer reads.

Sources, in order of preference:
  1. countries.csv          (scrape.mjs: churchofjesuschrist.org/learn/facts-statistics)
  2. newsroom-countries.csv (scrape-newsroom.mjs: newsroom.churchofjesuschrist.org)
     fills in countries the first site has no page for (about 40, e.g. the United
     Kingdom and Turkey). Where both have a country the first wins; they agree.
Countries the Church reports no statistics for (China, Israel, ...) are left out.

Writes docs/datasets/lds-units-by-country/country-stats.json and continent-stats.json.
Run from the repo root: python scripts/church-facts-statistics/build_country_stats.py
"""
import csv
import json
from collections import defaultdict

DIR = "scripts/church-facts-statistics/"
OUT = "docs/datasets/lds-units-by-country/"
as_int = lambda v: int(v) if v else 0


def read(name):
    with open(DIR + name, encoding="utf-8") as f:
        return list(csv.DictReader(f))


# Newsroom slugs that are the same country as a learn-site entry under another name.
SAME_AS_LEARN = {"united-states", "saint-vincent"}

countries = {}

for r in read("countries.csv"):
    if not r["year"] or not r["membership"]:
        continue  # the source page returned another country's record
    countries[r["country"]] = {
        "continent": r["continent"],
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

learn_slugs = {r["slug"] for r in read("countries.csv") if r["membership"]}
added = []
for r in read("newsroom-countries.csv"):
    if r["slug"] in learn_slugs or r["name"] in countries or r["slug"] in SAME_AS_LEARN:
        continue
    countries[r["name"]] = {
        "continent": r["continent"],
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
    added.append(r["name"])

countries = dict(sorted(countries.items(), key=lambda kv: -kv[1]["members"]))
with open(OUT + "country-stats.json", "w", encoding="utf-8") as f:
    json.dump({"as_of": "2025 (per-country data year in each row)", "countries": countries}, f, indent=1)

# Continents: the Church's own continent totals, plus counts of countries and the
# ward/branch split (which the continent pages don't give) summed from countries.
FIELDS = ["members", "congregations", "wards", "branches", "stakes", "districts", "missions", "temples", "family_history_centers"]
sums = defaultdict(lambda: defaultdict(int))
n_countries = defaultdict(int)
for c in countries.values():
    n_countries[c["continent"]] += 1
    for f in FIELDS:
        sums[c["continent"]][f] += c[f]

continents = {}
for r in read("continents.csv"):
    name = r["continent"]
    continents[name] = {
        "year": int(r["year"]) if r["year"] else 2025,
        "members": as_int(r["membership"]),
        "congregations": as_int(r["congregations"]),
        "wards": sums[name]["wards"],
        "branches": sums[name]["branches"],
        "stakes": as_int(r["stakes"]),
        "districts": as_int(r["districts"]),
        "missions": as_int(r["missions"]),
        "temples": as_int(r["temples"]),
        "family_history_centers": as_int(r["family_history_centers"]),
        "countries_with_data": n_countries[name],
        "note": "Continent totals are the Church's own; wards and branches are summed from the countries listed.",
    }
with open(OUT + "continent-stats.json", "w", encoding="utf-8") as f:
    json.dump({"as_of": "2025", "continents": continents}, f, indent=1)

print(len(countries), "countries (", len(added), "from the Newsroom ), ", len(continents), "continents")
print("newsroom additions:", ", ".join(added))

# The Activity Estimator reads a slimmer file: members plus the ward/branch split.
with open(DIR + "worldwide.json", encoding="utf-8") as f:
    worldwide = json.load(f)["membership"]
units = {
    name: {k: c[k] for k in ("continent", "year", "members", "wards", "branches", "source_url")}
    for name, c in countries.items()
    if c["wards"] + c["branches"] > 0
}
with open(OUT + "units-by-country.json", "w", encoding="utf-8") as f:
    json.dump(
        {
            "as_of": "2025 (per-country data year in each row)",
            "source_note": "Built by scripts/church-facts-statistics/build_country_stats.py from the Church's facts-and-statistics pages (learn site and Newsroom).",
            "worldwide_members": worldwide,
            "country_order": list(units),
            "countries": units,
        },
        f,
        indent=1,
    )
covered = sum(c["members"] for c in countries.values())
print(f"members covered: {covered:,} of {worldwide:,} worldwide ({covered / worldwide:.1%}); {len(units)} countries have a ward/branch split")

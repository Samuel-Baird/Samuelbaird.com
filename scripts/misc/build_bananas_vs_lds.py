"""
Build docs/datasets/misc/bananas-vs-lds/comparison.json

Sources:
  - LDS membership: docs/datasets/lds-units-by-country/country-stats.json
    (Church-reported figures, year per country, scraped by scripts/church-facts-statistics/)
  - Banana production: D:/latter-day-stats-data/funny/banana-production.csv
    (FAOSTAT via Our World in Data, "Bananas - Production (tonnes)" column)
    https://ourworldindata.org/grapher/banana-production

The script picks the most recent year in the banana CSV for each country, then
maps OWID entity names to Church country names where they differ.

Run from the project root:
  python scripts/misc/build_bananas_vs_lds.py
"""

import csv
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).parent.parent.parent
LDS_JSON = ROOT / "docs/datasets/lds-units-by-country/country-stats.json"
BANANA_CSV = pathlib.Path("D:/latter-day-stats-data/funny/banana-production.csv")
OUT_JSON = ROOT / "docs/datasets/misc/bananas-vs-lds/comparison.json"

TRUCKLOAD_TONNES = 20

# Map from OWID/FAOSTAT entity name -> Church country name.
# Only entries that differ are listed; matching names need no entry.
OWID_TO_CHURCH: dict[str, str] = {
    "United States": "United States",
    "Congo": "Republic of the Congo",
    "Democratic Republic of Congo": "Democratic Republic of the Congo",
    "Cote d'Ivoire": "Cote d'Ivoire",
    "Timor": "Timor-Leste",
    "Czechia": "Czech Republic",
    "North Macedonia": "Macedonia",
    "Eswatini": "Swaziland",
    "Cabo Verde": "Cape Verde",
    "Micronesia (country)": "Micronesia",
}

# Church country names that OWID uses a different spelling for.
# Built automatically from the inverse of OWID_TO_CHURCH where needed.
CHURCH_TO_OWID: dict[str, str] = {v: k for k, v in OWID_TO_CHURCH.items() if k != v}


def load_banana_data(path: pathlib.Path) -> dict[str, float]:
    """Return {owid_entity: tonnes} for the most recent year each country has data."""
    latest: dict[str, tuple[int, float]] = {}  # {entity: (year, tonnes)}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            entity = row["Entity"].strip()
            # Skip aggregate rows (no ISO code or OWID aggregate codes)
            code = row.get("Code", "").strip()
            if not code or code.startswith("OWID_") or "(FAO)" in entity:
                continue
            try:
                year = int(row["Year"])
                tonnes_str = row["Bananas - Production (tonnes)"].strip()
                if not tonnes_str:
                    continue
                tonnes = float(tonnes_str)
            except (ValueError, KeyError):
                continue
            if entity not in latest or year > latest[entity][0]:
                latest[entity] = (year, tonnes)
    return {entity: data[1] for entity, data in latest.items()}


def main() -> None:
    # Load LDS data
    with open(LDS_JSON, encoding="utf-8") as f:
        lds_raw = json.load(f)
    lds_countries: dict[str, dict] = lds_raw["countries"]

    # Load banana data
    banana_by_owid = load_banana_data(BANANA_CSV)

    # Index banana data by Church name for fast lookup
    banana_by_church: dict[str, float] = {}
    for owid_name, tonnes in banana_by_owid.items():
        church_name = OWID_TO_CHURCH.get(owid_name, owid_name)
        banana_by_church[church_name] = tonnes

    # LDS stat fields to carry through (all come from country-stats.json)
    LDS_STAT_FIELDS = [
        "members", "congregations", "wards", "branches",
        "stakes", "districts", "missions", "temples", "family_history_centers",
    ]

    # Build merged output
    countries_out: dict[str, dict] = {}
    for country, lds in lds_countries.items():
        banana_tonnes = banana_by_church.get(country)
        # Also try the reverse mapping (Church name -> OWID name -> back)
        if banana_tonnes is None:
            owid_alt = CHURCH_TO_OWID.get(country)
            if owid_alt:
                banana_tonnes = banana_by_owid.get(owid_alt)

        entry: dict = {}
        for field in LDS_STAT_FIELDS:
            entry[f"lds_{field}"] = lds.get(field, 0) or 0

        if banana_tonnes is not None:
            entry["banana_tonnes"] = round(banana_tonnes, 2)
            entry["banana_truckloads"] = round(banana_tonnes / TRUCKLOAD_TONNES, 2)

        countries_out[country] = entry

    # Determine banana year (most common latest year in the dataset)
    banana_year = 2022  # OWID data most recent complete year
    with open(BANANA_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        years: list[int] = []
        for row in reader:
            code = row.get("Code", "").strip()
            if not code or code.startswith("OWID_") or "(FAO)" in row["Entity"]:
                continue
            try:
                years.append(int(row["Year"]))
            except ValueError:
                pass
    if years:
        from collections import Counter
        # Use the most common maximum year seen across all countries
        banana_year = Counter(years).most_common(1)[0][0]

    output = {
        "source": "LDS: Church of Jesus Christ facts-and-statistics pages; Bananas: FAOSTAT via Our World in Data (ourworldindata.org/grapher/banana-production)",
        "lds_year": lds_raw.get("as_of", "2025"),
        "banana_year": banana_year,
        "truckload_tonnes": TRUCKLOAD_TONNES,
        "countries": countries_out,
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    total = len(countries_out)
    both = sum(1 for v in countries_out.values() if "banana_tonnes" in v and v["lds_members"] > 0)
    lds_only = sum(1 for v in countries_out.values() if "banana_tonnes" not in v and v["lds_members"] > 0)
    banana_only = sum(1 for v in countries_out.values() if "banana_tonnes" in v and v["lds_members"] == 0)

    print(f"Wrote {OUT_JSON}")
    print(f"  {total} Church countries total")
    print(f"  {both} with both LDS and banana data → will be blue or yellow")
    print(f"  {lds_only} LDS-only (no banana production data) → will be blue")
    print(f"  {banana_only} banana-only (zero LDS members reported) → will be yellow")
    print(f"  Banana data year (most common): {banana_year}")


if __name__ == "__main__":
    main()

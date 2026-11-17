"""
Flagship chart for pew-religion-migration: the religious composition of the
world's international migrants in 2020, the most recent year in Pew's
"Religious Composition of the World's Migrants, 1990-2020" report (Kramer,
Tong & Shi, 2024).

Reads the raw "Incoming and Outgoing Migrant Counts.csv" (data/
pew-religion-migration/, gitignored - not committed). That file has one row
per (Direction, Year, Country/Region/Global-Total, Religion), with `level`
distinguishing country (1), region (2), and the world total (3). This chart
uses only the `level == 3` ("Global Total") rows for `Direction ==
"Incoming"` in the most recent year (2020) - i.e. the global stock of
international migrants living outside their birth country, broken out by
religion. "Incoming" and "Outgoing" global totals are identical by
construction (every migrant counted as an inflow to one country is an
outflow from another), so only one direction is needed for a world-total
chart; "Incoming" is used here since Pew's own report frames migrants by
where they now live.

The companion "Peru case study" folder (FOTM_Peru_impute.Rmd/.pdf,
data0X_*.csv, result0X_*.csv) demonstrates Pew's imputation algorithm for
filling in religious composition where the underlying censuses/surveys don't
report it - it is not itself usable output data and is not read by this
script.

Usage: python scripts/pew-religion-migration/global_migrant_composition.py
"""
import json

import pandas as pd

CSV = "data/pew-religion-migration/Incoming and Outgoing Migrant Counts.csv"
YEAR = 2020


def main():
    df = pd.read_csv(CSV, header=1)
    df.columns = [
        "Direction", "Year", "Country", "Religion", "Count", "Percent",
        "Region", "level", "countrycode",
    ]
    df["Count"] = pd.to_numeric(df["Count"].astype(str).str.replace(",", ""), errors="coerce")
    df["Percent"] = pd.to_numeric(df["Percent"], errors="coerce")

    world = df[
        (df["level"] == 3) & (df["Direction"] == "Incoming") & (df["Year"] == YEAR)
    ]
    total_row = world[world["Religion"] == "All"].iloc[0]
    total_migrants = float(total_row["Count"])

    RELIGION_LABELS = {
        "Christian": "Christian",
        "Muslim": "Muslim",
        "Unaffiliated": "Religiously unaffiliated",
        "Hindu": "Hindu",
        "Buddhist": "Buddhist",
        "Jew": "Jewish",
        "Other": "Other religions",
    }

    results = {}
    for raw, label in RELIGION_LABELS.items():
        row = world[world["Religion"] == raw].iloc[0]
        results[label] = {
            "pct": round(float(row["Percent"]), 1),
            "count": float(row["Count"]),
        }

    order = sorted(results, key=lambda label: -results[label]["pct"])

    # 2020 vs the series' first year (1990), for context in the README/report.
    series = df[
        (df["level"] == 3) & (df["Direction"] == "Incoming") & (df["Religion"] == "Christian")
    ][["Year", "Percent", "Count"]].sort_values("Year")

    out = {
        "source": "Kramer, Stephanie, Yunping Tong and Anne Fengyan Shi. 2024. "
                  "\"Religious Composition of the World's Migrants, 1990-2020.\" "
                  "Pew Research Center.",
        "method": "Global total ('Global Total', level 3) rows for Direction=Incoming, "
                  "Year=2020, from Pew's 'Incoming and Outgoing Migrant Counts' file - "
                  "Pew's own estimate of the religious composition of the world's "
                  "international migrant stock (people living outside their country of "
                  "birth), built primarily from 270 censuses and surveys plus Pew's own "
                  "indirect-estimation methodology for gaps (see the Peru case study in "
                  "this dataset's data/ folder for a worked example of that imputation).",
        "year": YEAR,
        "total_migrants": total_migrants,
        "group_order": order,
        "global_composition": results,
        "christian_share_by_year": {
            int(r.Year): {"pct": round(float(r.Percent), 1), "count": float(r.Count)}
            for r in series.itertuples()
        },
    }
    with open("docs/datasets/pew-religion-migration/global-migrant-composition.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:26} {r['pct']:5.1f}%  (n={r['count']:,.0f})")
    print(f"\nTotal migrants, {YEAR}: {total_migrants:,.0f}")
    print("Wrote docs/datasets/pew-religion-migration/global-migrant-composition.json")


if __name__ == "__main__":
    main()

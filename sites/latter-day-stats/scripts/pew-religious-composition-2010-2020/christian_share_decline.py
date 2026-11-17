"""
Flagship chart for the pew-religious-composition-2010-2020 dataset: which
countries saw the Christian share of their population fall the most between
2010 and 2020? This dataset (Pew's "How the Global Religious Landscape
Changed From 2010 to 2020," updated Feb. 12, 2026 with a Religious Diversity
Index) has no Latter-day Saint-specific breakout - LDS people are folded
into the broad "Christians" category alongside every other Christian
tradition - so the natural angle here is Christianity at the country level,
not an LDS-specific one. Worldwide, the raw number of Christians grew (2.15B
-> 2.27B, rounded counts CSV, "All World" row) over the decade, but that
growth trailed global population growth, so Christians' *share* of world
population slipped (30.6% -> 28.8%). This chart looks at where that
share-of-population story was most dramatic at the country level: every one
of the ten steepest declines is a wealthy, secularizing country (Australia,
Chile, the U.S., Canada, the UK, several of Western/Northern Europe) - a
useful backdrop for the Church's own growth numbers elsewhere on this site,
since LDS membership trends run counter to the broader Christian-share
decline in several of these same countries.

Reads the "percentages" CSV (not rounded/unrounded counts - this chart is a
share-of-population comparison, so percentages are the right worksheet per
the dataset's own README.txt guidance to use rounded counts only for count
reporting). Level 1 rows are individual countries/territories (Level 2 is
the six Pew regions, Level 3 is "All World") - 201 countries/territories in
each of 2010 and 2020, matching the README's stated coverage.

Usage: python scripts/pew-religious-composition-2010-2020/christian_share_decline.py
"""
import json

import pandas as pd

CSV = "data/pew-religious-composition-2010-2020/Religious Composition 2010-2020 (percentages).csv"
TOP_N = 10


def main():
    df = pd.read_csv(CSV)
    countries = df[df["Level"] == 1].copy()

    pivot = countries.pivot(index="Country", columns="Year", values="Christians")
    pivot.columns = [str(c) for c in pivot.columns]
    pivot["change_pp"] = pivot["2020"] - pivot["2010"]

    declines = pivot.sort_values("change_pp").head(TOP_N)

    results = {}
    for country, row in declines.iterrows():
        results[country] = {
            "pct_2010": round(float(row["2010"]), 1),
            "pct_2020": round(float(row["2020"]), 1),
            "change_pp": round(float(row["change_pp"]), 1),
            "decline_pp": round(-float(row["change_pp"]), 1),
        }

    order = sorted(results, key=lambda c: -results[c]["decline_pp"])

    out = {
        "source": "Pew Research Center. 2026. \"How the Global Religious Landscape Changed "
                  "From 2010 to 2020.\" (dataset updated Feb. 12, 2026 with a Religious "
                  "Diversity Index.)",
        "method": "Percentage-point change in each country/territory's Christian share of "
                  "population, 2020 minus 2010, from the dataset's own \"percentages\" "
                  "worksheet (Level 1 = individual country/territory rows; Level 2 = Pew's "
                  "six regional rollups; Level 3 = \"All World\" - only Level 1 rows are used "
                  "here). Ranked by the ten largest declines (most negative change) across "
                  "all 201 countries/territories covered by the dataset. Underlying estimates "
                  "are compiled from more than 2,700 national censuses, demographic surveys, "
                  "and population registers, not a single Pew-fielded survey.",
        "n_countries": int(pivot.shape[0]),
        "world_christian_pct_2010": None,
        "world_christian_pct_2020": None,
        "group_order": order,
        "christian_share_decline_pp": results,
    }

    world = df[(df["Level"] == 3)].set_index("Year")["Christians"]
    out["world_christian_pct_2010"] = round(float(world.loc[2010]), 1)
    out["world_christian_pct_2020"] = round(float(world.loc[2020]), 1)

    with open(
        "docs/datasets/pew-religious-composition-2010-2020/christian-share-decline.json",
        "w", encoding="utf-8",
    ) as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for country in order:
        r = results[country]
        print(f"{country:16} {r['pct_2010']:5.1f}% -> {r['pct_2020']:5.1f}%  ({r['change_pp']:+.1f}pp)")
    print(f"\nWorld: {out['world_christian_pct_2010']}% -> {out['world_christian_pct_2020']}%")
    print("\nWrote docs/datasets/pew-religious-composition-2010-2020/christian-share-decline.json")


if __name__ == "__main__":
    main()

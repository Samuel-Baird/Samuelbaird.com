"""
Computes "Party ID (pid7), LDS men vs. LDS women, over time" for the Data
Explorer's Ryan Burge graphics - docs/datasets/ryan-burge/GRAPHICS_TODO.md's
"CES stacked — party ID over time" section, second item (the first,
LDS-overall party ID over time, already shipped as pid-over-time.json).

Population: `trad == "Mormon"`, split by `gender` (Male/Female - the only
two values in this file), across all eight waves (2006-2018).

**Design decision** (per the backlog item's own recommendation): the full
7-point pid7 scale collapses to 3 categories - Democrat (Strong + Not Very
Strong + Lean Democrat), Independent, Republican (mirrored) - because
splitting all 7 points by gender across 8 years produces thin cells in the
smallest year (2017, N=273 total: 134 women, 139 men). The unsplit
LDS-overall chart (pid-over-time.json) keeps a continuous mean instead of
this categorical collapse, a different design choice for a different
population size - not a contradiction, per the backlog's own note that
item 1 "isn't split further and can likely keep the full 7-point scale."

This file has **no survey weight column** (see this dataset's own note in
GRAPHICS_TODO.md) - every number below is a raw unweighted share.

Usage: python scripts/ryan-burge/pid_by_gender.py
"""
import json

import numpy as np
import pandas as pd

CSV = "data/ryan-burge/tier1-strong/ces_stacked_2006-2018_css_small.csv"

DEM_LABELS = {"Strong\nDemocrat", "Not Very\nStrong Dem.", "Lean\nDemocrat"}
REP_LABELS = {"Strong\nRepublican", "Not Very\nStrong Rep.", "Lean\nRepublican"}
IND_LABELS = {"Independent"}

CATEGORY_ORDER = ["Democrat", "Independent", "Republican"]
WAVES = [2006, 2008, 2010, 2012, 2014, 2016, 2017, 2018]


def collapse(pid7: str) -> str | None:
    if pid7 in DEM_LABELS:
        return "Democrat"
    if pid7 in REP_LABELS:
        return "Republican"
    if pid7 in IND_LABELS:
        return "Independent"
    return None


def main():
    df = pd.read_csv(CSV)
    df = df[df["trad"] == "Mormon"].copy()
    df["pid3"] = df["pid7"].map(collapse)

    results = {}
    for year in WAVES:
        for gender in ("Male", "Female"):
            sub = df[(df["year"] == year) & (df["gender"] == gender) & df["pid3"].notna()]
            n = len(sub)
            shares = {cat: round(100 * (sub["pid3"] == cat).sum() / n, 2) if n else None
                      for cat in CATEGORY_ORDER}
            results[f"{year}_{gender}"] = {
                "year": year,
                "gender": gender,
                "shares_pct": shares,
                "n": int(n),
            }

    out = {
        "source": "Ryan Burge (github.com/ryanburge), CES stacked 2006-2018 common content "
                   "extract (ces_stacked_2006-2018_css_small.csv).",
        "via": "Ryan Burge",
        "method": "Population: trad == 'Mormon', split by gender, across all eight waves. "
                  "pid7's 7 categories collapsed to 3 (Democrat/Independent/Republican, "
                  "leaners folded into their party) per the backlog item's own design-decision "
                  "note - the smallest year/gender cell (2017 women, N=134) is too thin for "
                  "the full 7-point split. Unweighted - this file carries no survey weight "
                  "column.",
        "category_order": CATEGORY_ORDER,
        "waves": WAVES,
        "by_year_gender": results,
    }
    with open("docs/datasets/ryan-burge/pid-by-gender.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print("\n=== LDS party ID (3-category), by gender and year ===")
    for year in WAVES:
        for gender in ("Male", "Female"):
            r = results[f"{year}_{gender}"]
            shares = ", ".join(f"{k} {v:.0f}%" for k, v in r["shares_pct"].items())
            print(f"{year} {gender:6} {shares}  (n={r['n']})")

    print("\nWrote docs/datasets/ryan-burge/pid-by-gender.json")


if __name__ == "__main__":
    main()

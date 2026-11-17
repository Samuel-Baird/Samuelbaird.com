"""
Computes the birth-decade distribution (BIRTHDECADE) for each Christian
tradition's current membership, plus a weighted Christian-overall average,
for the Data Explorer's Pew RLS graphic.

GRAPHICS_TODO.md's "Partially blocked" item: there is no continuous age
variable in the public-use file, and no age-in-single-years or half-decade
variable either (BIRTHHALFDECADE is restricted-use only). BIRTHDECADE (7
buckets, public) is the only age measure available, so this ships the
distribution chart the TODO calls "fully buildable" and drops the numeric
median age it calls not directly computable without assuming a distribution
within each bucket.

Population: CURREL (current religion, same coding as switching_rates.py's
FRMREL/CURREL groups) - this is a snapshot of who's in each tradition today,
not who was raised in it, so CURREL is the right variable (not FRMREL).
Respondents who declined to answer BIRTHDECADE (code "99") are excluded from
that group's denominator, matching how Pew's own tables handle non-response
on a single item.

Usage: python scripts/pew-rls/birth_decade_distribution.py
"""
import json

import numpy as np
import pandas as pd

CSV = "data/pew-rls-2023-24/2023-24 RLS Public Use File Feb 19.csv"

# Same six-group Christian set as switching_rates.py's GROUPS, in the order
# GRAPHICS_TODO.md lists the "childhood formation" group set.
GROUPS = {
    "1000": "Protestant",
    "10000": "Catholic",
    "20000": "Latter-day Saint",
    "30000": "Orthodox Christian",
    "40001": "Jehovah's Witness",
    "40002": "Other Christian",
}

DECADES = {
    "1": "1940s or earlier",
    "2": "1950s",
    "3": "1960s",
    "4": "1970s",
    "5": "1980s",
    "6": "1990s",
    "7": "2000s",
}

REPWT_COLS = [f"REPWT_{i:03d}" for i in range(1, 501)]
USECOLS = ["CURREL", "BIRTHDECADE", "WEIGHT", *REPWT_COLS]


def weighted_decade_shares(weight: np.ndarray, decade_col: pd.Series) -> dict:
    """% share of each decade bucket among respondents who answered (excludes '99')."""
    answered = decade_col.values != "99"
    w = weight[answered]
    total = w.sum()
    shares = {}
    for code, label in DECADES.items():
        pct = 100 * w[decade_col.values[answered] == code].sum() / total
        shares[label] = round(pct, 2)
    return shares


def main():
    print("Loading CSV (this takes a bit - 502 columns, 36,908 rows)...")
    df = pd.read_csv(CSV, usecols=USECOLS, dtype={"CURREL": str, "BIRTHDECADE": str})
    weight = df["WEIGHT"].to_numpy()

    results = {}
    for code, label in GROUPS.items():
        mask = df["CURREL"].values == code
        results[label] = {
            "shares_pct": weighted_decade_shares(weight[mask], df.loc[mask, "BIRTHDECADE"]),
            "unweighted_n": int(mask.sum()),
            "answered_unweighted_n": int((mask & (df["BIRTHDECADE"].values != "99")).sum()),
        }

    # Weighted Christian-overall average: every respondent whose CURREL falls
    # in one of the six groups above, pooled together.
    christian_mask = df["CURREL"].isin(GROUPS.keys()).to_numpy()
    results["Christian average"] = {
        "shares_pct": weighted_decade_shares(weight[christian_mask], df.loc[christian_mask, "BIRTHDECADE"]),
        "unweighted_n": int(christian_mask.sum()),
        "answered_unweighted_n": int((christian_mask & (df["BIRTHDECADE"].values != "99")).sum()),
    }

    out = {
        "source": "Pew Research Center. 2025. “2023-24 Religious Landscape Study "
                   "(RLS) Dataset.” doi: 10.58094/3kwb-bf52.",
        "method": "Share of each tradition's current (CURREL) membership born in each decade "
                  "(BIRTHDECADE), weighted by WEIGHT. Respondents who declined to answer "
                  "BIRTHDECADE are excluded from that group's denominator. No continuous age "
                  "variable exists in the public-use file, so this is the finest age measure "
                  "available; a numeric median age is not computed here since it would require "
                  "assuming a distribution within each decade bucket rather than reading Pew's "
                  "own number.",
        "decade_order": list(DECADES.values()),
        "total_unweighted_n": int(len(df)),
        "distribution": results,
    }
    with open("docs/datasets/pew-rls-2023-24/birth-decade-distribution.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print("\n=== Birth-decade distribution by current tradition ===")
    for label, r in results.items():
        row = "  ".join(f"{d}: {r['shares_pct'][d]:.0f}%" for d in DECADES.values())
        print(f"{label:20} (n={r['answered_unweighted_n']:>5})  {row}")

    print("\nWrote docs/datasets/pew-rls-2023-24/birth-decade-distribution.json")


if __name__ == "__main__":
    main()

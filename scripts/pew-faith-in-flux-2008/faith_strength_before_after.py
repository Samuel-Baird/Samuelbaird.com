"""
Fifth flagship chart for Faith in Flux: after switching religion, is
people's faith stronger or weaker than it was as a teenager? Compares
top-two-box ("very strong" + "somewhat strong") on q12 (faith strength as
a teenager, in their childhood religion) against q13 (faith strength now,
in their current religion), across all 2,867 recontacted switchers - same
population as reasons_left_religion.py in this folder. Not a matched
before/after for each individual item's own denominator - each question
excludes its own don't know/refused/no-faith-at-the-time separately.

Usage: python scripts/pew-faith-in-flux-2008/faith_strength_before_after.py
"""
import json

import numpy as np
import pyreadstat

SAV = ("data/pew-faith-in-flux-2008/"
       "Dataset - Pew Forum on Religion & Public Life 2008 Conversion Recontact Survey.sav")

ITEMS = {
    "q12": "As a teenager",
    "q13": "Now",
}
STRONG_CODES = {1.0, 2.0}  # very strong, somewhat strong
VALID_CODES = {1.0, 2.0, 3.0, 4.0}  # excludes "didn't/don't have religious faith" (5.0) and DK/refused (9.0)


def main():
    usecols = ["weight", *ITEMS.keys()]
    df, _ = pyreadstat.read_sav(SAV, usecols=usecols)
    weight = df["weight"].to_numpy()

    results = {}
    for col, label in ITEMS.items():
        item = df[col].to_numpy()
        valid = np.isin(item, list(VALID_CODES))
        strong = valid & np.isin(item, list(STRONG_CODES))
        results[label] = {
            "pct": round(100 * weight[strong].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
        }

    order = ["As a teenager", "Now"]

    out = {
        "source": 'Pew Research Center. 2009. "Faith in Flux: Changes in Religious '
                  'Affiliation in the U.S."',
        "method": "Population is all respondents who left the religion they were raised in "
                  "(this recontact survey's own design). Top-two-box (\"very strong\" + "
                  "\"somewhat strong\") on q12 (faith strength as a teenager, in their "
                  "childhood religion) and q13 (faith strength now, in their current "
                  "religion); each item's own \"didn't/don't have religious faith\" and "
                  "don't know/refused excluded from its own denominator. Weighted by the "
                  "dataset's own `weight` variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "time_order": order,
        "strong_faith_pct": results,
    }
    with open("docs/datasets/pew-faith-in-flux-2008/faith-strength-before-after.json",
              "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:16} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>4})")
    print("\nWrote docs/datasets/pew-faith-in-flux-2008/faith-strength-before-after.json")


if __name__ == "__main__":
    main()

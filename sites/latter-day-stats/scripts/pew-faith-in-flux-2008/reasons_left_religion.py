"""
Second flagship chart for Faith in Flux: among the survey's 2,867
respondents who left the religion they were raised in, which reasons do
they give? Unlike reasons_joined_lds.py in this folder (which isolates the
38-respondent LDS-convert subgroup - too small a base for a leaving-side
mirror; former Mormons here number just 26), this is a single-population
ranking across ALL religious leavers surveyed, using six broadly worded
items from the q4 battery ("is this an important reason you are no longer
[FRMREL]") that apply regardless of which religion someone left. Several
other q4 items (e.g. q4g, q4h, q4s) are worded around specifically
Catholic practices and are excluded for that reason.

Usage: python scripts/pew-faith-in-flux-2008/reasons_left_religion.py
"""
import json

import numpy as np
import pyreadstat

SAV = ("data/pew-faith-in-flux-2008/"
       "Dataset - Pew Forum on Religion & Public Life 2008 Conversion Recontact Survey.sav")

REASON_ITEMS = {
    "q4o": "Stopped believing in the religion's teachings",
    "q4f": "Just gradually drifted away",
    "q4d": "Found a religion they liked more",
    "q4b": "Spiritual needs weren't being met",
    "q4n": "Wasn't comfortable with the community there",
    "q4a": "Married someone of a different religion",
}
IMPORTANT = 1.0
VALID_CODES = {1.0, 2.0}


def main():
    usecols = ["weight", *REASON_ITEMS.keys()]
    df, _ = pyreadstat.read_sav(SAV, usecols=usecols)
    weight = df["weight"].to_numpy()

    results = {}
    for col, label in REASON_ITEMS.items():
        item = df[col].to_numpy()
        valid = np.isin(item, list(VALID_CODES))
        important = valid & (item == IMPORTANT)
        results[label] = {
            "pct": round(100 * weight[important].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
        }

    order = sorted(results, key=lambda label: -results[label]["pct"])

    out = {
        "source": 'Pew Research Center. 2009. "Faith in Flux: Changes in Religious '
                  'Affiliation in the U.S."',
        "method": "Population is all respondents who left the religion they were raised in "
                  "(this recontact survey's own design - all 2,867 respondents had changed "
                  "religious tradition or moved within one since childhood). Each reason's "
                  "own don't know/refused excluded from its own denominator. Weighted by "
                  "the dataset's own `weight` variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "reason_order": order,
        "important_reason_pct": results,
    }
    with open("docs/datasets/pew-faith-in-flux-2008/reasons-left-religion.json",
              "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:44} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>4})")
    print("\nWrote docs/datasets/pew-faith-in-flux-2008/reasons-left-religion.json")


if __name__ == "__main__":
    main()

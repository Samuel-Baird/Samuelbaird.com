"""
Fifth flagship-style chart for the 2011 National Survey of Mormons: three
core Christian/LDS belief items (q409a/b/d), a single-population ranking
among Mormons themselves - same shape as essential_to_being_mormon.py.
Each item's own don't know/refused (9) is excluded from that item's own
denominator.

Hook: Easter (Palm Sunday/Good Friday/Easter Sunday), March 21-28 2027.

Usage: python scripts/pew-mormon-survey-2011/core_beliefs.py
"""
import json

import numpy as np
import pyreadstat

SAV = ("data/pew-mormon-survey-2011/"
       "Dataset - Pew Forum on Religion & Public Life 2011 National Survey of Mormons.sav")

ITEMS = {
    "q409a": "Jesus rose from the dead",
    "q409d": "Families can be sealed together eternally in temple ceremonies",
    "q409b": "God the Father and Jesus Christ are separate, physical beings",
}
VALID_CODES = {1.0, 2.0}
YES = 1.0


def main():
    usecols = ["weight", *ITEMS.keys()]
    df, _ = pyreadstat.read_sav(SAV, usecols=usecols)
    weight = df["weight"].to_numpy()

    results = {}
    for col, label in ITEMS.items():
        item = df[col].to_numpy()
        valid = np.isin(item, list(VALID_CODES))
        yes = valid & (item == YES)
        results[label] = {
            "pct": round(100 * weight[yes].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
        }

    order = sorted(results, key=lambda label: -results[label]["pct"])

    out = {
        "source": 'Pew Research Center. 2012. "2011 National Survey of Mormons."',
        "method": "Population is all respondents (self-identified Mormons by the survey's "
                  "own design). Each item's own don't know/refused excluded from its own "
                  "denominator. Weighted by the dataset's own `weight` variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "item_order": order,
        "believe_pct": results,
    }
    with open("docs/datasets/pew-mormon-survey-2011/core-beliefs.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:60} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>4})")
    print("\nWrote docs/datasets/pew-mormon-survey-2011/core-beliefs.json")


if __name__ == "__main__":
    main()

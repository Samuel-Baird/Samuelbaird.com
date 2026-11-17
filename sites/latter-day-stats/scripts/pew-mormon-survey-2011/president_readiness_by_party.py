"""
Sixth flagship chart for the 2011 National Survey of Mormons: do Mormons
of different parties differ in whether they think Americans are ready to
elect a Mormon president (q311)? Population is all respondents
(self-identified Mormons by the survey's own design), broken out by
self-reported party (party). "Other/depends" (q311 code 3) is excluded
from the yes/no share along with don't know/refused, matching this site's
existing yes/no-share convention (see mormonism_christian.py's don't-know
handling, which explicitly keeps DK as its own segment - this one instead
narrows to a clean yes/no share since q311 has no similarly-published
three-way topline to preserve).

Usage: python scripts/pew-mormon-survey-2011/president_readiness_by_party.py
"""
import json

import numpy as np
import pyreadstat

SAV = ("data/pew-mormon-survey-2011/"
       "Dataset - Pew Forum on Religion & Public Life 2011 National Survey of Mormons.sav")

PARTY_CODES = {1.0: "Republican", 2.0: "Democrat", 3.0: "Independent"}
YES = 1.0
VALID_CODES = {1.0, 2.0}  # yes / no (excludes "other/depends" and don't know/refused)
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["party", "q311", "weight"])
    weight = df["weight"].to_numpy()
    party = df["party"].to_numpy()
    ready = df["q311"].to_numpy()

    results = {}
    for code, label in PARTY_CODES.items():
        group_mask = party == code
        valid = group_mask & np.isin(ready, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        yes = valid & (ready == YES)
        results[label] = {
            "pct": round(100 * weight[yes].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(ready, list(VALID_CODES))
    yes_all = valid_all & (ready == YES)
    results["All Mormon adults"] = {
        "pct": round(100 * weight[yes_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }

    order = [label for label in results if label != "All Mormon adults"]
    order.sort(key=lambda label: -results[label]["pct"])
    order.append("All Mormon adults")

    out = {
        "source": 'Pew Research Center. 2012. "2011 National Survey of Mormons."',
        "method": "Population is all respondents (self-identified Mormons by the survey's "
                  "own design), broken out by self-reported party (party). Share answering "
                  "\"yes\" to q311 (\"do you think the American people as a whole are ready "
                  "to elect a Mormon as president\"); \"other/depends\" and don't know/"
                  "refused excluded from each row's denominator. Weighted by the dataset's "
                  "own `weight` variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "ready_for_mormon_president": results,
    }
    with open("docs/datasets/pew-mormon-survey-2011/president-readiness-by-party.json",
              "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:20} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>4})")
    print("\nWrote docs/datasets/pew-mormon-survey-2011/president-readiness-by-party.json")


if __name__ == "__main__":
    main()

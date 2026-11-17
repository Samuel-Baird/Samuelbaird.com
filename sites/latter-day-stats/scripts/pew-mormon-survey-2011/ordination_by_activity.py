"""
Flagship chart for the 2011 National Survey of Mormons: does support for
ordaining women to the priesthood vary with how active a respondent is in
the Church? Reads q409e ("Do you believe that women who are dedicated
members of the LDS/Mormon Church should be ordained to the priesthood, or
not?") against q406 ("How active are you in the LDS/Mormon Church?"),
weighted by `weight`. Population is all 1,019 respondents (all
self-identified Mormons by design - see data/pew-mormon-survey-2011's own
codebook); q409e's own don't know/refused (9) is excluded from each row's
denominator, same as every other binary-share item across this pipeline.

Usage: python scripts/pew-mormon-survey-2011/ordination_by_activity.py
"""
import json

import numpy as np
import pyreadstat

SAV = ("data/pew-mormon-survey-2011/"
       "Dataset - Pew Forum on Religion & Public Life 2011 National Survey of Mormons.sav")

ACTIVITY_ORDER = ["Very active", "Somewhat active", "Not too active", "Not at all active"]
ACTIVITY_CODES = {1.0: "Very active", 2.0: "Somewhat active", 3.0: "Not too active", 4.0: "Not at all active"}


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["q406", "q409e", "weight"])
    weight = df["weight"].to_numpy()
    activity = df["q406"].to_numpy()
    ordain = df["q409e"].to_numpy()

    results = {}
    for code, label in ACTIVITY_CODES.items():
        group_mask = activity == code
        valid = group_mask & np.isin(ordain, [1.0, 2.0])
        yes = valid & (ordain == 1.0)
        results[label] = {
            "pct": round(100 * weight[yes].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(ordain, [1.0, 2.0])
    yes_all = valid_all & (ordain == 1.0)
    results["All Mormon adults"] = {
        "pct": round(100 * weight[yes_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }

    out = {
        "source": 'Pew Research Center. 2012. "2011 National Survey of Mormons."',
        "method": "Population is all respondents (self-identified Mormons by the survey's own "
                  "design), broken out by self-reported activity level in the Church (q406); "
                  "q409e's own don't know/refused is excluded from each row's denominator. "
                  "Weighted by the dataset's own `weight` variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "activity_order": ACTIVITY_ORDER + ["All Mormon adults"],
        "ordain_women_yes": results,
    }
    with open("docs/datasets/pew-mormon-survey-2011/ordination-by-activity.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in ACTIVITY_ORDER + ["All Mormon adults"]:
        r = results[label]
        print(f"{label:20} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>4})")
    print("\nWrote docs/datasets/pew-mormon-survey-2011/ordination-by-activity.json")


if __name__ == "__main__":
    main()

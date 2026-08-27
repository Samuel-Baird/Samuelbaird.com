"""
Fourth flagship chart for the 2011 National Survey of Mormons: does paying
a full tithe (q416, "yes, pay tithing") vary with how active a respondent
is in the Church (q406)? Same by-group construction as
ordination_by_activity.py - q416's own don't know/refused (9) and the
partial-donor response ("donate money to church, but not a full 10%", 3)
are excluded from each row's denominator, since the question this chart
answers is specifically "do you pay a full tithe or not," matching q416's
own yes/no framing rather than its three-way response option.

Usage: python scripts/pew-mormon-survey-2011/tithing_by_activity.py
"""
import json

import numpy as np
import pyreadstat

SAV = ("data/pew-mormon-survey-2011/"
       "Dataset - Pew Forum on Religion & Public Life 2011 National Survey of Mormons.sav")

ACTIVITY_ORDER = ["Very active", "Somewhat active", "Not too active", "Not at all active"]
ACTIVITY_CODES = {1.0: "Very active", 2.0: "Somewhat active", 3.0: "Not too active", 4.0: "Not at all active"}
VALID_CODES = {1.0, 2.0}  # yes, pay tithing / no, do not pay tithing


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["q406", "q416", "weight"])
    weight = df["weight"].to_numpy()
    activity = df["q406"].to_numpy()
    tithe = df["q416"].to_numpy()

    results = {}
    for code, label in ACTIVITY_CODES.items():
        group_mask = activity == code
        valid = group_mask & np.isin(tithe, list(VALID_CODES))
        yes = valid & (tithe == 1.0)
        results[label] = {
            "pct": round(100 * weight[yes].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(tithe, list(VALID_CODES))
    yes_all = valid_all & (tithe == 1.0)
    results["All Mormon adults"] = {
        "pct": round(100 * weight[yes_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }

    out = {
        "source": 'Pew Research Center. 2012. "2011 National Survey of Mormons."',
        "method": "Population is all respondents (self-identified Mormons by the survey's "
                  "own design), broken out by self-reported activity level in the Church "
                  "(q406). q416's \"donate but not a full 10%\" response and its own don't "
                  "know/refused are excluded from each row's denominator, since this chart "
                  "answers q416's own yes/no framing (pay a full tithe, or not). Weighted "
                  "by the dataset's own `weight` variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "activity_order": ACTIVITY_ORDER + ["All Mormon adults"],
        "pay_tithing_yes": results,
    }
    with open("docs/datasets/pew-mormon-survey-2011/tithing-by-activity.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in ACTIVITY_ORDER + ["All Mormon adults"]:
        r = results[label]
        print(f"{label:20} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>4})")
    print("\nWrote docs/datasets/pew-mormon-survey-2011/tithing-by-activity.json")


if __name__ == "__main__":
    main()

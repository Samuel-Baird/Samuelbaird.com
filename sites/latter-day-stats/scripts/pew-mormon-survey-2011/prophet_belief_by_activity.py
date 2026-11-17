"""
Flagship chart for the 2011 National Survey of Mormons: does belief that
the president of the LDS/Mormon Church is a prophet of God (q409c) vary
with how active a respondent is in the Church (q406)? Same by-group
construction as ordination_by_activity.py, temple_recommend_by_activity.py,
and daily_prayer_by_activity.py in this folder - q409c's own don't know/
refused (9) is excluded from each row's denominator. Distinct from
core_beliefs.py's q409a/b/d trio, which reports a single Mormons-overall
ranking with no activity breakout - q409c is the one core-belief item in
that same battery not yet used anywhere on the site, and it names a
foundational, load-bearing LDS truth claim: that the Church's president is
a living prophet, on par with the earlier belief-by-activity items already
built for q408/q412/q419.

Usage: python scripts/pew-mormon-survey-2011/prophet_belief_by_activity.py
"""
import json

import numpy as np
import pyreadstat

SAV = ("data/pew-mormon-survey-2011/"
       "Dataset - Pew Forum on Religion & Public Life 2011 National Survey of Mormons.sav")

ACTIVITY_ORDER = ["Very active", "Somewhat active", "Not too active", "Not at all active"]
ACTIVITY_CODES = {1.0: "Very active", 2.0: "Somewhat active", 3.0: "Not too active", 4.0: "Not at all active"}
VALID_CODES = {1.0, 2.0}  # yes / no


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["q406", "q409c", "weight"])
    weight = df["weight"].to_numpy()
    activity = df["q406"].to_numpy()
    prophet = df["q409c"].to_numpy()

    results = {}
    for code, label in ACTIVITY_CODES.items():
        group_mask = activity == code
        valid = group_mask & np.isin(prophet, list(VALID_CODES))
        yes = valid & (prophet == 1.0)
        results[label] = {
            "pct": round(100 * weight[yes].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(prophet, list(VALID_CODES))
    yes_all = valid_all & (prophet == 1.0)
    results["All Mormon adults"] = {
        "pct": round(100 * weight[yes_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }

    out = {
        "source": 'Pew Research Center. 2012. "2011 National Survey of Mormons."',
        "method": "Population is all respondents (self-identified Mormons by the survey's "
                  "own design), broken out by self-reported activity level in the Church "
                  "(q406). q409c asks whether the respondent believes the president of the "
                  "LDS/Mormon Church is a prophet of God; its own don't know/refused is "
                  "excluded from each row's denominator. Weighted by the dataset's own "
                  "`weight` variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "activity_order": ACTIVITY_ORDER + ["All Mormon adults"],
        "believes_president_is_prophet_pct": results,
    }
    with open("docs/datasets/pew-mormon-survey-2011/prophet-belief-by-activity.json",
              "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in ACTIVITY_ORDER + ["All Mormon adults"]:
        r = results[label]
        print(f"{label:20} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>4})")
    print("\nWrote docs/datasets/pew-mormon-survey-2011/prophet-belief-by-activity.json")


if __name__ == "__main__":
    main()

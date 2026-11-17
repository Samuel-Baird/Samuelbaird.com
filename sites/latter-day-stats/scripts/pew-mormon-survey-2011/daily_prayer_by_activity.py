"""
Flagship chart for the 2011 National Survey of Mormons: does praying at
least once a day outside of religious services (q412, top-two-box
"several times a day" + "once a day") vary with how active a respondent
is in the Church (q406)? Same by-group construction as
ordination_by_activity.py, tithing_by_activity.py, and
temple_recommend_by_activity.py in this folder - q412's own don't know/
refused (9) is excluded from each row's denominator.

Usage: python scripts/pew-mormon-survey-2011/daily_prayer_by_activity.py
"""
import json

import numpy as np
import pyreadstat

SAV = ("data/pew-mormon-survey-2011/"
       "Dataset - Pew Forum on Religion & Public Life 2011 National Survey of Mormons.sav")

ACTIVITY_ORDER = ["Very active", "Somewhat active", "Not too active", "Not at all active"]
ACTIVITY_CODES = {1.0: "Very active", 2.0: "Somewhat active", 3.0: "Not too active", 4.0: "Not at all active"}
VALID_CODES = {1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0}
DAILY_CODES = {1.0, 2.0}  # several times a day, once a day


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["q406", "q412", "weight"])
    weight = df["weight"].to_numpy()
    activity = df["q406"].to_numpy()
    prayer = df["q412"].to_numpy()

    results = {}
    for code, label in ACTIVITY_CODES.items():
        group_mask = activity == code
        valid = group_mask & np.isin(prayer, list(VALID_CODES))
        daily = valid & np.isin(prayer, list(DAILY_CODES))
        results[label] = {
            "pct": round(100 * weight[daily].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(prayer, list(VALID_CODES))
    daily_all = valid_all & np.isin(prayer, list(DAILY_CODES))
    results["All Mormon adults"] = {
        "pct": round(100 * weight[daily_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }

    out = {
        "source": 'Pew Research Center. 2012. "2011 National Survey of Mormons."',
        "method": "Population is all respondents (self-identified Mormons by the survey's "
                  "own design), broken out by self-reported activity level in the Church "
                  "(q406). q412 asks how often the respondent prays outside of religious "
                  "services; this chart shows the top-two-box share praying at least once a "
                  "day (\"several times a day\" + \"once a day\"). Don't know/refused is "
                  "excluded from each row's denominator. Weighted by the dataset's own "
                  "`weight` variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "activity_order": ACTIVITY_ORDER + ["All Mormon adults"],
        "prays_daily_pct": results,
    }
    with open("docs/datasets/pew-mormon-survey-2011/daily-prayer-by-activity.json",
              "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in ACTIVITY_ORDER + ["All Mormon adults"]:
        r = results[label]
        print(f"{label:20} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>4})")
    print("\nWrote docs/datasets/pew-mormon-survey-2011/daily-prayer-by-activity.json")


if __name__ == "__main__":
    main()

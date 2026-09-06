"""
Flagship chart for the 2011 National Survey of Mormons: does belief in yoga
"not just as exercise, but as a spiritual practice" (q409f) vary with how
active a respondent is in the Church (q406)? Same by-group
construction as prophet_belief_by_activity.py, ordination_by_activity.py,
temple_recommend_by_activity.py, and daily_prayer_by_activity.py in this
folder -- q409f's own don't know/refused is excluded from each row's
denominator. Distinct from core_beliefs.py's q409a/b/d trio and the already-
shipped q409c/q409e items -- q409f is the one item left in that same battery
not yet used anywhere on the site (q409g, belief in reincarnation, is skipped
as a near-duplicate of the already-shipped pew-atp-w143-2024
believes-in-reincarnation chart, which asks the identical construct of
Mormons alongside other traditions). Unlike a core doctrinal item, this one
reads as a proxy for openness to non-LDS spiritual practice: the Word of
Wisdom and modern-day counsel from Church leaders caution against exercise
substitutes for revealed worship, so a gradient by activity level (more
engaged members less likely to treat yoga as spiritual practice) is a
plausible, checkable story.

Usage: python scripts/pew-mormon-survey-2011/yoga_by_activity.py
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
    df, _ = pyreadstat.read_sav(SAV, usecols=["q406", "q409f", "weight"])
    weight = df["weight"].to_numpy()
    activity = df["q406"].to_numpy()
    yoga = df["q409f"].to_numpy()

    results = {}
    for code, label in ACTIVITY_CODES.items():
        group_mask = activity == code
        valid = group_mask & np.isin(yoga, list(VALID_CODES))
        yes = valid & (yoga == 1.0)
        results[label] = {
            "pct": round(100 * weight[yes].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(yoga, list(VALID_CODES))
    yes_all = valid_all & (yoga == 1.0)
    results["All Mormon adults"] = {
        "pct": round(100 * weight[yes_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }

    out = {
        "source": 'Pew Research Center. 2012. "2011 National Survey of Mormons."',
        "method": "Population is all respondents (self-identified Mormons by the survey's "
                  "own design), broken out by self-reported activity level in the Church "
                  "(q406). q409f asks whether the respondent believes in yoga, not just as "
                  "exercise, but as a spiritual practice; its own don't know/refused is "
                  "excluded from each row's denominator. Weighted by the dataset's own "
                  "`weight` variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "activity_order": ACTIVITY_ORDER + ["All Mormon adults"],
        "believes_yoga_spiritual_pct": results,
    }
    with open("docs/datasets/pew-mormon-survey-2011/yoga-by-activity.json",
              "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in ACTIVITY_ORDER + ["All Mormon adults"]:
        r = results[label]
        print(f"{label:20} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>4})")
    print("\nWrote docs/datasets/pew-mormon-survey-2011/yoga-by-activity.json")


if __name__ == "__main__":
    main()

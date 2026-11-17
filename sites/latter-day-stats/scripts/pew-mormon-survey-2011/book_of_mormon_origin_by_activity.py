"""
Flagship chart for the 2011 National Survey of Mormons: does belief that
the Book of Mormon was written by ancient prophets and translated by
Joseph Smith (rather than written by Joseph Smith himself) vary with how
active a respondent is in the Church? Reads q408 ("Which statement comes
closer to your own views") against q406 ("How active are you in the
LDS/Mormon Church?"), weighted by `weight`. Population is all 1,019
respondents (all self-identified Mormons by design); q408's own
other/neither/both (3) and don't know/refused (9) are excluded from each
row's denominator, matching this chart's ancient-prophets-vs-Joseph-Smith
framing. Same by-group construction as ordination_by_activity.py and
tithing_by_activity.py in this folder.

Usage: python scripts/pew-mormon-survey-2011/book_of_mormon_origin_by_activity.py
"""
import json

import numpy as np
import pyreadstat

SAV = ("data/pew-mormon-survey-2011/"
       "Dataset - Pew Forum on Religion & Public Life 2011 National Survey of Mormons.sav")

ACTIVITY_ORDER = ["Very active", "Somewhat active", "Not too active", "Not at all active"]
ACTIVITY_CODES = {1.0: "Very active", 2.0: "Somewhat active", 3.0: "Not too active", 4.0: "Not at all active"}
VALID_CODES = {1.0, 2.0}  # written by Joseph Smith / written by ancient prophets, translated
ANCIENT_PROPHETS = 2.0


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["q406", "q408", "weight"])
    weight = df["weight"].to_numpy()
    activity = df["q406"].to_numpy()
    origin = df["q408"].to_numpy()

    results = {}
    for code, label in ACTIVITY_CODES.items():
        group_mask = activity == code
        valid = group_mask & np.isin(origin, list(VALID_CODES))
        ancient = valid & (origin == ANCIENT_PROPHETS)
        results[label] = {
            "pct": round(100 * weight[ancient].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(origin, list(VALID_CODES))
    ancient_all = valid_all & (origin == ANCIENT_PROPHETS)
    results["All Mormon adults"] = {
        "pct": round(100 * weight[ancient_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }

    out = {
        "source": 'Pew Research Center. 2012. "2011 National Survey of Mormons."',
        "method": "Population is all respondents (self-identified Mormons by the survey's "
                  "own design), broken out by self-reported activity level in the Church "
                  "(q406). q408 asks respondents to choose between \"the Book of Mormon was "
                  "WRITTEN by Joseph Smith\" and \"the Book of Mormon was written by ancient "
                  "prophets and translated by Joseph Smith\"; this chart shows the ancient-"
                  "prophets share. The other/neither/both response and don't know/refused are "
                  "excluded from each row's denominator. Weighted by the dataset's own "
                  "`weight` variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "activity_order": ACTIVITY_ORDER + ["All Mormon adults"],
        "ancient_prophets_pct": results,
    }
    with open("docs/datasets/pew-mormon-survey-2011/book-of-mormon-origin-by-activity.json",
              "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in ACTIVITY_ORDER + ["All Mormon adults"]:
        r = results[label]
        print(f"{label:20} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>4})")
    print("\nWrote docs/datasets/pew-mormon-survey-2011/book-of-mormon-origin-by-activity.json")


if __name__ == "__main__":
    main()

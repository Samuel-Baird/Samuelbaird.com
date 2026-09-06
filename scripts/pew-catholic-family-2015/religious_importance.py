"""
Fifth chart for the 2015 Survey of U.S. Catholics and Family Life: qf2,
"How important is religion in your life -- very important, somewhat
important, not too important, or not at all important?" Asked of the
general public (not Catholics only), broken out by present religion
(relig) -- same sample and grouping convention as adult_arrangements.py/
prayer_style.py in this folder.

Hook: general religious-salience item, not LDS-specific wording, but a
clean cross-tradition comparison point. 81.4% of Mormons say religion is
"very important" in their life, 2nd only to Jehovah's Witness (87.9%,
n=32) among named traditions and well above Protestant (73.1%) and far
above Catholic (62.5%) -- consistent with the Church's emphasis on
religion as a daily, lived practice rather than a periodic observance.
Mormon n=88 (unweighted valid), comfortably above the 30-floor.

Checked against overlap with this dataset's existing charts (household-
arrangement items, prayer style qf6, annulment/Communion) -- distinct
construct, not previously used. Checked against CHIMPREL (importance of
religion *growing up*) already shipped elsewhere on the site (pew-rls-
2023-24, referenced in the pew-atp-w44-2018 exploration-log entry) --
that item asks about childhood, this one asks about the respondent's
life today; different construct, same top-line "importance" theme but
not a duplicate.

Denominator excludes only "don't know/refused" (qf2==9).

Usage: python scripts/pew-catholic-family-2015/religious_importance.py
"""
import json

import numpy as np
import pyreadstat

SAV = (
    "data/pew-catholic-family-2015/Dataset - Pew Research Center 2015 Survey "
    "of U.S. Catholics and Family Life - Version 1.1 - Mar 1, 2018.sav"
)

RELIG_CODES = {
    1.0: "Protestant",
    2.0: "Catholic",
    3.0: "Mormon",
    4.0: "Orthodox Christian",
    5.0: "Jewish",
    6.0: "Muslim",
    7.0: "Buddhist",
    8.0: "Hindu",
    9.0: "Atheist",
    10.0: "Agnostic",
    11.0: "Something else",
    12.0: "Nothing in particular",
    13.0: "Christian (unspecified)",
    15.0: "Jehovah's Witness",
}
MIN_VALID_N = 30
TOP_BOX = 1.0  # "very important"
VALID_CODES = {1.0, 2.0, 3.0, 4.0}  # excludes only don't know/refused (9)


def top_box_by_group(col, weight, relig):
    results = {}
    for code, label in RELIG_CODES.items():
        group_mask = relig == code
        valid = group_mask & np.isin(col, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        hit = valid & (col == TOP_BOX)
        results[label] = {
            "pct": round(100 * weight[hit].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }
    valid_all = np.isin(col, list(VALID_CODES))
    hit_all = valid_all & (col == TOP_BOX)
    results["U.S. adults"] = {
        "pct": round(100 * weight[hit_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(col)),
    }
    return results


def main():
    cols = ["relig", "qf2", "weight"]
    df, _ = pyreadstat.read_sav(SAV, usecols=cols)
    weight = df["weight"].to_numpy()
    relig = df["relig"].to_numpy()

    religion_very_important = top_box_by_group(df["qf2"].to_numpy(), weight, relig)

    out = {
        "source": "Pew Research Center. 2015 Survey of U.S. Catholics and Family Life, "
                  "fielded May 5-June 7, 2015.",
        "method": "Population is all respondents (a general-public sample with a Catholic "
                  "oversample), grouped by present religion (relig). qf2 asks how important "
                  "religion is in the respondent's life: very important, somewhat important, "
                  "not too important, or not at all important -- only don't know/refused is "
                  "excluded from the denominator. Share is top box ('very important'). Groups "
                  "under 30 valid respondents omitted -- Mormon N is thin (88 valid "
                  "respondents) and should be read directionally. Weighted by the dataset's "
                  "own weight variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "religion_very_important_pct": religion_very_important,
    }
    with open(
        "docs/datasets/pew-catholic-family-2015/religious-importance.json", "w", encoding="utf-8"
    ) as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label, r in religion_very_important.items():
        print(f"{label:25} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']})")
    print("\nWrote docs/datasets/pew-catholic-family-2015/religious-importance.json")


if __name__ == "__main__":
    main()

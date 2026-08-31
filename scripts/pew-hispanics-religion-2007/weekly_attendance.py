"""
"Aside from weddings and funerals, how often do you attend religious
services" (qn23) for the 2007 Pew Hispanic Center/Pew Forum "Changing
Faiths" survey of U.S. Latinos, broken out by the survey's own recoded
religion variable (relig). Reports the share attending at least once a
week ("more than once a week" or "once a week").

Latino Mormons attend weekly or more at 67.4%, 2nd only to Jehovah's
Witnesses (74.5%) and well above Protestants (63.0%) and Catholics (42.7%
- the group whose declining attendance and switching to Protestantism/no
religion drives this survey's headline finding).

Groups under 30 valid respondents are omitted (drops Muslim [n=2] and
Orthodox [n=3]). Weighted by the dataset's own newweight variable, which
corrects for a deliberate oversample of 2,000 non-Catholic respondents.

Usage: python scripts/pew-hispanics-religion-2007/weekly_attendance.py
"""
import json

import numpy as np
import pyreadstat

SAV = (
    "data/pew-hispanics-religion-2007/"
    "Pew Hispanic Center - Pew Forum Religion Survey Data 5-1-2008.sav"
)

RELIG_CODES = {
    0.0: "Unaffiliated",
    1.0: "Catholic",
    2.0: "Protestant",
    3.0: "Jehovah's Witness",
    4.0: "Mormon",
    5.0: "Jewish",
}
WEEKLY_PLUS = {1.0, 2.0}
VALID_CODES = {1.0, 2.0, 3.0, 4.0, 5.0, 6.0}
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["relig", "qn23", "newweight"])
    weight = df["newweight"].to_numpy()
    relig = df["relig"].to_numpy()
    q = df["qn23"].to_numpy()

    results = {}
    for code, label in RELIG_CODES.items():
        group_mask = relig == code
        valid = group_mask & np.isin(q, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        weekly = valid & np.isin(q, list(WEEKLY_PLUS))
        results[label] = {
            "pct": round(100 * weight[weekly].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    order = sorted(results, key=lambda label: -results[label]["pct"])

    out = {
        "source": "Pew Research Center (Pew Hispanic Center and Pew Forum on Religion & "
                  "Public Life). \"Changing Faiths: Latinos and the Transformation of "
                  "American Religion,\" survey of 4,016 U.S. Hispanic adults, fielded "
                  "Aug. 10-Oct. 4, 2006.",
        "method": "Population is Hispanic adults currently belonging to each religious "
                  "group (the survey's own recoded 'relig' variable). Share answering "
                  "\"More than once a week\" or \"Once a week\" (vs. less often/never) "
                  "to qn23, \"Aside from weddings and funerals, how often do you attend "
                  "religious services\"; don't know/refused excluded from each row's "
                  "denominator. Groups under 30 valid respondents omitted. Weighted by "
                  "the dataset's own newweight variable, which corrects for a deliberate "
                  "oversample of 2,000 non-Catholic respondents.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "weekly_or_more": results,
    }
    with open(
        "docs/datasets/pew-hispanics-religion-2007/weekly-attendance.json",
        "w", encoding="utf-8",
    ) as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:18} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-hispanics-religion-2007/weekly-attendance.json")


if __name__ == "__main__":
    main()

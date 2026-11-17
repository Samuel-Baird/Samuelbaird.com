"""
"How important would you say religion is in your own life" (qn24) for the
2007 Pew Hispanic Center/Pew Forum "Changing Faiths" survey of U.S. Latinos,
broken out by the survey's own recoded religion variable (relig).

Latino Mormons rate religion "very important" in their own life at 84.8%,
2nd only to Jehovah's Witnesses (92.1%) and well above Catholics (68.5%,
the group that gives this survey its Latino-religious-switching headline)
and the religiously unaffiliated (29.5%).

Groups under 30 valid respondents are omitted (drops Muslim [n=2] and
Orthodox [n=3]). Weighted by the dataset's own newweight variable, which
corrects for a deliberate oversample of 2,000 non-Catholic respondents.

Usage: python scripts/pew-hispanics-religion-2007/importance_of_religion.py
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
VERY_IMPORTANT = 1.0
VALID_CODES = {1.0, 2.0, 3.0}
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["relig", "qn24", "newweight"])
    weight = df["newweight"].to_numpy()
    relig = df["relig"].to_numpy()
    q24 = df["qn24"].to_numpy()

    results = {}
    for code, label in RELIG_CODES.items():
        group_mask = relig == code
        valid = group_mask & np.isin(q24, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        very_important = valid & (q24 == VERY_IMPORTANT)
        results[label] = {
            "pct": round(100 * weight[very_important].sum() / weight[valid].sum(), 2),
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
                  "\"Very important\" (vs. \"Fairly important\"/\"Not very important\") "
                  "to qn24, \"How important would you say religion is in your own life\"; "
                  "don't know/refused excluded from each row's denominator. Groups under "
                  "30 valid respondents omitted. Weighted by the dataset's own newweight "
                  "variable, which corrects for a deliberate oversample of 2,000 "
                  "non-Catholic respondents.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "very_important": results,
    }
    with open(
        "docs/datasets/pew-hispanics-religion-2007/importance-of-religion.json",
        "w", encoding="utf-8",
    ) as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:18} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-hispanics-religion-2007/importance-of-religion.json")


if __name__ == "__main__":
    main()

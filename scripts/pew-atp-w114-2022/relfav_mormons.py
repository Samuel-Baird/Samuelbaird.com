"""
ATP Wave 114 (September 2022): how favorably do Americans of different
religious backgrounds view Mormons? RELFAV_c_W114 is one item in Wave
114's RELFAV battery ("Please indicate whether you have a favorable or
unfavorable view of each of the following groups?"), asked of the full
sample regardless of the respondent's own religion. This chart breaks it
out by the respondent's own self-reported affiliation (F_RELIG) - unlike
essent_jesus.py and essent_attend.py in this folder, which look at what
Latter-day Saints themselves say, this one looks outward: how other
religious and non-religious groups perceive Latter-day Saints.

Like christian_nation.py in this same folder, this wave has no F_RELTRAD
frame variable, so the breakout uses F_RELIG.

Usage: python scripts/pew-atp-w114-2022/relfav_mormons.py
"""
import json

import numpy as np
import pyreadstat

SAV = "data/pew-atp-w114-2022/ATP W114.sav"

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
    11.0: "Other",
    12.0: "Nothing in particular",
}
FAVORABLE = {1.0, 2.0}
VALID_CODES = {1.0, 2.0, 3.0, 4.0, 5.0}
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(
        SAV, usecols=["F_RELIG", "RELFAV_c_W114", "WEIGHT_W114"]
    )
    weight = df["WEIGHT_W114"].to_numpy()
    relig = df["F_RELIG"].to_numpy()
    fav = df["RELFAV_c_W114"].to_numpy()

    results = {}
    for code, label in RELIG_CODES.items():
        group_mask = relig == code
        valid = group_mask & np.isin(fav, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        yes = valid & np.isin(fav, list(FAVORABLE))
        results[label] = {
            "pct": round(100 * weight[yes].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(fav, list(VALID_CODES))
    yes_all = valid_all & np.isin(fav, list(FAVORABLE))
    results["All U.S. adults"] = {
        "pct": round(100 * weight[yes_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }

    order = [label for label in results if label != "All U.S. adults"]
    order.sort(key=lambda label: -results[label]["pct"])
    order.append("All U.S. adults")

    out = {
        "source": "Pew Research Center. American Trends Panel Wave 114, fielded September "
                  "13-18, 2022.",
        "method": "Population is respondent's self-reported religious affiliation (F_RELIG) - "
                  "Wave 114 does not carry the finer F_RELTRAD frame variable used in other "
                  "ATP waves in this dataset family. Share with a very or somewhat favorable "
                  "view of Mormons (RELFAV_c_W114), among respondents who offered an opinion "
                  "(\"don't know enough to say\" and refused excluded from each row's "
                  "denominator). Groups under 30 valid respondents omitted. Weighted by the "
                  "dataset's own WEIGHT_W114 variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "favorable_toward_mormons": results,
    }
    with open(
        "docs/datasets/pew-atp-w114-2022/relfav-mormons.json", "w", encoding="utf-8"
    ) as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:26} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-atp-w114-2022/relfav-mormons.json")


if __name__ == "__main__":
    main()

"""
Fourth flagship chart for the 2014 Religious Landscape Study: how young is
each religious tradition's membership? Share born 1981-1996 (Millennials,
cohort5cat), by current religious tradition (RELTRAD). Groups with n < 30
valid respondents are dropped, same convention as
weekly_attendance.py/certainty_of_god.py in this folder.

Usage: python scripts/pew-rls-2014/millennial_share.py
"""
import json

import numpy as np
import pyreadstat

SAV = ("data/pew-rls-2014/"
       "Dataset - Pew Research Center 2014 Religious Landscape Study National Telephone "
       "Survey - Version 1.1 - December 1 2016.sav")

RELTRAD_CODES = {
    1100.0: "Evangelical Protestant Tradition",
    1200.0: "Mainline Protestant Tradition",
    1300.0: "Historically Black Protestant Tradition",
    10000.0: "Catholic",
    20000.0: "Mormon",
    30000.0: "Orthodox Christian",
    40001.0: "Jehovah's Witness",
    50000.0: "Jewish",
    60000.0: "Muslim",
    70000.0: "Buddhist",
    80000.0: "Hindu",
    100000.0: "Unaffiliated (religious \"nones\")",
}
MILLENNIAL = 5.0
VALID_CODES = {1.0, 2.0, 3.0, 4.0, 5.0}
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["RELTRAD", "cohort5cat", "WEIGHT"])
    weight = df["WEIGHT"].to_numpy()
    reltrad = df["RELTRAD"].to_numpy()
    cohort = df["cohort5cat"].to_numpy()

    results = {}
    for code, label in RELTRAD_CODES.items():
        group_mask = reltrad == code
        valid = group_mask & np.isin(cohort, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        millennial = valid & (cohort == MILLENNIAL)
        results[label] = {
            "pct": round(100 * weight[millennial].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(cohort, list(VALID_CODES))
    millennial_all = valid_all & (cohort == MILLENNIAL)
    results["All U.S. adults"] = {
        "pct": round(100 * weight[millennial_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }

    order = [label for label in results if label != "All U.S. adults"]
    order.sort(key=lambda label: -results[label]["pct"])
    order.append("All U.S. adults")

    out = {
        "source": 'Pew Research Center. 2015. "2014 Religious Landscape Study."',
        "method": "Population is current religious tradition (RELTRAD). Share born "
                  "1981-1996 (Millennials, cohort5cat); don't know/refused excluded from "
                  "each row's denominator. Groups with fewer than 30 valid respondents are "
                  "omitted. Weighted by the dataset's own national WEIGHT variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "millennial_pct": results,
    }
    with open("docs/datasets/pew-rls-2014/millennial-share.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:38} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-rls-2014/millennial-share.json")


if __name__ == "__main__":
    main()

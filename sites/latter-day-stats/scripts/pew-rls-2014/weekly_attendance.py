"""
Second flagship chart for the 2014 Religious Landscape Study: how often do
people attend religious services (ATTEND), by current religious tradition
(RELTRAD)? Top-two-box is "more than once a week" + "once a week" -
weekly or more. Groups with n < 30 valid respondents are dropped rather
than shown with an unreliable estimate, same convention as this site's
2010 Religious Knowledge Survey charts.

Usage: python scripts/pew-rls-2014/weekly_attendance.py
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
WEEKLY_CODES = {1.0, 2.0}
VALID_CODES = {1.0, 2.0, 3.0, 4.0, 5.0, 6.0}
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["RELTRAD", "attend", "WEIGHT"])
    weight = df["WEIGHT"].to_numpy()
    reltrad = df["RELTRAD"].to_numpy()
    attend = df["attend"].to_numpy()

    results = {}
    for code, label in RELTRAD_CODES.items():
        group_mask = reltrad == code
        valid = group_mask & np.isin(attend, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        weekly = valid & np.isin(attend, list(WEEKLY_CODES))
        results[label] = {
            "pct": round(100 * weight[weekly].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(attend, list(VALID_CODES))
    weekly_all = valid_all & np.isin(attend, list(WEEKLY_CODES))
    results["All U.S. adults"] = {
        "pct": round(100 * weight[weekly_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }

    order = [label for label in results if label != "All U.S. adults"]
    order.sort(key=lambda label: -results[label]["pct"])
    order.append("All U.S. adults")

    out = {
        "source": 'Pew Research Center. 2015. "2014 Religious Landscape Study."',
        "method": "Population is current religious tradition (RELTRAD). Weekly+ combines "
                  "\"more than once a week\" and \"once a week\" on ATTEND; don't know/"
                  "refused excluded from each row's denominator. Groups with fewer than 30 "
                  "valid respondents are omitted. Weighted by the dataset's own national "
                  "WEIGHT variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "attend_weekly": results,
    }
    with open("docs/datasets/pew-rls-2014/weekly-attendance.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:38} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-rls-2014/weekly-attendance.json")


if __name__ == "__main__":
    main()

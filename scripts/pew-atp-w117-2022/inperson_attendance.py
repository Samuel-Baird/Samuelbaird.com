"""
Flagship chart for ATP Wave 117 (November 2022): who attended religious
services in person in the past month? ATTENDMONTH_W117 asked "In the last
month, did you attend religious services in person at a church, synagogue,
mosque or other house of worship?" of all respondents; broken out by
F_RELTRAD. This is the same item (ATTENDMONTH_*) w70's
inperson_attendance_covid.py used for the July 2020 pandemic-lockdown
wave - here it's asked again two and a half years later, once in-person
attendance had substantially recovered, and Latter-day Saints report by
far the highest rate of any tradition in the wave (80% vs. the next
highest group's 50%). Groups under 30 valid respondents are dropped.

Usage: python scripts/pew-atp-w117-2022/inperson_attendance.py
"""
import json

import numpy as np
import pyreadstat

SAV = "data/pew-atp-w117-2022/ATP W117.sav"

RELTRAD_CODES = {
    1100.0: "Evangelical Protestant",
    1200.0: "Mainline Protestant",
    1300.0: "Historically Black Protestant",
    10000.0: "Catholic",
    20000.0: "Mormon",
    30000.0: "Orthodox Christian",
    50000.0: "Jewish",
    100000.0: "Unaffiliated",
}
YES = 1.0
VALID_CODES = {1.0, 2.0}
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["F_RELTRAD", "ATTENDMONTH_W117", "WEIGHT_W117"])
    weight = df["WEIGHT_W117"].to_numpy()
    reltrad = df["F_RELTRAD"].to_numpy()
    attended = df["ATTENDMONTH_W117"].to_numpy()

    results = {}
    for code, label in RELTRAD_CODES.items():
        group_mask = reltrad == code
        valid = group_mask & np.isin(attended, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        yes = valid & (attended == YES)
        results[label] = {
            "pct": round(100 * weight[yes].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(attended, list(VALID_CODES))
    yes_all = valid_all & (attended == YES)
    results["All U.S. adults"] = {
        "pct": round(100 * weight[yes_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }

    order = sorted(results, key=lambda label: -results[label]["pct"])
    order.remove("All U.S. adults")
    order.append("All U.S. adults")

    out = {
        "source": "Pew Research Center. American Trends Panel Wave 117, fielded November 16-27, 2022.",
        "method": "Population is respondent's religious tradition (F_RELTRAD). Share "
                  "answering \"yes\" to ATTENDMONTH_W117 (\"In the last month, did you "
                  "attend religious services in person at a church, synagogue, mosque or "
                  "other house of worship?\"); refused excluded from each row's "
                  "denominator. Groups under 30 valid respondents omitted. Weighted by "
                  "the dataset's own WEIGHT_W117 variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "attended_in_person": results,
    }
    with open("docs/datasets/pew-atp-w117-2022/inperson-attendance.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:26} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-atp-w117-2022/inperson-attendance.json")


if __name__ == "__main__":
    main()

"""
ATP Wave 117 (November 2022): who participates in in-person prayer groups,
scripture study groups, or religious education programs? NONTECH1_c_W117
asked "Do you ever do any of the following? Participate in in-person prayer
groups, scripture study groups or religious education programs" of all
respondents, broken out by F_RELTRAD. Latter-day Saints report by far the
highest rate of any tradition (57%) - consistent with the Church's emphasis
on ward-level Sunday School, Relief Society/Elders Quorum lessons, and
seminary/institute. Groups under 30 valid respondents are dropped.

Usage: python scripts/pew-atp-w117-2022/nontech_prayer_groups.py
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
    df, _ = pyreadstat.read_sav(SAV, usecols=["F_RELTRAD", "NONTECH1_c_W117", "WEIGHT_W117"])
    weight = df["WEIGHT_W117"].to_numpy()
    reltrad = df["F_RELTRAD"].to_numpy()
    does_it = df["NONTECH1_c_W117"].to_numpy()

    results = {}
    for code, label in RELTRAD_CODES.items():
        group_mask = reltrad == code
        valid = group_mask & np.isin(does_it, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        yes = valid & (does_it == YES)
        results[label] = {
            "pct": round(100 * weight[yes].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(does_it, list(VALID_CODES))
    yes_all = valid_all & (does_it == YES)
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
                  "answering \"yes, I do this\" to NONTECH1_c_W117 (\"Do you ever do any "
                  "of the following? Participate in in-person prayer groups, scripture "
                  "study groups or religious education programs\"); refused excluded from "
                  "each row's denominator. Groups under 30 valid respondents omitted. "
                  "Weighted by the dataset's own WEIGHT_W117 variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "participates_in_person_study_group": results,
    }
    with open("docs/datasets/pew-atp-w117-2022/nontech-prayer-groups.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:26} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-atp-w117-2022/nontech-prayer-groups.json")


if __name__ == "__main__":
    main()

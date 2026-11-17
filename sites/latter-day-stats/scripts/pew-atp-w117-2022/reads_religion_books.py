"""
ATP Wave 117 (November 2022): who reads religion-focused books at least
weekly? NONTECH2_b_W117 is a 7-point frequency scale ("Several times a
day" through "Less than once a month"), collapsed here to "at least once a
week" (codes 1-4) vs. less often (codes 5-7), broken out by F_RELTRAD.
Latter-day Saints report the highest rate of any Christian tradition (59%),
2nd only to Jewish respondents (74%, who clear the 30-respondent floor at
n=55) and well ahead of Historically Black Protestant (58%), Evangelical
Protestant (51%), and Catholic/Mainline Protestant (both ~40%) - a
companion to this wave's already-shipped `nontech-prayer-groups.json`
(participating in in-person study groups) that ties to the same personal/
family scripture-study culture but captures a distinct behavior (reading
alone vs. group participation). Groups under 30 valid respondents are
dropped.

Usage: python scripts/pew-atp-w117-2022/reads_religion_books.py
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
WEEKLY_PLUS = {1.0, 2.0, 3.0, 4.0}
VALID_CODES = {1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0}
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["F_RELTRAD", "NONTECH2_b_W117", "WEIGHT_W117"])
    weight = df["WEIGHT_W117"].to_numpy()
    reltrad = df["F_RELTRAD"].to_numpy()
    freq = df["NONTECH2_b_W117"].to_numpy()

    results = {}
    for code, label in RELTRAD_CODES.items():
        group_mask = reltrad == code
        valid = group_mask & np.isin(freq, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        weekly = valid & np.isin(freq, list(WEEKLY_PLUS))
        results[label] = {
            "pct": round(100 * weight[weekly].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(freq, list(VALID_CODES))
    weekly_all = valid_all & np.isin(freq, list(WEEKLY_PLUS))
    results["All U.S. adults"] = {
        "pct": round(100 * weight[weekly_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }

    order = sorted(results, key=lambda label: -results[label]["pct"])
    order.remove("All U.S. adults")
    order.append("All U.S. adults")

    out = {
        "source": "Pew Research Center. American Trends Panel Wave 117, fielded November 16-27, 2022.",
        "method": "Population is respondent's religious tradition (F_RELTRAD). Share "
                  "reading religion-focused books at least once a week (codes 1-4 of "
                  "NONTECH2_b_W117's 7-point frequency scale, from \"several times a "
                  "day\" through \"once a week\"), vs. less often; refused excluded "
                  "from each row's denominator. Groups under 30 valid respondents "
                  "omitted. Weighted by the dataset's own WEIGHT_W117 variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "reads_religion_books_weekly": results,
    }
    with open("docs/datasets/pew-atp-w117-2022/reads-religion-books.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:26} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-atp-w117-2022/reads-religion-books.json")


if __name__ == "__main__":
    main()

"""
Second flagship chart for Religion in Latin America: how often do people
attend religious services (Q45), by the respondent's own current religion
(QCURRELrec)? Weekly+ combines "more than once a week" and "once a week."
Population is pooled across all 18 Latin American/Caribbean countries and
Puerto Rico, same scope as mormons_as_christian.py in this folder.

Usage: python scripts/pew-latin-america-2014/weekly_attendance.py
"""
import json

import numpy as np
import pyreadstat

SAV = "data/pew-latin-america-2014/Religion in Latin America Dataset.sav"

RELIGION_CODES = {1.0: "Catholic", 2.0: "Protestant/Evangelical", 3.0: "Other religion", 4.0: "Unaffiliated"}
WEEKLY_CODES = {1.0, 2.0}
VALID_CODES = {1.0, 2.0, 3.0, 4.0, 5.0, 6.0}


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["QCURRELrec", "Q45", "WEIGHT"])
    weight = df["WEIGHT"].to_numpy()
    religion = df["QCURRELrec"].to_numpy()
    attend = df["Q45"].to_numpy()

    results = {}
    for code, label in RELIGION_CODES.items():
        group_mask = religion == code
        valid = group_mask & np.isin(attend, list(VALID_CODES))
        weekly = valid & np.isin(attend, list(WEEKLY_CODES))
        results[label] = {
            "pct": round(100 * weight[weekly].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(attend, list(VALID_CODES))
    weekly_all = valid_all & np.isin(attend, list(WEEKLY_CODES))
    results["All respondents"] = {
        "pct": round(100 * weight[weekly_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }

    order = sorted(results, key=lambda label: -results[label]["pct"])
    order.remove("All respondents")
    order.append("All respondents")

    out = {
        "source": 'Pew Research Center. 2014. "Religion in Latin America: Widespread Change '
                  'in a Historically Catholic Region."',
        "method": "Population is respondent's own current religion (QCURRELrec), pooled "
                  "across all 18 Latin American/Caribbean countries and Puerto Rico. "
                  "Weekly+ combines \"more than once a week\" and \"once a week\" on Q45; "
                  "don't know/refused excluded from each row's denominator. Weighted by the "
                  "dataset's own combined base/post-stratification WEIGHT.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "attend_weekly": results,
    }
    with open("docs/datasets/pew-latin-america-2014/weekly-attendance.json",
              "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:26} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>6})")
    print("\nWrote docs/datasets/pew-latin-america-2014/weekly-attendance.json")


if __name__ == "__main__":
    main()

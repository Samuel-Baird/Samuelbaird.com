"""
Sixth flagship chart for the 2014 RLS recontact survey: how much did the
respondent's parents (or guardians) talk about religion when they were
growing up (qb15), by current religious tradition (reltrad)? Top box is
"a lot." Same population/threshold conventions as raised_interfaith.py in
this folder: groups under 30 valid respondents are dropped (this recontact
reached only 5,000 of the main 2014 RLS's 35,071 respondents).

Usage: python scripts/pew-rls-2014-recontact/parents_talked_religion.py
"""
import json

import numpy as np
import pyreadstat

SAV = "data/pew-rls-2014-recontact/RLS II recontact public release.sav"

RELTRAD_CODES = {
    1100.0: "Evangelical Protestant",
    1200.0: "Mainline Protestant",
    1300.0: "Historically Black Protestant",
    10000.0: "Catholic",
    20000.0: "Mormon",
    100000.0: "Unaffiliated",
}
A_LOT = 1.0
VALID_CODES = {1.0, 2.0, 3.0, 4.0}  # excludes "Undesignated" (8.0) and don't know/refused (9.0)
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["reltrad", "qb15", "rweight"])
    weight = df["rweight"].to_numpy()
    reltrad = df["reltrad"].to_numpy()
    talked = df["qb15"].to_numpy()

    results = {}
    for code, label in RELTRAD_CODES.items():
        group_mask = reltrad == code
        valid = group_mask & np.isin(talked, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        a_lot = valid & (talked == A_LOT)
        results[label] = {
            "pct": round(100 * weight[a_lot].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(talked, list(VALID_CODES))
    a_lot_all = valid_all & (talked == A_LOT)
    results["All U.S. adults"] = {
        "pct": round(100 * weight[a_lot_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }

    order = sorted(results, key=lambda label: -results[label]["pct"])
    order.remove("All U.S. adults")
    order.append("All U.S. adults")

    out = {
        "source": 'Pew Research Center. 2016. "One-in-Five U.S. Adults Were Raised in '
                  'Interfaith Homes."',
        "method": "Population is current religious tradition (reltrad). qb15 asks how much "
                  "the respondent's parents/guardians talked about religion when the "
                  "respondent was growing up; this reads the \"a lot\" top box. "
                  "\"Undesignated\" and don't know/refused excluded from each row's "
                  "denominator. Groups under 30 valid respondents omitted (this recontact "
                  "reached only 5,000 of the main 2014 RLS's 35,071 respondents). Weighted "
                  "by the dataset's own `rweight` variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "parents_talked_religion_a_lot": results,
    }
    with open("docs/datasets/pew-rls-2014-recontact/parents-talked-religion.json",
              "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:32} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>4})")
    print("\nWrote docs/datasets/pew-rls-2014-recontact/parents-talked-religion.json")


if __name__ == "__main__":
    main()

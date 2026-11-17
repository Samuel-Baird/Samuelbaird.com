"""
Seventh flagship chart for the 2014 RLS recontact survey: since turning
18, has the respondent ever gone through a period of attending religious
services LESS often than they do now (qc9), by current religious
tradition (reltrad)? A lower share reflects a more stable, unbroken
lifelong attendance pattern. Same population/threshold conventions as
raised_interfaith.py in this folder: groups under 30 valid respondents
are dropped (this recontact reached only 5,000 of the main 2014 RLS's
35,071 respondents).

Usage: python scripts/pew-rls-2014-recontact/attendance_stability.py
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
YES_ATTENDED_LESS = 1.0
VALID_CODES = {1.0, 2.0}  # excludes don't know/refused (9.0)
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["reltrad", "qc9", "rweight"])
    weight = df["rweight"].to_numpy()
    reltrad = df["reltrad"].to_numpy()
    attended_less = df["qc9"].to_numpy()

    results = {}
    for code, label in RELTRAD_CODES.items():
        group_mask = reltrad == code
        valid = group_mask & np.isin(attended_less, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        yes = valid & (attended_less == YES_ATTENDED_LESS)
        results[label] = {
            "pct": round(100 * weight[yes].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(attended_less, list(VALID_CODES))
    yes_all = valid_all & (attended_less == YES_ATTENDED_LESS)
    results["All U.S. adults"] = {
        "pct": round(100 * weight[yes_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }

    order = sorted(results, key=lambda label: -results[label]["pct"])
    order.remove("All U.S. adults")
    order.append("All U.S. adults")

    out = {
        "source": 'Pew Research Center. 2016. "One-in-Five U.S. Adults Were Raised in '
                  'Interfaith Homes."',
        "method": "Population is current religious tradition (reltrad). qc9 asks whether, "
                  "since turning 18, there has ever been a time the respondent attended "
                  "religious services LESS often than they do now; this reads the \"yes\" "
                  "share, i.e. the share whose attendance has ever lapsed. Don't know/refused "
                  "excluded from each row's denominator. Groups under 30 valid respondents "
                  "omitted (this recontact reached only 5,000 of the main 2014 RLS's 35,071 "
                  "respondents). Weighted by the dataset's own `rweight` variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "ever_attended_less_since_18": results,
    }
    with open("docs/datasets/pew-rls-2014-recontact/attendance-stability.json",
              "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:32} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>4})")
    print("\nWrote docs/datasets/pew-rls-2014-recontact/attendance-stability.json")


if __name__ == "__main__":
    main()

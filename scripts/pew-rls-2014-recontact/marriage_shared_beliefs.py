"""
Flagship chart for the 2014 RLS recontact survey: how important is sharing
religious beliefs with a spouse, by religious tradition? qd1g asked
"whether it is very important, somewhat important, or not important for a
successful marriage" that a couple share religious beliefs - this reads
the "very important" (top box) share. Population is current religious
tradition (reltrad); groups under 30 valid respondents are dropped (this
survey recontacted only 5,000 of the main 2014 RLS's 35,071 respondents,
so several traditions here are too thin to report - e.g. Muslim, Buddhist,
Hindu, Orthodox, Jehovah's Witness all land under 20 unweighted cases).

Usage: python scripts/pew-rls-2014-recontact/marriage_shared_beliefs.py
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
    50000.0: "Jewish",
    100000.0: "Unaffiliated",
}
VERY_IMPORTANT = 1.0
VALID_CODES = {1.0, 2.0, 3.0}
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["reltrad", "qd1g", "rweight"])
    weight = df["rweight"].to_numpy()
    reltrad = df["reltrad"].to_numpy()
    shared = df["qd1g"].to_numpy()

    results = {}
    for code, label in RELTRAD_CODES.items():
        group_mask = reltrad == code
        valid = group_mask & np.isin(shared, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        very = valid & (shared == VERY_IMPORTANT)
        results[label] = {
            "pct": round(100 * weight[very].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(shared, list(VALID_CODES))
    very_all = valid_all & (shared == VERY_IMPORTANT)
    results["All U.S. adults"] = {
        "pct": round(100 * weight[very_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }

    order = sorted(results, key=lambda label: -results[label]["pct"])
    order.remove("All U.S. adults")
    order.append("All U.S. adults")

    out = {
        "source": 'Pew Research Center. 2016. "One-in-Five U.S. Adults Were Raised in '
                  'Interfaith Homes."',
        "method": "Population is current religious tradition (reltrad). Cutpoint is top "
                  "box (\"very important\") on qd1g (\"shared religious beliefs\" for a "
                  "successful marriage); don't know/refused excluded from each row's "
                  "denominator. Groups under 30 valid respondents omitted (this recontact "
                  "reached only 5,000 of the main 2014 RLS's 35,071 respondents). Weighted "
                  "by the dataset's own `rweight` variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "shared_beliefs_very_important": results,
    }
    with open("docs/datasets/pew-rls-2014-recontact/marriage-shared-beliefs.json",
              "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:32} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>4})")
    print("\nWrote docs/datasets/pew-rls-2014-recontact/marriage-shared-beliefs.json")


if __name__ == "__main__":
    main()

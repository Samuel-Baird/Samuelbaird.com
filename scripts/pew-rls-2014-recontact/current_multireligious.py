"""
Third pass on the 2014 RLS recontact survey: how many people CURRENTLY think
of themselves as belonging to more than one religion (qb21), by current
religious tradition (reltrad)? Distinct construct from raised_interfaith.py's
qb19 (raised in more than one religion growing up) - that one is about
childhood upbringing, this one is about current self-identification. Same
population/threshold conventions as the rest of this folder: this recontact
reached only 5,000 of the main 2014 RLS's 35,071 respondents, so groups under
30 valid respondents are dropped rather than shown with an unreliable
estimate.

Usage: python scripts/pew-rls-2014-recontact/current_multireligious.py
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
BELONGS_MULTIPLE = 1.0
VALID_CODES = {1.0, 2.0}  # excludes "(VOL) not part of any religion" (3.0) - not applicable
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["reltrad", "qb21", "rweight"])
    weight = df["rweight"].to_numpy()
    reltrad = df["reltrad"].to_numpy()
    belongs = df["qb21"].to_numpy()

    results = {}
    for code, label in RELTRAD_CODES.items():
        group_mask = reltrad == code
        valid = group_mask & np.isin(belongs, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        multi = valid & (belongs == BELONGS_MULTIPLE)
        results[label] = {
            "pct": round(100 * weight[multi].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(belongs, list(VALID_CODES))
    multi_all = valid_all & (belongs == BELONGS_MULTIPLE)
    results["All U.S. adults"] = {
        "pct": round(100 * weight[multi_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }

    order = sorted(results, key=lambda label: -results[label]["pct"])
    order.remove("All U.S. adults")
    order.append("All U.S. adults")

    out = {
        "source": 'Pew Research Center, 2015 Religious Landscape Study Recontact Survey.',
        "method": "Population is current religious tradition (reltrad). qb21 asks whether "
                  "the respondent CURRENTLY thinks of themself as belonging to more than one "
                  "religion (a distinct construct from qb19's \"raised in more than one "
                  "religion,\" already charted separately); \"(VOL) not part of any religion\" "
                  "and don't know/refused excluded from each row's denominator. Groups under "
                  "30 valid respondents omitted (this recontact reached only 5,000 of the main "
                  "2014 RLS's 35,071 respondents). Weighted by the dataset's own `rweight` "
                  "variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "current_multireligious": results,
    }
    with open("docs/datasets/pew-rls-2014-recontact/current-multireligious.json",
              "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:32} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>4})")
    print("\nWrote docs/datasets/pew-rls-2014-recontact/current-multireligious.json")


if __name__ == "__main__":
    main()

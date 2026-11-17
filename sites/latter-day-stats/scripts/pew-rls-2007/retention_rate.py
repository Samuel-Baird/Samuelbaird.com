"""
Fourth flagship chart for the 2007 U.S. Religious Landscape Survey: of
people raised in a given tradition, what share still identify with that
same tradition as adults? Childhood tradition comes from q50 ("in what
religion were you raised") collapsed to five coarse buckets - Protestant
(any denomination), Catholic, Mormon, Jewish, and Unaffiliated (atheist +
agnostic + nothing in particular collapsed) - since q50 doesn't split
Protestants into Evangelical/Mainline/Historically Black the way current
RELTRAD does; retention is measured as "still in the same coarse bucket
today" using current RELTRAD collapsed the same way. This is coarser than
a full RELTRAD-to-RELTRAD retention matrix (which would need Pew's own
FAMILY-based childhood classification, not available in this file) but
answers the same "did people raised X stay X" question for the traditions
where q50's granularity allows it.

Usage: python scripts/pew-rls-2007/retention_rate.py
"""
import json

import numpy as np
import pyreadstat

SAV = "data/pew-rls-2007/Religious Landscape Survey Data - Continental US.sav"

RAISED_CODES = {
    "Protestant": [1.0],
    "Catholic": [2.0],
    "Mormon": [3.0],
    "Jewish": [5.0],
    "Unaffiliated": [9.0, 10.0, 12.0],
}
CURRENT_CODES = {
    "Protestant": [1100.0, 1200.0, 1300.0],
    "Catholic": [10000.0],
    "Mormon": [20000.0],
    "Jewish": [50000.0],
    "Unaffiliated": [100000.0],
}


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["reltrad", "q50", "weight"])
    weight = df["weight"].to_numpy()
    reltrad = df["reltrad"].to_numpy()
    raised = df["q50"].to_numpy()

    results = {}
    for label, raised_codes in RAISED_CODES.items():
        raised_mask = np.isin(raised, raised_codes)
        retained = raised_mask & np.isin(reltrad, CURRENT_CODES[label])
        results[label] = {
            "pct": round(100 * weight[retained].sum() / weight[raised_mask].sum(), 2),
            "raised_unweighted_n": int(raised_mask.sum()),
        }

    order = sorted(results, key=lambda label: -results[label]["pct"])

    out = {
        "source": 'Pew Research Center. 2008. "U.S. Religious Landscape Survey."',
        "method": "Raised tradition is q50 (\"in what religion were you raised\") collapsed "
                  "to five coarse buckets (Protestant of any denomination, Catholic, "
                  "Mormon, Jewish, Unaffiliated); retention is the share of each raised "
                  "bucket whose current tradition (RELTRAD) falls in the matching coarse "
                  "bucket. Continental-US main survey only. Weighted by the dataset's own "
                  "`weight` variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "retained_pct": results,
    }
    with open("docs/datasets/pew-rls-2007/retention-rate.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:14} {r['pct']:5.1f}%  (raised n={r['raised_unweighted_n']:>6})")
    print("\nWrote docs/datasets/pew-rls-2007/retention-rate.json")


if __name__ == "__main__":
    main()

"""
ATP Wave 143 (February 2024): 'religion encourages tolerance' vs. 'religion
encourages intolerance' (RELIMPCT_TOL_W143), by religion (F_RELIG); share
choosing tolerance. Latter-day Saints (84%) are the most likely of any group
to say religion encourages tolerance. The sibling RELIMPCT_SOC item (helps
vs. hurts society) is skipped as a near-duplicate of the live 2007 RLS
'religion causes more problems than it solves' chart.

Same population, F_RELIG group set, MIN_VALID_N floor, and JSON shape as
religious_minority.py in this folder (this wave has no F_RELTRAD).

Usage: python scripts/pew-atp-w143-2024/religion_encourages_tolerance.py
"""
import json

import numpy as np
import pyreadstat

SAV = "data/pew-atp-w143-2024/ATP W143.sav"

RELIG_CODES = {
    1.0: "Protestant",
    2.0: "Catholic",
    3.0: "Mormon",
    4.0: "Orthodox Christian",
    5.0: "Jewish",
    6.0: "Muslim",
    7.0: "Buddhist",
    8.0: "Hindu",
    9.0: "Atheist",
    10.0: "Agnostic",
    11.0: "Other",
    12.0: "Nothing in particular",
}
ITEM = "RELIMPCT_TOL_W143"
YES_CODES = {1.0}  # Religion encourages tolerance
VALID_CODES = {1.0, 2.0}  # encourages tolerance / encourages intolerance; refused excluded
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["F_RELIG", ITEM, "WEIGHT_W143"])
    weight = df["WEIGHT_W143"].to_numpy()
    relig = df["F_RELIG"].to_numpy()
    x = df[ITEM].to_numpy()

    results = {}
    for code, label in RELIG_CODES.items():
        group_mask = relig == code
        valid = group_mask & np.isin(x, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        yes = valid & np.isin(x, list(YES_CODES))
        results[label] = {
            "pct": round(100 * weight[yes].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(x, list(VALID_CODES))
    yes_all = valid_all & np.isin(x, list(YES_CODES))
    results["U.S. adults"] = {
        "pct": round(100 * weight[yes_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }

    out = {
        "source": "Pew Research Center. American Trends Panel Wave 143, fielded Feb. 13-25, 2024.",
        "method": "Population is all respondents, grouped by religious affiliation (F_RELIG) - "
                  "this wave does not carry the F_RELTRAD frame variable other ATP waves in this "
                  "repo use. Share choosing 'religion encourages tolerance' over 'religion encourages intolerance,' RELIMPCT_TOL_W143; refused excluded from each row's denominator. Groups under "
                  "30 valid respondents omitted. Weighted by the dataset's own WEIGHT_W143 "
                  "variable.",
        "total_weighted_n": float(weight[valid_all].sum()),
        "total_unweighted_n": int(valid_all.sum()),
        "group_order": list(results.keys()),
        "religion_encourages_tolerance": results,
    }
    with open("docs/datasets/pew-atp-w143-2024/religion-encourages-tolerance.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label, r in sorted(results.items(), key=lambda kv: -kv[1]["pct"]):
        print(f"{label:24} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-atp-w143-2024/religion-encourages-tolerance.json")


if __name__ == "__main__":
    main()

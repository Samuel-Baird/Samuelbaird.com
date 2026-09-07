"""
ATP Wave 132 (July 31-Aug. 6, 2023): 'Over the course of your lifetime, have
you generally become more religious, become less religious, some of both,
or stayed about the same?' (LIFEDIR_W132), by religion (F_RELIG); share
saying more religious. Latter-day Saints (49%) are twice the national 24%
and only 18% say less religious (vs. 34%) - a lifetime trajectory that runs
the opposite direction from the country as a whole. Note this is asked of
current members, so people who left the Church appear in other rows.

Same F_RELIG frame, MIN_VALID_N floor, and JSON shape as
spirituality_important.py in this folder (Wave 132 has no F_RELTRAD).
group_order is sorted here via chart_style.sort_groups (highest to lowest,
"U.S. adults" pinned to the bottom) because this folder's render scripts
read it as-is.

Usage: python scripts/pew-atp-w132-2023/more_religious_over_lifetime.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pyreadstat

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from chart_style import sort_groups  # noqa: E402

SAV = "data/pew-atp-w132-2023/ATP W132.sav"

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
ITEM = "LIFEDIR_W132"
YES_CODES = {1.0}  # Become more religious
VALID_CODES = {1.0, 2.0, 3.0, 4.0}  # more / less / some of both / same; refused excluded
MIN_VALID_N = 30
ALL_LABEL = "U.S. adults"


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["F_RELIG", ITEM, "WEIGHT_W132"])
    weight = df["WEIGHT_W132"].to_numpy()
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
    results[ALL_LABEL] = {
        "pct": round(100 * weight[yes_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }
    order = sort_groups(list(results.keys()), lambda label: results[label]["pct"])

    out = {
        "source": "Pew Research Center. American Trends Panel Wave 132, fielded July 31-Aug. 6, 2023.",
        "method": "Population is all respondents, grouped by religious affiliation (F_RELIG; this "
                  "wave has no F_RELTRAD). Share saying they have generally become more religious over the course of their lifetime (vs. less religious, some of both, or stayed about the same), LIFEDIR_W132; refused excluded from each row's denominator. "
                  "Groups under 30 valid respondents omitted. Weighted by the dataset's own "
                  "WEIGHT_W132 variable.",
        "total_weighted_n": float(weight[valid_all].sum()),
        "total_unweighted_n": int(valid_all.sum()),
        "group_order": order,
        "more_religious_over_lifetime": results,
    }
    with open("docs/datasets/pew-atp-w132-2023/more-religious-over-lifetime.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:24} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-atp-w132-2023/more-religious-over-lifetime.json")


if __name__ == "__main__":
    main()

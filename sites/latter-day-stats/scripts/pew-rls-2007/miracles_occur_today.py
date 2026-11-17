"""
2007 U.S. Religious Landscape Survey: "Miracles still occur today as in
ancient times" (q39a), by current religious tradition (RELTRAD); share who
COMPLETELY agree (the sibling angels-demons chart in this folder uses
completely-or-mostly; the top box is used here because agreement on
miracles is near-universal among Christians and only the strongest form
separates traditions). Latter-day Saint teaching holds that the gifts of
the Spirit, including healing and miracles, continue in the restored
Church (Moroni 7:27-37; Articles of Faith 1:7), and members are the most
likely of any tradition to completely agree.

Row order via chart_style.sort_groups (highest to lowest, "All U.S. adults"
pinned to the bottom). Same population, weighting, and JSON shape as
divine_healing_witnessed.py in this folder.

Usage: python scripts/pew-rls-2007/miracles_occur_today.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pyreadstat

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from chart_style import sort_groups  # noqa: E402

SAV = "data/pew-rls-2007/Religious Landscape Survey Data - Continental US.sav"

RELTRAD_CODES = {
    1100.0: "Evangelical Protestant Churches",
    1200.0: "Mainline Protestant Churches",
    1300.0: "Historically Black Protestant Churches",
    10000.0: "Catholic",
    20000.0: "Mormon",
    30000.0: "Orthodox",
    40001.0: "Jehovah's Witness",
    50000.0: "Jewish",
    60000.0: "Muslim",
    70000.0: "Buddhist",
    80000.0: "Hindu",
    100000.0: "Unaffiliated",
}
ITEM = "q39a"
YES_CODES = {1.0}  # Completely agree
VALID_CODES = {1.0, 2.0, 3.0, 4.0}  # completely/mostly agree, mostly/completely disagree; 9 = DK/refused excluded
MIN_VALID_N = 30
ALL_LABEL = "All U.S. adults"


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["reltrad", ITEM, "weight"])
    weight = df["weight"].to_numpy()
    reltrad = df["reltrad"].to_numpy()
    x = df[ITEM].to_numpy()

    results = {}
    for code, label in RELTRAD_CODES.items():
        group_mask = reltrad == code
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
        "source": 'Pew Research Center. 2008. "U.S. Religious Landscape Survey."',
        "method": "Population is current religious tradition (RELTRAD), continental-US main "
                  "survey only. q39a asked whether the respondent agrees that miracles still occur today as in ancient times; shown here is the share who completely agree (vs. mostly agree, mostly disagree, or completely disagree). Don't know/refused are excluded from each row's "
                  "denominator. Groups with fewer than 30 valid respondents are omitted. "
                  "Weighted by the dataset's own `weight` variable.",
        "total_weighted_n": float(weight[valid_all].sum()),
        "total_unweighted_n": int(valid_all.sum()),
        "group_order": order,
        "miracles_completely_agree": results,
    }
    with open("docs/datasets/pew-rls-2007/miracles-occur-today.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:38} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-rls-2007/miracles-occur-today.json")


if __name__ == "__main__":
    main()

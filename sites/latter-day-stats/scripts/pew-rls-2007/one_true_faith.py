"""
2007 U.S. Religious Landscape Survey: "My religion is the one, true faith
leading to eternal life" vs. "Many religions can lead to eternal life"
(q40a), by current religious tradition (RELTRAD); share choosing the first.
Asked of religiously affiliated respondents. The Church teaches that it is
"the only true and living church upon the face of the whole earth" (D&C
1:30) while also teaching that all people will have the opportunity to accept
the gospel in this life or the next - so how members answer a forced-choice
exclusivity item is a genuine question, not a foregone conclusion. Distinct
from the 2014 chart on whether NON-CHRISTIAN religions can lead to eternal
life (qh2), which is a follow-up asked only of those who chose 'many
religions.'

Row order via chart_style.sort_groups (highest to lowest, "All U.S. adults"
pinned to the bottom). Same population, weighting, and JSON shape as
divine_healing_witnessed.py in this folder.

Usage: python scripts/pew-rls-2007/one_true_faith.py
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
ITEM = "q40a"
YES_CODES = {1.0}  # My religion is the one, true faith leading to eternal life
VALID_CODES = {1.0, 2.0, 3.0}  # first / second / (vol) neither-both; 9 = DK/refused excluded
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
                  "survey only. q40a asked which statement comes closer to the respondent's views: 'my religion is the one, true faith leading to eternal life' or 'many religions can lead to eternal life'; shown here is the share choosing the first (volunteered neither/both kept in the base). Don't know/refused are excluded from each row's "
                  "denominator. Groups with fewer than 30 valid respondents are omitted. "
                  "Weighted by the dataset's own `weight` variable.",
        "total_weighted_n": float(weight[valid_all].sum()),
        "total_unweighted_n": int(valid_all.sum()),
        "group_order": order,
        "one_true_faith": results,
    }
    with open("docs/datasets/pew-rls-2007/one-true-faith.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:38} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-rls-2007/one-true-faith.json")


if __name__ == "__main__":
    main()

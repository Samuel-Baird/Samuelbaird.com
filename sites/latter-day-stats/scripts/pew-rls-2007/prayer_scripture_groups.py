"""
2007 U.S. Religious Landscape Survey: how often do people participate in
prayer groups, Scripture study groups, or religious education programs
(q42a), by current religious tradition (RELTRAD)? Top box is "at least once
a week." Organized weekly scripture study - Sunday School, seminary,
institute, adult religion classes - is a distinctive structural feature of
Latter-day Saint practice, so this item checks that emphasis against every
other tradition's own rate of group religious-education participation.

Usage: python scripts/pew-rls-2007/prayer_scripture_groups.py
"""
import json

import numpy as np
import pyreadstat

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
TOP_BOX = {1.0}  # at least once a week
VALID_CODES = {1.0, 2.0, 3.0, 4.0, 5.0}
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["reltrad", "q42a", "weight"])
    weight = df["weight"].to_numpy()
    reltrad = df["reltrad"].to_numpy()
    q42a = df["q42a"].to_numpy()

    results = {}
    for code, label in RELTRAD_CODES.items():
        group_mask = reltrad == code
        valid = group_mask & np.isin(q42a, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        weekly = valid & np.isin(q42a, list(TOP_BOX))
        results[label] = {
            "pct": round(100 * weight[weekly].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(q42a, list(VALID_CODES))
    weekly_all = valid_all & np.isin(q42a, list(TOP_BOX))
    results["All U.S. adults"] = {
        "pct": round(100 * weight[weekly_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }

    order = [label for label in results if label != "All U.S. adults"]
    order.sort(key=lambda label: -results[label]["pct"])
    order.append("All U.S. adults")

    out = {
        "source": 'Pew Research Center. 2008. "U.S. Religious Landscape Survey."',
        "method": "Population is current religious tradition (RELTRAD), continental-US main "
                  "survey only. q42a asked how often the respondent participates in prayer "
                  "groups, Scripture study groups, or religious education programs; top box is "
                  "\"at least once a week.\" Don't know/refused are excluded from each row's "
                  "denominator. Groups with fewer than 30 valid respondents are omitted. "
                  "Weighted by the dataset's own `weight` variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "weekly_prayer_or_scripture_group": results,
    }
    with open(
        "docs/datasets/pew-rls-2007/prayer-scripture-groups.json", "w", encoding="utf-8"
    ) as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:34} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-rls-2007/prayer-scripture-groups.json")


if __name__ == "__main__":
    main()

"""
2007 U.S. Religious Landscape Survey: how often do you share your faith with
non-believers or people from other religious backgrounds (q42d), by current
religious tradition (RELTRAD)? Latter-day Saints are best known among outside
observers for full-time proselytizing missionary service, but this item
checks everyday member-missionary behavior - sharing faith personally,
outside any formal mission - against every other tradition's own rate.

Usage: python scripts/pew-rls-2007/share_faith_nonbelievers.py
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
WEEKLY_PLUS_CODES = {1.0, 2.0}  # at least once a week, once or twice a month
VALID_CODES = {1.0, 2.0, 3.0, 4.0, 5.0}
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["reltrad", "q42d", "weight"])
    weight = df["weight"].to_numpy()
    reltrad = df["reltrad"].to_numpy()
    q42d = df["q42d"].to_numpy()

    results = {}
    for code, label in RELTRAD_CODES.items():
        group_mask = reltrad == code
        valid = group_mask & np.isin(q42d, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        weekly_plus = valid & np.isin(q42d, list(WEEKLY_PLUS_CODES))
        results[label] = {
            "pct": round(100 * weight[weekly_plus].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(q42d, list(VALID_CODES))
    weekly_all = valid_all & np.isin(q42d, list(WEEKLY_PLUS_CODES))
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
                  "survey only. q42d asked how often the respondent shares their faith with "
                  "non-believers or people from other religious backgrounds; shown here is the "
                  "share answering \"at least once a week\" or \"once or twice a month.\" "
                  "Don't know/refused are excluded from each row's denominator. Unaffiliated "
                  "respondents have no valid cases (item not meaningfully asked of them). "
                  "Groups with fewer than 30 valid respondents are omitted. Weighted by the "
                  "dataset's own `weight` variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "shares_faith_monthly_plus": results,
    }
    with open(
        "docs/datasets/pew-rls-2007/share-faith-nonbelievers.json", "w", encoding="utf-8"
    ) as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:34} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-rls-2007/share-faith-nonbelievers.json")


if __name__ == "__main__":
    main()

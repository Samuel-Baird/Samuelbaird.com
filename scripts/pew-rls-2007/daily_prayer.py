"""
Third flagship chart for the 2007 U.S. Religious Landscape Survey: how
many people pray outside of religious services at least once a day (q41,
"several times a day" or "once a day"), by current religious tradition
(RELTRAD)? Same scope as evolution_belief.py and certainty_of_god.py in
this folder: population is RELTRAD, continental-US main survey only.

Usage: python scripts/pew-rls-2007/daily_prayer.py
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
DAILY_CODES = {1.0, 2.0}  # several times a day, once a day
VALID_CODES = {1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0}


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["reltrad", "q41", "weight"])
    weight = df["weight"].to_numpy()
    reltrad = df["reltrad"].to_numpy()
    prayer = df["q41"].to_numpy()

    results = {}
    for code, label in RELTRAD_CODES.items():
        group_mask = reltrad == code
        valid = group_mask & np.isin(prayer, list(VALID_CODES))
        daily = valid & np.isin(prayer, list(DAILY_CODES))
        results[label] = {
            "pct": round(100 * weight[daily].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(prayer, list(VALID_CODES))
    daily_all = valid_all & np.isin(prayer, list(DAILY_CODES))
    results["All U.S. adults"] = {
        "pct": round(100 * weight[daily_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }

    order = sorted(results, key=lambda label: -results[label]["pct"])
    order.remove("All U.S. adults")
    order.append("All U.S. adults")

    out = {
        "source": 'Pew Research Center. 2008. "U.S. Religious Landscape Survey."',
        "method": "Population is current religious tradition (RELTRAD), continental-US main "
                  "survey only. q41 asks how often respondents pray outside of religious "
                  "services; daily+ combines \"several times a day\" and \"once a day.\" "
                  "Don't know/refused excluded from each row's denominator. Weighted by the "
                  "dataset's own `weight` variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "pray_daily": results,
    }
    with open("docs/datasets/pew-rls-2007/daily-prayer.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:34} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-rls-2007/daily-prayer.json")


if __name__ == "__main__":
    main()

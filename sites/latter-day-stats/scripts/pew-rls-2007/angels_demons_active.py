"""
2007 U.S. Religious Landscape Survey: "Angels and demons are active in the
world" (q39b), agree vs. disagree, by current religious tradition (RELTRAD).
Latter-day Saint scripture and doctrine are unusually rich in accounts of
literal angelic ministration (Moroni's visits to Joseph Smith chief among
them) and a personal, active adversary, so this item checks that belief
against every other tradition's own rate.

Usage: python scripts/pew-rls-2007/angels_demons_active.py
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
AGREE_CODES = {1.0, 2.0}  # completely agree, mostly agree
VALID_CODES = {1.0, 2.0, 3.0, 4.0}
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["reltrad", "q39b", "weight"])
    weight = df["weight"].to_numpy()
    reltrad = df["reltrad"].to_numpy()
    q39b = df["q39b"].to_numpy()

    results = {}
    for code, label in RELTRAD_CODES.items():
        group_mask = reltrad == code
        valid = group_mask & np.isin(q39b, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        agree = valid & np.isin(q39b, list(AGREE_CODES))
        results[label] = {
            "pct": round(100 * weight[agree].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(q39b, list(VALID_CODES))
    agree_all = valid_all & np.isin(q39b, list(AGREE_CODES))
    results["All U.S. adults"] = {
        "pct": round(100 * weight[agree_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }

    order = [label for label in results if label != "All U.S. adults"]
    order.sort(key=lambda label: -results[label]["pct"])
    order.append("All U.S. adults")

    out = {
        "source": 'Pew Research Center. 2008. "U.S. Religious Landscape Survey."',
        "method": "Population is current religious tradition (RELTRAD), continental-US main "
                  "survey only. q39b asked whether the respondent agrees or disagrees that "
                  "\"angels and demons are active in the world\"; shown here is the share "
                  "answering \"completely agree\" or \"mostly agree.\" Don't know/refused are "
                  "excluded from each row's denominator. Groups with fewer than 30 valid "
                  "respondents are omitted. Weighted by the dataset's own `weight` variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "angels_demons_active": results,
    }
    with open(
        "docs/datasets/pew-rls-2007/angels-demons-active.json", "w", encoding="utf-8"
    ) as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:34} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-rls-2007/angels-demons-active.json")


if __name__ == "__main__":
    main()

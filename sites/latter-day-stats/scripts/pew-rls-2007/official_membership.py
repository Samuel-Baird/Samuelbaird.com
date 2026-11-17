"""
2007 U.S. Religious Landscape Survey: are you or your family official members
of the local church or house of worship where you attend (q29), by current
religious tradition (RELTRAD)? Formal, recorded membership is central to
Latter-day Saint practice - baptism and confirmation create a membership
record the Church actively maintains - so this item checks that institutional
emphasis against every other tradition's own sense of formal belonging.

Usage: python scripts/pew-rls-2007/official_membership.py
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
YES_CODE = {1.0}
VALID_CODES = {1.0, 2.0}
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["reltrad", "q29", "weight"])
    weight = df["weight"].to_numpy()
    reltrad = df["reltrad"].to_numpy()
    q29 = df["q29"].to_numpy()

    results = {}
    for code, label in RELTRAD_CODES.items():
        group_mask = reltrad == code
        valid = group_mask & np.isin(q29, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        member = valid & np.isin(q29, list(YES_CODE))
        results[label] = {
            "pct": round(100 * weight[member].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(q29, list(VALID_CODES))
    member_all = valid_all & np.isin(q29, list(YES_CODE))
    results["All U.S. adults"] = {
        "pct": round(100 * weight[member_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }

    order = [label for label in results if label != "All U.S. adults"]
    order.sort(key=lambda label: -results[label]["pct"])
    order.append("All U.S. adults")

    out = {
        "source": 'Pew Research Center. 2008. "U.S. Religious Landscape Survey."',
        "method": "Population is current religious tradition (RELTRAD), continental-US main "
                  "survey only. q29 asked whether the respondent or their family are official "
                  "members of the church or house of worship where they attend most often; "
                  "don't know/refused are excluded from each row's denominator. Groups with "
                  "fewer than 30 valid respondents are omitted. Weighted by the dataset's own "
                  "`weight` variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "official_member": results,
    }
    with open(
        "docs/datasets/pew-rls-2007/official-membership.json", "w", encoding="utf-8"
    ) as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:34} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-rls-2007/official-membership.json")


if __name__ == "__main__":
    main()

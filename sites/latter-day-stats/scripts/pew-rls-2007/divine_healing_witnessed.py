"""
2007 U.S. Religious Landscape Survey: "Have you ever experienced or
witnessed a divine healing of an illness or injury?" (q43d), by current
religious tradition (RELTRAD). Latter-day Saint practice includes
priesthood healing blessings - anointing with oil and the laying on of
hands for the sick (D&C 42:43-44; James 5:14-15) - administered by any
worthy Melchizedek Priesthood holder, not reserved to clergy, so this item
checks lived/witnessed divine healing against every other tradition's own
rate.

Usage: python scripts/pew-rls-2007/divine_healing_witnessed.py
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
YES_CODE = {1.0}
VALID_CODES = {1.0, 2.0}
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["reltrad", "q43d", "weight"])
    weight = df["weight"].to_numpy()
    reltrad = df["reltrad"].to_numpy()
    q43d = df["q43d"].to_numpy()

    results = {}
    for code, label in RELTRAD_CODES.items():
        group_mask = reltrad == code
        valid = group_mask & np.isin(q43d, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        yes = valid & np.isin(q43d, list(YES_CODE))
        results[label] = {
            "pct": round(100 * weight[yes].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(q43d, list(VALID_CODES))
    yes_all = valid_all & np.isin(q43d, list(YES_CODE))
    results["All U.S. adults"] = {
        "pct": round(100 * weight[yes_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }

    order = sort_groups(list(results.keys()), lambda label: results[label]["pct"])

    out = {
        "source": 'Pew Research Center. 2008. "U.S. Religious Landscape Survey."',
        "method": "Population is current religious tradition (RELTRAD), continental-US main "
                  "survey only. q43d asked whether the respondent has ever experienced or "
                  "witnessed a divine healing of an illness or injury; shown here is the "
                  "share answering \"yes.\" Don't know/refused are excluded from each row's "
                  "denominator. Groups with fewer than 30 valid respondents are omitted. "
                  "Weighted by the dataset's own `weight` variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "divine_healing_witnessed": results,
    }
    with open(
        "docs/datasets/pew-rls-2007/divine-healing-witnessed.json", "w", encoding="utf-8"
    ) as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:34} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-rls-2007/divine-healing-witnessed.json")


if __name__ == "__main__":
    main()

"""
Second flagship chart for the 2007 U.S. Religious Landscape Survey: how
certain are people that God or a universal spirit exists (q31), by current
religious tradition (RELTRAD)? q31 was only asked of respondents who
answered "yes" to q30 (believe in God/a universal spirit); its own missing
values for non-believers are excluded automatically since they fall
outside VALID_CODES. Top box is "Absolutely certain." Population is
RELTRAD, continental-US main survey only (same scope as
evolution_belief.py in this folder - the Alaska/Hawaii supplement is a
separate file with its own weight and isn't combined here).

Usage: python scripts/pew-rls-2007/certainty_of_god.py
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
TOP_BOX = {1.0}  # absolutely certain
VALID_CODES = {1.0, 2.0, 3.0, 4.0}


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["reltrad", "q31", "weight"])
    weight = df["weight"].to_numpy()
    reltrad = df["reltrad"].to_numpy()
    certainty = df["q31"].to_numpy()

    results = {}
    for code, label in RELTRAD_CODES.items():
        group_mask = reltrad == code
        valid = group_mask & np.isin(certainty, list(VALID_CODES))
        top = valid & np.isin(certainty, list(TOP_BOX))
        results[label] = {
            "pct": round(100 * weight[top].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(certainty, list(VALID_CODES))
    top_all = valid_all & np.isin(certainty, list(TOP_BOX))
    results["All U.S. adults"] = {
        "pct": round(100 * weight[top_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }

    order = sorted(results, key=lambda label: -results[label]["pct"])
    order.remove("All U.S. adults")
    order.append("All U.S. adults")

    out = {
        "source": 'Pew Research Center. 2008. "U.S. Religious Landscape Survey."',
        "method": "Population is current religious tradition (RELTRAD), continental-US main "
                  "survey only. q31 (\"how certain are you\") was asked only of respondents "
                  "who said yes to believing in God/a universal spirit (q30); non-believers "
                  "and don't know/refused are excluded from each row's denominator since "
                  "they fall outside q31's valid range. Top box is \"absolutely certain.\" "
                  "Weighted by the dataset's own `weight` variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "absolutely_certain": results,
    }
    with open("docs/datasets/pew-rls-2007/certainty-of-god.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:34} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-rls-2007/certainty-of-god.json")


if __name__ == "__main__":
    main()

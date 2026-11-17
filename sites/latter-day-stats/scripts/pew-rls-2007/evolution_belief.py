"""
Flagship chart for the 2007 U.S. Religious Landscape Survey: how many
people in each religious tradition agree that evolution is the best
explanation for human life on Earth (q10c), top-two-box (completely +
mostly agree), matching this site's existing agree-scale convention.
Population is RELTRAD (current tradition), continental-US main survey only
(the Alaska/Hawaii supplement is a separate file with its own weight and
isn't combined here). Don't know/refused excluded from each row.

Usage: python scripts/pew-rls-2007/evolution_belief.py
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


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["reltrad", "q10c", "weight"])
    weight = df["weight"].to_numpy()
    reltrad = df["reltrad"].to_numpy()
    evo = df["q10c"].to_numpy()

    results = {}
    for code, label in RELTRAD_CODES.items():
        group_mask = reltrad == code
        valid = group_mask & np.isin(evo, list(VALID_CODES))
        agree = valid & np.isin(evo, list(AGREE_CODES))
        results[label] = {
            "pct": round(100 * weight[agree].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(evo, list(VALID_CODES))
    agree_all = valid_all & np.isin(evo, list(AGREE_CODES))
    results["All U.S. adults"] = {
        "pct": round(100 * weight[agree_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }

    order = sorted(results, key=lambda label: -results[label]["pct"])
    order.remove("All U.S. adults")
    order.append("All U.S. adults")

    out = {
        "source": 'Pew Research Center. 2008. "U.S. Religious Landscape Survey."',
        "method": "Population is current religious tradition (RELTRAD), continental-US main "
                  "survey only. Cutpoint is top-two-box (completely + mostly agree) on q10c "
                  "(\"Evolution is the best explanation for the origins of human life on "
                  "earth\"); don't know/refused excluded from each row's denominator. "
                  "Weighted by the dataset's own `weight` variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "evolution_agree": results,
    }
    with open("docs/datasets/pew-rls-2007/evolution-belief.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:34} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-rls-2007/evolution-belief.json")


if __name__ == "__main__":
    main()

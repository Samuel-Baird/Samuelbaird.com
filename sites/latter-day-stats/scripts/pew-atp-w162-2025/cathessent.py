"""
What's essential to being Catholic? (CATHESSENT_a-n, 14 items), a
single-population ranking among Catholics (RELIG_W162 == 2) - same shape
as pew-mormon-survey-2011/essential_to_being_mormon.py. "Essential" is the
top of a three-point scale (essential, important but not essential, not
important). Own don't know/refused excluded from each item's denominator.

Hook: Dec 8 2026 (Feast of the Immaculate Conception) / Dec 12 2026
(Feast of Our Lady of Guadalupe).

Usage: python scripts/pew-atp-w162-2025/cathessent.py
"""
import json

import numpy as np
import pyreadstat

SAV = "data/pew-atp-w162-2025/ATP W162.sav"

ITEMS = {
    "CATHESSENT_a_W162": "Receiving the Eucharist",
    "CATHESSENT_b_W162": "A relationship with Jesus",
    "CATHESSENT_d_W162": "Devotion to the Virgin Mary",
    "CATHESSENT_f_W162": "The pope's leadership",
    "CATHESSENT_j_W162": "Helping the poor and needy",
    "CATHESSENT_k_W162": "Opposing abortion",
    "CATHESSENT_l_W162": "Caring for immigrants",
    "CATHESSENT_n_W162": "Opposing the death penalty",
}
VALID_CODES = {1.0, 2.0, 3.0}
ESSENTIAL = 1.0
RELIG_CATHOLIC = 2.0


def main():
    usecols = ["RELIG_W162", "WEIGHT_W162", *ITEMS.keys()]
    df, _ = pyreadstat.read_sav(SAV, usecols=usecols)
    weight = df["WEIGHT_W162"].to_numpy()
    catholic = df["RELIG_W162"].to_numpy() == RELIG_CATHOLIC

    results = {}
    for col, label in ITEMS.items():
        item = df[col].to_numpy()
        valid = catholic & np.isin(item, list(VALID_CODES))
        essential = valid & (item == ESSENTIAL)
        results[label] = {
            "pct": round(100 * weight[essential].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
        }

    order = sorted(results, key=lambda label: -results[label]["pct"])

    out = {
        "source": "Pew Research Center. American Trends Panel Wave 162, fielded Feb. 3-9, 2025.",
        "method": "Population is Catholic respondents (RELIG_W162 == 2, \"Roman Catholic\"). "
                  "Each item's own don't know/refused excluded from its own denominator; "
                  "\"essential\" is the top of a three-point scale (essential, important but "
                  "not essential, not important). Weighted by WEIGHT_W162.",
        "total_weighted_n": float(weight[catholic].sum()),
        "total_unweighted_n": int(catholic.sum()),
        "item_order": order,
        "essential_pct": results,
    }
    with open("docs/datasets/pew-atp-w162-2025/cathessent.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:44} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>4})")
    print("\nWrote docs/datasets/pew-atp-w162-2025/cathessent.json")


if __name__ == "__main__":
    main()

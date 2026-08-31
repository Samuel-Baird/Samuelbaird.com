"""
How often do Catholics go to confession? (CONFESS_W162) A single-population
distribution across the item's own five response options, among Catholics
(RELIG_W162 == 2) - same shape as pew-mormon-survey-2011/polygamy_morality.py.
Own don't know/refused excluded from the denominator.

Hook: Ash Wednesday / Lent begins, Feb 10 2027.

Usage: python scripts/pew-atp-w162-2025/confession_frequency.py
"""
import json

import numpy as np
import pyreadstat

SAV = "data/pew-atp-w162-2025/ATP W162.sav"

OPTIONS = {
    5.0: "Never",
    4.0: "Less than once a year",
    3.0: "Once a year",
    2.0: "Several times a year",
    1.0: "At least once a month",
}
RELIG_CATHOLIC = 2.0


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["RELIG_W162", "CONFESS_W162", "WEIGHT_W162"])
    weight = df["WEIGHT_W162"].to_numpy()
    catholic = df["RELIG_W162"].to_numpy() == RELIG_CATHOLIC
    col = df["CONFESS_W162"].to_numpy()
    valid = catholic & np.isin(col, list(OPTIONS.keys()))
    base_w = weight[valid].sum()

    results = {}
    for code, label in OPTIONS.items():
        hit = valid & (col == code)
        results[label] = {
            "pct": round(100 * weight[hit].sum() / base_w, 2),
            "valid_unweighted_n": int(hit.sum()),
        }

    order = sorted(OPTIONS.values(), key=lambda label: -results[label]["pct"])

    out = {
        "source": "Pew Research Center. American Trends Panel Wave 162, fielded Feb. 3-9, 2025.",
        "method": "Population is Catholic respondents (RELIG_W162 == 2). Don't know/refused "
                  "excluded from the denominator. Weighted by WEIGHT_W162.",
        "total_weighted_n": float(weight[valid].sum()),
        "total_unweighted_n": int(valid.sum()),
        "item_order": order,
        "confession_frequency_pct": results,
    }
    with open("docs/datasets/pew-atp-w162-2025/confession-frequency.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:28} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>4})")
    print("\nWrote docs/datasets/pew-atp-w162-2025/confession-frequency.json")


if __name__ == "__main__":
    main()

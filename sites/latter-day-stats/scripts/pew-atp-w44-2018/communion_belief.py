"""
Do Catholics believe in transubstantiation? (COMMUNB_W44) - "Regardless of
the official teaching of the Catholic Church, what do you personally
believe about the bread and wine used for Communion?" Asked only of
Catholics (F_RELTRAD == 10000, per the wave's own skip logic - verified
against crosstab, no other tradition has non-missing responses), so this
is a single-population distribution, same shape as
pew-atp-w162-2025/confession_frequency.py. Own refused excluded.

Hook: Corpus Christi, May 27 2027. More precise than
pew-latin-america-2014/transubstantiation.py's Q60m for a US-focused site:
this item is U.S. Catholics' own belief (not "communion" generically) and
distinguishes "actually become" (the Church's actual teaching,
transubstantiation) from "are symbols of" - the same two-option framing
COMMUNA_W44 (a knowledge item, not used here) tests respondents on.

Usage: python scripts/pew-atp-w44-2018/communion_belief.py
"""
import json

import numpy as np
import pyreadstat

SAV = "data/pew-atp-w44-2018/ATP W44.sav"

OPTIONS = {
    1.0: "Actually become the body and blood of Christ",
    2.0: "Are symbols of the body and blood of Christ",
}
RELTRAD_CATHOLIC = 10000.0


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["F_RELTRAD", "COMMUNB_W44", "WEIGHT_W44"])
    weight = df["WEIGHT_W44"].to_numpy()
    catholic = df["F_RELTRAD"].to_numpy() == RELTRAD_CATHOLIC
    col = df["COMMUNB_W44"].to_numpy()
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
        "source": "Pew Research Center. American Trends Panel Wave 44, fielded Feb. 4-19, 2019.",
        "method": "Population is Catholic respondents (F_RELTRAD == 10000, per this wave's own "
                  "skip logic - COMMUNB was not asked outside this group). Refused excluded "
                  "from the denominator. Weighted by WEIGHT_W44.",
        "total_weighted_n": float(weight[valid].sum()),
        "total_unweighted_n": int(valid.sum()),
        "item_order": order,
        "belief_pct": results,
    }
    with open("docs/datasets/pew-atp-w44-2018/communion-belief.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:44} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>4})")
    print("\nWrote docs/datasets/pew-atp-w44-2018/communion-belief.json")


if __name__ == "__main__":
    main()

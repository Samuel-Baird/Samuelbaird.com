"""
2014 Religious Landscape Study: should my church or denomination preserve
its traditional beliefs and practices, adjust them in light of new
circumstances, or adopt modern beliefs and practices (qh4), by current
religious tradition (RELTRAD). Asked of the full sample, so all 12 RELTRAD
groups clear the 30-valid floor comfortably. Latter-day Saints teach that
core doctrine is eternal and unchanging even as the Church receives
continuing revelation on its application - this item checks how strongly
Latter-day Saints favor preserving traditional belief and practice over
adjusting or modernizing it, relative to other traditions.

Usage: python scripts/pew-rls-2014/preserve_traditional_beliefs.py
"""
import json

import numpy as np
import pyreadstat

SAV = ("data/pew-rls-2014/"
       "Dataset - Pew Research Center 2014 Religious Landscape Study National Telephone "
       "Survey - Version 1.1 - December 1 2016.sav")

RELTRAD_CODES = {
    1100.0: "Evangelical Protestant",
    1200.0: "Mainline Protestant",
    1300.0: "Historically Black Protestant",
    10000.0: "Catholic",
    20000.0: "Mormon",
    30000.0: "Orthodox Christian",
    40001.0: "Jehovah's Witness",
    50000.0: "Jewish",
    60000.0: "Muslim",
    70000.0: "Buddhist",
    80000.0: "Hindu",
    100000.0: "Unaffiliated",
}
PRESERVE_CODE = {1.0}
VALID_CODES = {1.0, 2.0, 3.0}
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["RELTRAD", "qh4", "WEIGHT"])
    weight = df["WEIGHT"].to_numpy()
    reltrad = df["RELTRAD"].to_numpy()
    qh4 = df["qh4"].to_numpy()

    results = {}
    for code, label in RELTRAD_CODES.items():
        group_mask = reltrad == code
        valid = group_mask & np.isin(qh4, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        preserve = valid & np.isin(qh4, list(PRESERVE_CODE))
        results[label] = {
            "pct": round(100 * weight[preserve].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(qh4, list(VALID_CODES))
    preserve_all = valid_all & np.isin(qh4, list(PRESERVE_CODE))
    results["All U.S. adults"] = {
        "pct": round(100 * weight[preserve_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }

    order = [label for label in results if label != "All U.S. adults"]
    order.sort(key=lambda label: -results[label]["pct"])
    order.append("All U.S. adults")

    out = {
        "source": 'Pew Research Center. 2015. "2014 Religious Landscape Study."',
        "method": "Population is the full sample, classified by current religious tradition "
                  "(RELTRAD). qh4 asked whether the respondent's own church or denomination "
                  "should preserve its traditional beliefs and practices, adjust traditional "
                  "beliefs and practices in light of new circumstances, or adopt modern "
                  "beliefs and practices; volunteered \"other\" and don't know/refused are "
                  "excluded from each row's denominator. Groups with fewer than 30 valid "
                  "respondents are omitted. Weighted by the dataset's own national WEIGHT "
                  "variable.",
        "total_weighted_n": float(weight[valid_all].sum()),
        "total_unweighted_n": int(valid_all.sum()),
        "group_order": order,
        "prefers_preserving_traditional_beliefs": results,
    }
    with open(
        "docs/datasets/pew-rls-2014/preserve-traditional-beliefs.json", "w", encoding="utf-8"
    ) as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:38} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-rls-2014/preserve-traditional-beliefs.json")


if __name__ == "__main__":
    main()

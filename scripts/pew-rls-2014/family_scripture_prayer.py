"""
2014 Religious Landscape Study: among parents, do you pray or read Scripture
with your child(ren) (qk10a), by current religious tradition (RELTRAD). This
item was asked only of respondents with children, which is why every group's
N is well under the full sample size but still comfortably clears the
30-valid floor for all 12 RELTRAD groups. Family scripture study and prayer
sit at the center of Latter-day Saint practice - the Church formally teaches
weekly "family home evening" and daily personal/family scripture study - so
this item checks that emphasis against parents from other traditions doing
the same thing with their own kids.

Usage: python scripts/pew-rls-2014/family_scripture_prayer.py
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
YES_CODE = {1.0}
VALID_CODES = {1.0, 2.0}
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["RELTRAD", "qk10a", "WEIGHT"])
    weight = df["WEIGHT"].to_numpy()
    reltrad = df["RELTRAD"].to_numpy()
    qk10a = df["qk10a"].to_numpy()

    results = {}
    for code, label in RELTRAD_CODES.items():
        group_mask = reltrad == code
        valid = group_mask & np.isin(qk10a, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        does_it = valid & np.isin(qk10a, list(YES_CODE))
        results[label] = {
            "pct": round(100 * weight[does_it].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(qk10a, list(VALID_CODES))
    does_it_all = valid_all & np.isin(qk10a, list(YES_CODE))
    results["All parents"] = {
        "pct": round(100 * weight[does_it_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(valid_all.sum()),
    }

    order = [label for label in results if label != "All parents"]
    order.sort(key=lambda label: -results[label]["pct"])
    order.append("All parents")

    out = {
        "source": 'Pew Research Center. 2015. "2014 Religious Landscape Study."',
        "method": "Population is parents (respondents with children), classified by current "
                  "religious tradition (RELTRAD). qk10a asked parents whether they pray or "
                  "read Scripture with their child(ren); don't know/refused are excluded from "
                  "each row's denominator. Groups with fewer than 30 valid respondents are "
                  "omitted. Weighted by the dataset's own national WEIGHT variable.",
        "total_weighted_n": float(weight[valid_all].sum()),
        "total_unweighted_n": int(valid_all.sum()),
        "group_order": order,
        "prays_or_reads_scripture_with_children": results,
    }
    with open(
        "docs/datasets/pew-rls-2014/family-scripture-prayer.json", "w", encoding="utf-8"
    ) as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:38} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-rls-2014/family-scripture-prayer.json")


if __name__ == "__main__":
    main()

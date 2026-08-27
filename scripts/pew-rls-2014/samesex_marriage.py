"""
Flagship chart for the 2014 Religious Landscape Study: support for
same-sex marriage by religious tradition (qb22 - "Do you strongly favor,
favor, oppose or strongly oppose allowing gays and lesbians to marry
legally?"), top-two-box (strongly favor + favor). Population is RELTRAD
(current tradition); don't know/refused excluded from each row.

Usage: python scripts/pew-rls-2014/samesex_marriage.py
"""
import json

import numpy as np
import pyreadstat

SAV = ("data/pew-rls-2014/"
       "Dataset - Pew Research Center 2014 Religious Landscape Study National Telephone "
       "Survey - Version 1.1 - December 1 2016.sav")

RELTRAD_CODES = {
    1100.0: "Evangelical Protestant Tradition",
    1200.0: "Mainline Protestant Tradition",
    1300.0: "Historically Black Protestant Tradition",
    10000.0: "Catholic",
    20000.0: "Mormon",
    40001.0: "Jehovah's Witness",
    50000.0: "Jewish",
    100000.0: "Unaffiliated (religious \"nones\")",
}
FAVOR_CODES = {1.0, 2.0}
VALID_CODES = {1.0, 2.0, 3.0, 4.0}


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["RELTRAD", "qb22", "WEIGHT"])
    weight = df["WEIGHT"].to_numpy()
    reltrad = df["RELTRAD"].to_numpy()
    marriage = df["qb22"].to_numpy()

    results = {}
    for code, label in RELTRAD_CODES.items():
        group_mask = reltrad == code
        valid = group_mask & np.isin(marriage, list(VALID_CODES))
        favor = valid & np.isin(marriage, list(FAVOR_CODES))
        results[label] = {
            "pct": round(100 * weight[favor].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(marriage, list(VALID_CODES))
    favor_all = valid_all & np.isin(marriage, list(FAVOR_CODES))
    results["All U.S. adults"] = {
        "pct": round(100 * weight[favor_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }

    order = sorted(results, key=lambda label: -results[label]["pct"])
    order.remove("All U.S. adults")
    order.append("All U.S. adults")

    out = {
        "source": 'Pew Research Center. 2015. "2014 Religious Landscape Study."',
        "method": "Population is current religious tradition (RELTRAD). Cutpoint is "
                  "top-two-box (strongly favor + favor) on qb22 (\"allowing gays and "
                  "lesbians to marry legally\"); don't know/refused excluded from each "
                  "row's denominator. Weighted by the dataset's own national WEIGHT variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "favor_samesex_marriage": results,
    }
    with open("docs/datasets/pew-rls-2014/samesex-marriage.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:38} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-rls-2014/samesex-marriage.json")


if __name__ == "__main__":
    main()

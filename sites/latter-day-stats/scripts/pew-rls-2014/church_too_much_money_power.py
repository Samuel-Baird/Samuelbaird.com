"""
2014 Religious Landscape Study: agreement that "churches and other religious
organizations are too concerned with money and power" (qm5b), by current
religious tradition (RELTRAD). Asked of the full sample, so all 12 RELTRAD
groups clear the 30-valid floor comfortably. The second of the qm5a/b/d
"critique of religious institutions" battery flagged as an open candidate
across several prior passes' notes (checked for overlap against the 2023-24
wave's public-life battery first: that battery's RELINST_E/F/G ask the
positive-framed counterparts - protecting morality, bringing people
together, helping the poor - not this negative "too many rules/too much
money and power/too political" framing, so these are a genuinely distinct
construct, not a duplicate). Latter-day Saints are the LEAST likely of any
of the 12 groups to agree churches are too concerned with money and power,
a natural companion to the sibling qm5a "too many rules" chart from the
same battery.

Usage: python scripts/pew-rls-2014/church_too_much_money_power.py
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
AGREE_CODE = {1.0}
VALID_CODES = {1.0, 2.0}
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["RELTRAD", "qm5b", "WEIGHT"])
    weight = df["WEIGHT"].to_numpy()
    reltrad = df["RELTRAD"].to_numpy()
    qm5b = df["qm5b"].to_numpy()

    results = {}
    for code, label in RELTRAD_CODES.items():
        group_mask = reltrad == code
        valid = group_mask & np.isin(qm5b, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        agree = valid & np.isin(qm5b, list(AGREE_CODE))
        results[label] = {
            "pct": round(100 * weight[agree].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(qm5b, list(VALID_CODES))
    agree_all = valid_all & np.isin(qm5b, list(AGREE_CODE))
    results["All U.S. adults"] = {
        "pct": round(100 * weight[agree_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }

    order = [label for label in results if label != "All U.S. adults"]
    order.sort(key=lambda label: -results[label]["pct"])
    order.append("All U.S. adults")

    out = {
        "source": 'Pew Research Center. 2015. "2014 Religious Landscape Study."',
        "method": "Population is the full sample, classified by current religious tradition "
                  "(RELTRAD). qm5b asked whether the respondent agrees or disagrees that "
                  "\"churches and other religious organizations are too concerned with money "
                  "and power\"; volunteered don't know/refused is excluded from each row's "
                  "denominator. Groups with fewer than 30 valid respondents are omitted. "
                  "Weighted by the dataset's own national WEIGHT variable.",
        "total_weighted_n": float(weight[valid_all].sum()),
        "total_unweighted_n": int(valid_all.sum()),
        "group_order": order,
        "agrees_church_too_much_money_power": results,
    }
    with open(
        "docs/datasets/pew-rls-2014/church-too-much-money-power.json", "w", encoding="utf-8"
    ) as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:38} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-rls-2014/church-too-much-money-power.json")


if __name__ == "__main__":
    main()

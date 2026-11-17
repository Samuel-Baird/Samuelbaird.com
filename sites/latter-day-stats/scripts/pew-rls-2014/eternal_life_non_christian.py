"""
2014 Religious Landscape Study: "do you think it's only Christian religions
that can lead to eternal life, or can some non-Christian religions also lead
to eternal life?" (qh2), by current religious tradition (RELTRAD). This item
was asked only of respondents already classified into a Christian tradition
(the survey's skip logic returns zero valid cases for Jewish/Muslim/Buddhist/
Hindu/Unaffiliated respondents, confirmed against the .sav), so the chart
covers only Christian traditions. Latter-day Saint doctrine teaches that
salvation is available to everyone, including those who never had a chance
to hear the gospel in life, through proxy ordinances performed in temples -
this item checks whether that universalist strand shows up as measurably
more inclusive views on this specific belief question than most other
Christian traditions. Jehovah's Witness clears the sample (n=245) but falls
under the 30-valid floor on this skip-gated item and is dropped, same
convention as certainty_of_god.py in this folder.

Usage: python scripts/pew-rls-2014/eternal_life_non_christian.py
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
    30000.0: "Orthodox Christian",
    40001.0: "Jehovah's Witness",
}
NON_CHRISTIAN_OK = {2.0}
VALID_CODES = {1.0, 2.0}
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["RELTRAD", "qh2", "WEIGHT"])
    weight = df["WEIGHT"].to_numpy()
    reltrad = df["RELTRAD"].to_numpy()
    qh2 = df["qh2"].to_numpy()

    results = {}
    for code, label in RELTRAD_CODES.items():
        group_mask = reltrad == code
        valid = group_mask & np.isin(qh2, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        inclusive = valid & np.isin(qh2, list(NON_CHRISTIAN_OK))
        results[label] = {
            "pct": round(100 * weight[inclusive].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(qh2, list(VALID_CODES))
    inclusive_all = valid_all & np.isin(qh2, list(NON_CHRISTIAN_OK))
    results["All Christian traditions"] = {
        "pct": round(100 * weight[inclusive_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(valid_all.sum()),
    }

    order = [label for label in results if label != "All Christian traditions"]
    order.sort(key=lambda label: -results[label]["pct"])
    order.append("All Christian traditions")

    out = {
        "source": 'Pew Research Center. 2015. "2014 Religious Landscape Study."',
        "method": "Population is current religious tradition (RELTRAD), restricted to "
                  "Christian traditions - qh2 was asked only of respondents the survey's "
                  "skip logic had already classified as Christian; non-Christian and "
                  "unaffiliated respondents have no valid cases on this item. Share shown "
                  "is those who say some non-Christian religions can also lead to eternal "
                  "life, vs. only Christian religions; don't know/refused/undesignated are "
                  "excluded from each row's denominator. Groups with fewer than 30 valid "
                  "respondents are omitted. Weighted by the dataset's own national WEIGHT "
                  "variable.",
        "total_weighted_n": float(weight[valid_all].sum()),
        "total_unweighted_n": int(valid_all.sum()),
        "group_order": order,
        "non_christian_can_lead_to_eternal_life": results,
    }
    with open(
        "docs/datasets/pew-rls-2014/eternal-life-non-christian.json", "w", encoding="utf-8"
    ) as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:38} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-rls-2014/eternal-life-non-christian.json")


if __name__ == "__main__":
    main()

"""
Sixth flagship chart for Faith in Flux: the joining-side mirror of
leaving_decision_maker.py in this folder. When people became their current
religious identity (CURREL) - which for some respondents means joining a
new religion, and for others means settling into "unaffiliated" - was it
mostly their own decision, or mostly decided by their parents or family
(q15)? Population is respondents with a valid q15 response: the survey
only asks q15 of people who report a specific age at which they became
CURREL (q14), so this is a subset of switchers, not the full 2,867 -
skewed toward people whose q14 age put them past childhood (q15 is skipped
for people who were very young children when they became CURREL, since a
decision framing doesn't apply to an infant). n=399 valid, comparable in
scale to reasons_joined_lds.py's 38-respondent LDS-only subgroup and
several other small-n charts already shipped from this dataset.

Usage: python scripts/pew-faith-in-flux-2008/joining_decision_maker.py
"""
import json

import numpy as np
import pyreadstat

SAV = ("data/pew-faith-in-flux-2008/"
       "Dataset - Pew Forum on Religion & Public Life 2008 Conversion Recontact Survey.sav")

DECISION_CODES = {
    1.0: "Mostly their own decision",
    2.0: "Mostly decided by parents or family",
    3.0: "Both/neither",
}
VALID_CODES = {1.0, 2.0, 3.0}


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["q15", "weight"])
    weight = df["weight"].to_numpy()
    decision = df["q15"].to_numpy()

    valid = np.isin(decision, list(VALID_CODES))
    valid_n = int(valid.sum())
    valid_w = weight[valid].sum()

    results = {}
    for code, label in DECISION_CODES.items():
        mask = valid & (decision == code)
        results[label] = {
            "pct": round(100 * weight[mask].sum() / valid_w, 2),
            "unweighted_n": int(mask.sum()),
        }

    order = sorted(results, key=lambda label: -results[label]["pct"])

    out = {
        "source": 'Pew Research Center. 2009. "Faith in Flux: Changes in Religious '
                  'Affiliation in the U.S."',
        "method": "Population is respondents with a valid answer to q15, asked only of "
                  "those who report a specific age at which they became their current "
                  "religious identity (q14) - a subset of this 2,867-respondent recontact "
                  "survey's switchers, skewed toward people who adopted CURREL past early "
                  "childhood. q15 asks whether becoming CURREL was mostly their own "
                  "decision or mostly decided by parents/family; don't know/refused "
                  "excluded from the denominator. Weighted by the dataset's own `weight` "
                  "variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "valid_unweighted_n": valid_n,
        "decision_order": order,
        "decision_pct": results,
    }
    with open("docs/datasets/pew-faith-in-flux-2008/joining-decision-maker.json",
              "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:38} {r['pct']:5.1f}%  (n={r['unweighted_n']:>4})")
    print("\nWrote docs/datasets/pew-faith-in-flux-2008/joining-decision-maker.json")


if __name__ == "__main__":
    main()

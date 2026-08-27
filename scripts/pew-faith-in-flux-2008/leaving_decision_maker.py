"""
Fourth flagship chart for Faith in Flux: when people left the religion
they were raised in, was it mostly their own decision, or mostly decided
by their parents or family (q2)? Single-population share across all 2,867
recontacted switchers - same population as reasons_left_religion.py and
leave_vs_join.py in this folder.

Usage: python scripts/pew-faith-in-flux-2008/leaving_decision_maker.py
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
    df, _ = pyreadstat.read_sav(SAV, usecols=["q2", "weight"])
    weight = df["weight"].to_numpy()
    decision = df["q2"].to_numpy()

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
        "method": "Population is all respondents who left the religion they were raised in "
                  "(this recontact survey's own design). q2 asks whether leaving was mostly "
                  "their own decision or mostly decided by parents/family; don't know/"
                  "refused excluded from the denominator. Weighted by the dataset's own "
                  "`weight` variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "valid_unweighted_n": valid_n,
        "decision_order": order,
        "decision_pct": results,
    }
    with open("docs/datasets/pew-faith-in-flux-2008/leaving-decision-maker.json",
              "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:38} {r['pct']:5.1f}%  (n={r['unweighted_n']:>4})")
    print("\nWrote docs/datasets/pew-faith-in-flux-2008/leaving-decision-maker.json")


if __name__ == "__main__":
    main()

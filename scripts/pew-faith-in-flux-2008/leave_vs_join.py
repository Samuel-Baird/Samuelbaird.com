"""
Third flagship chart for Faith in Flux: when people changed religion, was
it driven more by wanting to leave their old religion, or by wanting to
join a new one (q6)? Single-population share across all 2,867 recontacted
switchers - same population as reasons_left_religion.py in this folder.

Usage: python scripts/pew-faith-in-flux-2008/leave_vs_join.py
"""
import json

import numpy as np
import pyreadstat

SAV = ("data/pew-faith-in-flux-2008/"
       "Dataset - Pew Forum on Religion & Public Life 2008 Conversion Recontact Survey.sav")

MOTIVE_CODES = {
    1.0: "Wanted to leave the old religion",
    2.0: "Wanted to join the new religion",
    3.0: "Neither/both",
}
VALID_CODES = {1.0, 2.0, 3.0}


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["q6", "weight"])
    weight = df["weight"].to_numpy()
    motive = df["q6"].to_numpy()

    valid = np.isin(motive, list(VALID_CODES))
    valid_n = int(valid.sum())
    valid_w = weight[valid].sum()

    results = {}
    for code, label in MOTIVE_CODES.items():
        mask = valid & (motive == code)
        results[label] = {
            "pct": round(100 * weight[mask].sum() / valid_w, 2),
            "unweighted_n": int(mask.sum()),
        }

    order = sorted(results, key=lambda label: -results[label]["pct"])

    out = {
        "source": 'Pew Research Center. 2009. "Faith in Flux: Changes in Religious '
                  'Affiliation in the U.S."',
        "method": "Population is all respondents who left the religion they were raised in "
                  "(this recontact survey's own design). q6 asks whether the change was "
                  "more about wanting to leave the old religion or wanting to join the new "
                  "one; don't know/refused excluded from the denominator. Weighted by the "
                  "dataset's own `weight` variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "valid_unweighted_n": valid_n,
        "motive_order": order,
        "motive_pct": results,
    }
    with open("docs/datasets/pew-faith-in-flux-2008/leave-vs-join.json",
              "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:34} {r['pct']:5.1f}%  (n={r['unweighted_n']:>4})")
    print("\nWrote docs/datasets/pew-faith-in-flux-2008/leave-vs-join.json")


if __name__ == "__main__":
    main()

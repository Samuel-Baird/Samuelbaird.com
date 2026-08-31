"""
ATP Wave 114 (September 2022): how essential is attending religious
services regularly to what being a faithful member of your religious
tradition means? ESSENT_b_W114 is one item in Wave 114's ESSENT battery
("How important is each of the following to what being [Christian/Jewish/
Muslim/Buddhist/Hindu/faithful to your religious tradition] means to
you?"). Unlike ESSENT_k (personal relationship with Jesus Christ, see
essent_jesus.py in this folder), this item was piped to every religiously
affiliated respondent regardless of tradition, so it covers a wider set
of groups: Protestant, Catholic, Mormon, Orthodox Christian, Jewish,
Muslim, Buddhist, and Hindu (Atheist/Agnostic/Nothing in particular show
zero valid responses, as expected).

Like christian_nation.py in this same folder, this wave has no F_RELTRAD
frame variable, so the breakout uses F_RELIG (self-reported affiliation).

Regular church attendance is a well-known, distinctive marker of
Latter-day Saint practice (weekly sacrament meeting), so this is a
genuine practice-vs-data comparison, not a coincidental crosstab.

Usage: python scripts/pew-atp-w114-2022/essent_attend.py
"""
import json

import numpy as np
import pyreadstat

SAV = "data/pew-atp-w114-2022/ATP W114.sav"

RELIG_CODES = {
    1.0: "Protestant",
    2.0: "Catholic",
    3.0: "Mormon",
    4.0: "Orthodox Christian",
    5.0: "Jewish",
    6.0: "Muslim",
    7.0: "Buddhist",
    8.0: "Hindu",
}
ESSENTIAL = 1.0
VALID_CODES = {1.0, 2.0, 3.0}
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(
        SAV, usecols=["F_RELIG", "ESSENT_b_W114", "WEIGHT_W114"]
    )
    weight = df["WEIGHT_W114"].to_numpy()
    relig = df["F_RELIG"].to_numpy()
    essent = df["ESSENT_b_W114"].to_numpy()

    results = {}
    for code, label in RELIG_CODES.items():
        group_mask = relig == code
        valid = group_mask & np.isin(essent, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        yes = valid & (essent == ESSENTIAL)
        results[label] = {
            "pct": round(100 * weight[yes].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    order = sorted(results, key=lambda label: -results[label]["pct"])

    out = {
        "source": "Pew Research Center. American Trends Panel Wave 114, fielded September "
                  "13-18, 2022.",
        "method": "Population is respondent's self-reported religious affiliation (F_RELIG) - "
                  "Wave 114 does not carry the finer F_RELTRAD frame variable used in other "
                  "ATP waves in this dataset family. Share saying it is \"essential\" to what "
                  "being a faithful member of their tradition means to them that they attend "
                  "religious services regularly (ESSENT_b_W114). Refused excluded from each "
                  "row's denominator. Groups under 30 valid respondents omitted. Weighted by "
                  "the dataset's own WEIGHT_W114 variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "attend_services_essential": results,
    }
    with open(
        "docs/datasets/pew-atp-w114-2022/essent-attend.json", "w", encoding="utf-8"
    ) as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:26} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-atp-w114-2022/essent-attend.json")


if __name__ == "__main__":
    main()

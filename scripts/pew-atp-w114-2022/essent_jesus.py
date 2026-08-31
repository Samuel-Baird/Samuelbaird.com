"""
ATP Wave 114 (September 2022): how essential is a personal relationship
with Jesus Christ to what being a faithful member of your religious
tradition means? ESSENT_k_W114 is one item in Wave 114's ESSENT battery
("How important is each of the following to what being [Christian/Jewish/
Muslim/Buddhist/Hindu/faithful to your religious tradition] means to
you?"). This item ("Having a personal relationship with Jesus Christ")
was piped only to respondents whose religion involves Jesus Christ in
Pew's framing - confirmed against the .sav, valid responses appear only
for Protestant, Roman Catholic, Mormon, and Orthodox Christian
respondents (Jewish/Muslim/Buddhist/Hindu/Other/unaffiliated all show
zero valid responses on this item, as expected from the piped question
text).

Like christian_nation.py in this same folder, this wave has no F_RELTRAD
frame variable, so the breakout uses F_RELIG (self-reported affiliation).

A personal relationship with Jesus Christ is a recurring emphasis in
Latter-day Saint teaching and General Conference discourse, so this is a
genuine doctrine-vs-data comparison, not a coincidental crosstab.

Usage: python scripts/pew-atp-w114-2022/essent_jesus.py
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
}
ESSENTIAL = 1.0
VALID_CODES = {1.0, 2.0, 3.0}
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(
        SAV, usecols=["F_RELIG", "ESSENT_k_W114", "WEIGHT_W114"]
    )
    weight = df["WEIGHT_W114"].to_numpy()
    relig = df["F_RELIG"].to_numpy()
    essent = df["ESSENT_k_W114"].to_numpy()

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
                  "being a faithful member of their tradition means to them that they have \"a "
                  "personal relationship with Jesus Christ\" (ESSENT_k_W114). This item was "
                  "piped only to respondents whose tradition centers on Jesus Christ; Jewish, "
                  "Muslim, Buddhist, Hindu, Other, and unaffiliated respondents show zero valid "
                  "responses and are excluded. Refused excluded from each row's denominator. "
                  "Groups under 30 valid respondents omitted. Weighted by the dataset's own "
                  "WEIGHT_W114 variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "personal_relationship_jesus_essential": results,
    }
    with open(
        "docs/datasets/pew-atp-w114-2022/essent-jesus.json", "w", encoding="utf-8"
    ) as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:26} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-atp-w114-2022/essent-jesus.json")


if __name__ == "__main__":
    main()

"""
ATP Wave 114 (September 2022): how essential is believing in God to what
being a faithful member of your religious tradition means? ESSENT_a_W114
is one item in Wave 114's ESSENT battery ("How important is each of the
following to what being [Christian/Jewish/Muslim/Buddhist/Hindu/faithful
to your religious tradition] means to you?"). Like ESSENT_b (attendance,
see essent_attend.py in this folder), this item was piped to every
religiously affiliated respondent regardless of tradition, so it covers
the same wide set of groups: Protestant, Catholic, Mormon, Orthodox
Christian, Jewish, Muslim, Buddhist, and Hindu (Atheist/Agnostic/Nothing
in particular show zero valid responses, as expected from the piped
question text; "Other" is excluded as an incoherent tradition, matching
this folder's other two ESSENT scripts).

Belief in a living, personal God is foundational to Latter-day Saint
theology (the First Vision, D&C 130:22's teaching that God has a
tangible, corporeal form), so this is a genuine doctrine-vs-data
comparison, not a coincidental crosstab. Distinct from the already-
shipped pew-rls-2014 "absolutely certain God exists" chart, which asks
about certainty of God's existence in the abstract - this item asks
whether believing in God is essential to one's own faith *identity*,
a different construct.

Like christian_nation.py in this same folder, this wave has no F_RELTRAD
frame variable, so the breakout uses F_RELIG (self-reported affiliation).

Usage: python scripts/pew-atp-w114-2022/essent_believe_god.py
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
VALID_CODES = {1.0, 2.0, 3.0, 4.0}
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(
        SAV, usecols=["F_RELIG", "ESSENT_a_W114", "WEIGHT_W114"]
    )
    weight = df["WEIGHT_W114"].to_numpy()
    relig = df["F_RELIG"].to_numpy()
    essent = df["ESSENT_a_W114"].to_numpy()

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
                  "being a faithful member of their tradition means to them that they believe "
                  "in God (ESSENT_a_W114). Refused excluded from each row's denominator. "
                  "Groups under 30 valid respondents omitted. Weighted by the dataset's own "
                  "WEIGHT_W114 variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "believe_in_god_essential": results,
    }
    with open(
        "docs/datasets/pew-atp-w114-2022/essent-believe-god.json", "w", encoding="utf-8"
    ) as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:26} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-atp-w114-2022/essent-believe-god.json")


if __name__ == "__main__":
    main()

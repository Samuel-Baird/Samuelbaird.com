"""
Fourth chart for ATP Wave 132 (July 31-Aug. 6, 2023): how important is
spirituality in your life (SPIRIMP_W132), by religious tradition?

Same F_RELIG frame variable as this dataset's other charts (beyond_this_
world.py, has_cross.py, religious_community.py) - see beyond_this_world.py's
docstring for why F_RELIG is the right frame here (Wave 132 has no
F_RELTRAD).

SPIRIMP_W132 was asked of all respondents: "How important is spirituality
in your life?" (Very/Somewhat/Not too/Not at all important). Latter-day
Saints call spirituality "very important" at 66.5%, the highest of any
Christian tradition in the wave - ahead of Protestants (60.1%) and far
ahead of Catholics (36.3%) - and essentially tied with Muslims (66.7%), the
single highest group. This is a distinct construct from this dataset's
already-shipped beyond-this-world.json (a specific "connection beyond this
world" feeling item) and religious-community.json (institutional/
congregational involvement) - this one is a direct self-rating of how
central spirituality is to one's own life.

Groups under 30 valid respondents are dropped (MIN_VALID_N, matching every
other chart in this pipeline).

Usage: python scripts/pew-atp-w132-2023/spirituality_important.py
"""
import json

import numpy as np
import pyreadstat

SAV = "data/pew-atp-w132-2023/ATP W132.sav"

RELIG_CODES = {
    1.0: "Protestant",
    2.0: "Catholic",
    3.0: "Mormon",
    4.0: "Orthodox Christian",
    5.0: "Jewish",
    6.0: "Muslim",
    7.0: "Buddhist",
    8.0: "Hindu",
    9.0: "Atheist",
    10.0: "Agnostic",
    11.0: "Other",
    12.0: "Nothing in particular",
}
VERY_IMPORTANT = 1.0
VALID_CODES = {1.0, 2.0, 3.0, 4.0}
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["F_RELIG", "SPIRIMP_W132", "WEIGHT_W132"])
    weight = df["WEIGHT_W132"].to_numpy()
    relig = df["F_RELIG"].to_numpy()
    spirimp = df["SPIRIMP_W132"].to_numpy()

    results = {}
    for code, label in RELIG_CODES.items():
        group_mask = relig == code
        valid = group_mask & np.isin(spirimp, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        yes = valid & (spirimp == VERY_IMPORTANT)
        results[label] = {
            "pct": round(100 * weight[yes].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(spirimp, list(VALID_CODES))
    yes_all = valid_all & (spirimp == VERY_IMPORTANT)
    results["All U.S. adults"] = {
        "pct": round(100 * weight[yes_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }

    order = [label for label in results if label != "All U.S. adults"]
    order.sort(key=lambda label: -results[label]["pct"])
    order.append("All U.S. adults")

    out = {
        "source": "Pew Research Center. American Trends Panel Wave 132, fielded July 31-Aug. 6, 2023.",
        "method": "Population is respondent's religion (F_RELIG; this wave has no F_RELTRAD "
                  "frame variable, see this dataset's README). Share answering \"very "
                  "important\" to SPIRIMP_W132 (\"How important is spirituality in your "
                  "life?\", asked of all respondents); refused excluded from each row's "
                  "denominator. Groups under 30 valid respondents omitted. Weighted by the "
                  "dataset's own WEIGHT_W132 variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "spirituality_very_important": results,
    }
    with open("docs/datasets/pew-atp-w132-2023/spirituality-important.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:26} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-atp-w132-2023/spirituality-important.json")


if __name__ == "__main__":
    main()

"""
Flagship chart for ATP Wave 132 (July 31-Aug. 6, 2023): who has had "a
sudden or unexpected feeling of connection with something from beyond this
world" (BEYONDEXP_W132), by religious tradition?

Unlike Wave 70 and other earlier ATP waves in this pipeline, Wave 132 does
NOT carry an F_RELTRAD frame variable - confirmed by reading the .sav's own
column list (data/pew-atp-w132-2023/ATP W132 Readme.txt has no F_RELTRAD
section, and pyreadstat's metadata-only read lists no such column). This
wave instead carries F_RELIG (Pew's "religion" question, unrecoded/
un-collapsed - Mormon/Latter-day Saint respondents are code 3.0) and
F_RELIGCAT1 (a coarser 4-way Protestant/Catholic/Unaffiliated/Other split
with no Mormon category of its own). F_RELIG is the right frame variable
here since it's the finest-grained grouping this wave offers and it keeps
"Mormon" as its own row, matching every other flagship chart's convention.

BEYONDEXP_W132 was asked of all respondents (no attendance/belief gate -
confirmed against the questionnaire's own "ASK ALL" heading). Latter-day
Saints report this experience at a clearly higher rate (75.5%) than any
other named tradition in the wave - Protestants are next among the named
groups at 49.8%, a >25-point gap - which is what makes this a stronger
flagship pick than the wave's many bland belief-in-God-style items (where
Mormons cluster with other highly religious groups rather than standing
out on their own). Likely feeds Pew's Dec. 7, 2023 "Spirituality Among
Americans" report (see this dataset's README for the citation caveat).

Groups under 30 valid respondents would be dropped (MIN_VALID_N, matching
every other chart in this pipeline); none actually fall below that
threshold for this item.

Usage: python scripts/pew-atp-w132-2023/beyond_this_world.py
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
YES = 1.0
VALID_CODES = {1.0, 2.0}
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["F_RELIG", "BEYONDEXP_W132", "WEIGHT_W132"])
    weight = df["WEIGHT_W132"].to_numpy()
    relig = df["F_RELIG"].to_numpy()
    felt = df["BEYONDEXP_W132"].to_numpy()

    results = {}
    for code, label in RELIG_CODES.items():
        group_mask = relig == code
        valid = group_mask & np.isin(felt, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        yes = valid & (felt == YES)
        results[label] = {
            "pct": round(100 * weight[yes].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(felt, list(VALID_CODES))
    yes_all = valid_all & (felt == YES)
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
                  "frame variable, see this dataset's README). Share answering \"yes\" to "
                  "BEYONDEXP_W132 (\"Have you ever had a sudden or unexpected feeling of "
                  "connection with something from beyond this world?\"), asked of all "
                  "respondents; refused excluded from each row's denominator. Groups under "
                  "30 valid respondents omitted. Weighted by the dataset's own WEIGHT_W132 "
                  "variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "felt_beyond_this_world_connection": results,
    }
    with open("docs/datasets/pew-atp-w132-2023/beyond-this-world.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:26} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-atp-w132-2023/beyond-this-world.json")


if __name__ == "__main__":
    main()

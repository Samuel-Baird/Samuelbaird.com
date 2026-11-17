"""
Second flagship chart for ATP Wave 132 (July 31-Aug. 6, 2023): who has a
cross "for spiritual purposes" (SPIRTHINGS_e_W132), by religious tradition?

Same F_RELIG frame variable as this dataset's first chart
(beyond_this_world.py) - see that script's docstring for why F_RELIG is the
right frame here (Wave 132 has no F_RELTRAD).

SPIRTHINGS_e was asked of all respondents as part of a battery ("Do you have
any of the following for spiritual purposes?": jewelry, a tattoo/piercing,
crystals, a home shrine/altar/icon, a cross). Latter-day Saints report
having a cross for spiritual purposes at just 11.7% - far below every other
Christian tradition in the wave (Protestants 41.7%, Catholics 72.8%,
Orthodox Christians 82.0%) and closer to the non-Christian traditions. This
tracks a well-known, doctrinally deliberate LDS distinctive: the Church does
not use the cross as a symbol of the faith (leaders have repeatedly said the
resurrected, living Christ is preferred over an emblem of his death), unlike
most other Christian traditions where the cross is a central symbol. That
makes this a stronger flagship pick than most items in this wave, where
Mormons often cluster with other highly religious groups rather than
standing out on their own.

Groups under 30 valid respondents are dropped (MIN_VALID_N, matching every
other chart in this pipeline).

Usage: python scripts/pew-atp-w132-2023/has_cross.py
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
    df, _ = pyreadstat.read_sav(SAV, usecols=["F_RELIG", "SPIRTHINGS_e_W132", "WEIGHT_W132"])
    weight = df["WEIGHT_W132"].to_numpy()
    relig = df["F_RELIG"].to_numpy()
    has_cross = df["SPIRTHINGS_e_W132"].to_numpy()

    results = {}
    for code, label in RELIG_CODES.items():
        group_mask = relig == code
        valid = group_mask & np.isin(has_cross, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        yes = valid & (has_cross == YES)
        results[label] = {
            "pct": round(100 * weight[yes].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(has_cross, list(VALID_CODES))
    yes_all = valid_all & (has_cross == YES)
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
                  "SPIRTHINGS_e_W132 (has a cross \"for spiritual purposes\", one item in a "
                  "battery asked of all respondents); refused excluded from each row's "
                  "denominator. Groups under 30 valid respondents omitted. Weighted by the "
                  "dataset's own WEIGHT_W132 variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "has_cross_for_spiritual_purposes": results,
    }
    with open("docs/datasets/pew-atp-w132-2023/has-cross.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:26} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-atp-w132-2023/has-cross.json")


if __name__ == "__main__":
    main()

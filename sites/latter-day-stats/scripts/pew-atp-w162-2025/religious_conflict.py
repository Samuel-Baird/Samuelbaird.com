"""
Flagship chart for ATP Wave 162 (February 2025): how much conflict, if any,
respondents feel between their own religious beliefs and mainstream American
culture (RELIGCONFLICT_W162), broken out by present religion.

Unlike every other ATP wave already in this pipeline (see pew-atp-w70-2020),
Wave 162 does NOT carry an F_RELTRAD frame variable - confirmed by listing
every column in the .sav (131 total; no F_RELTRAD, no F_RELTRAD-shaped
name). This wave's own religion-classification variables are RELIGCAT1_W162
(4-category: Protestant/Catholic/Unaffiliated/Other) and RELIGCAT2_W162
(12-category, Protestant/Catholic split further by race), both built for a
wave whose real focus is connection to Catholicism (RELIGCAT2 doesn't even
have its own Mormon/LDS/Jewish/Muslim/etc. codes - they'd all fall in
"Other"). The variable that actually separates out Mormon respondents is
RELIG_W162 ("What is your present religion, if any?", code 3.0 = "Mormon
(Church of Jesus Christ of Latter-day Saints or LDS)") - so this script
groups by RELIG_W162 instead of F_RELTRAD.

RELIGCONFLICT_W162 is the same question Pew's own October 2025 report
("Growing Share of U.S. Adults Say Religion Is Gaining Influence in
American Life", pewresearch.org/religion/2025/10/20/...) leads with: "For
the first time since we began asking this question in 2020, a majority of
U.S. adults (58%) say they feel at least some conflict [between their
religious beliefs and mainstream American culture]." Recomputing that
top-line here (top_2box among valid RELIGCONFLICT codes 1-4, weighted by
WEIGHT_W162) reproduces 58.2%, confirming this script's methodology matches
Pew's. That report explicitly declined to break Mormons out on their own:
"The survey included respondents of many other religious backgrounds,
including members of the Church of Jesus Christ of Latter-day Saints
(widely known as Mormons), Muslims, Hindus and Buddhists. But there are not
enough respondents from these smaller groups to report on their answers
separately." Wave 162's Mormon unweighted N (135) clears this pipeline's
own MIN_VALID_N=30 threshold, so this chart reports the breakout Pew's own
report didn't - and it stands out: at 78.4%, Latter-day Saints report more
conflict between their beliefs and mainstream culture than any other group
in the wave, including Protestants (66.8%) and Catholics (54.9%).

Usage: python scripts/pew-atp-w162-2025/religious_conflict.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pyreadstat

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from chart_style import sort_groups  # noqa: E402

SAV = "data/pew-atp-w162-2025/ATP W162.sav"

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
    11.0: "Something else",
    12.0: "Nothing in particular",
}
VALID_CODES = {1.0, 2.0, 3.0, 4.0}
CONFLICT_CODES = {1.0, 2.0}  # "a great deal of conflict" or "some conflict"
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(
        SAV, usecols=["RELIG_W162", "RELIGCONFLICT_W162", "WEIGHT_W162"]
    )
    weight = df["WEIGHT_W162"].to_numpy()
    relig = df["RELIG_W162"].to_numpy()
    conflict = df["RELIGCONFLICT_W162"].to_numpy()

    results = {}
    for code, label in RELIG_CODES.items():
        group_mask = relig == code
        valid = group_mask & np.isin(conflict, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        yes = valid & np.isin(conflict, list(CONFLICT_CODES))
        results[label] = {
            "pct": round(100 * weight[yes].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(conflict, list(VALID_CODES))
    yes_all = valid_all & np.isin(conflict, list(CONFLICT_CODES))
    results["All U.S. adults"] = {
        "pct": round(100 * weight[yes_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }

    order = sort_groups(list(results.keys()), lambda label: results[label]["pct"])

    out = {
        "source": "Pew Research Center. American Trends Panel Wave 162, fielded February 3-9, 2025.",
        "method": "Population is respondent's present religion (RELIG_W162; this wave has no "
                  "F_RELTRAD frame variable, unlike other ATP waves in this pipeline - see "
                  "this script's module docstring). Share saying there is \"a great deal of "
                  "conflict\" or \"some conflict\" (vs. \"not much\"/\"no conflict at all\") "
                  "between their own religious beliefs and mainstream American culture "
                  "(RELIGCONFLICT_W162); don't know/refused excluded from each row's "
                  "denominator. Groups under 30 valid respondents omitted. Weighted by the "
                  "dataset's own WEIGHT_W162 variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "religious_belief_conflict": results,
    }
    with open(
        "docs/datasets/pew-atp-w162-2025/religious-conflict.json", "w", encoding="utf-8"
    ) as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:24} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-atp-w162-2025/religious-conflict.json")


if __name__ == "__main__":
    main()

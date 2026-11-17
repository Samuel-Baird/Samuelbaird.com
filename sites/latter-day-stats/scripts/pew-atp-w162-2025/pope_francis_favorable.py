"""
ATP Wave 162 (February 2025): overall opinion of Pope Francis (PPLFAV_a_W162)
by present religion (RELIG_W162 - see religious_conflict.py in this folder
for why this wave groups by RELIG_W162 rather than F_RELTRAD); share with a
very or mostly favorable opinion among those who have heard of him ("never
heard of this person" and refused excluded from the denominator).

The one item in this Catholic-focused wave that was asked of everyone and is
not already a live construct on the site (social trust, trust in government,
retention, and scripture reading all are). Latter-day Saints (63%) view Pope
Francis slightly more favorably than the country as a whole (62% among
those who had heard of him) - a modest but real read on Latter-day Saint-
Catholic relations in the last month of his papacy.

Usage: python scripts/pew-atp-w162-2025/pope_francis_favorable.py
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
ITEM = "PPLFAV_a_W162"
VALID_CODES = {1.0, 2.0, 3.0, 4.0}  # very/mostly favorable, mostly/very unfavorable; 5 = never heard of, refused excluded
FAVORABLE = {1.0, 2.0}
MIN_VALID_N = 30
ALL_LABEL = "All U.S. adults"


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["RELIG_W162", ITEM, "WEIGHT_W162"])
    weight = df["WEIGHT_W162"].to_numpy()
    relig = df["RELIG_W162"].to_numpy()
    x = df[ITEM].to_numpy()

    results = {}
    for code, label in RELIG_CODES.items():
        group_mask = relig == code
        valid = group_mask & np.isin(x, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        fav = valid & np.isin(x, list(FAVORABLE))
        results[label] = {
            "pct": round(100 * weight[fav].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(x, list(VALID_CODES))
    fav_all = valid_all & np.isin(x, list(FAVORABLE))
    results[ALL_LABEL] = {
        "pct": round(100 * weight[fav_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }
    order = sort_groups(list(results.keys()), lambda label: results[label]["pct"])

    out = {
        "source": "Pew Research Center. American Trends Panel Wave 162, fielded February 3-9, 2025.",
        "method": "Population is present religion (RELIG_W162; this wave has no F_RELTRAD). Share "
                  "with a very or mostly favorable opinion of Pope Francis (PPLFAV_a_W162) among "
                  "respondents who had heard of him; 'never heard of this person' and refused are "
                  "excluded from each row's denominator. Groups under 30 valid respondents "
                  "omitted. Weighted by the dataset's own WEIGHT_W162 variable.",
        "total_weighted_n": float(weight[valid_all].sum()),
        "total_unweighted_n": int(valid_all.sum()),
        "group_order": order,
        "pope_francis_favorable": results,
    }
    with open("docs/datasets/pew-atp-w162-2025/pope-francis-favorable.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:24} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-atp-w162-2025/pope-francis-favorable.json")


if __name__ == "__main__":
    main()

"""
ATP Wave 114 (September 2022): how Latter-day Saints view other religious
groups - the reverse of this folder's live relfav_mormons.py (how every
group views Mormons). Rows are the seven groups rated in the RELFAV battery
(RELFAV_a-f, i), the population is Latter-day Saint respondents only
(F_RELIG == 3, n=190), and each row is the share with a very or somewhat
favorable view among those who gave a rating ("don't know enough to say"
and refused excluded from the denominator, so the number reads as
"favorable among those with an opinion").

Among Latter-day Saints who gave a rating, favorable views run 65% for Jews,
61% for mainline Protestants, 60% for Catholics, 57% for evangelicals and 53%
for Muslims - each well above the corresponding national figure. The one
exception is atheists (26%). Their view of their own group (81%) is kept as a
reference row.

Usage: python scripts/pew-atp-w114-2022/lds_views_of_groups.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pyreadstat

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from chart_style import sort_groups  # noqa: E402

SAV = "data/pew-atp-w114-2022/ATP W114.sav"
LDS_CODE = 3.0  # F_RELIG: Mormon (Church of Jesus Christ of Latter-day Saints or LDS)

RATED_GROUPS = {
    "RELFAV_a_W114": "Evangelical Protestant",
    "RELFAV_b_W114": "Catholic",
    "RELFAV_c_W114": "Latter-day Saint",
    "RELFAV_d_W114": "Jewish",
    "RELFAV_e_W114": "Muslim",
    "RELFAV_f_W114": "Atheist",
    "RELFAV_i_W114": "Mainline Protestant",
}
FAVORABLE = {1.0, 2.0}  # very / somewhat favorable
VALID_CODES = {1.0, 2.0, 3.0, 4.0, 5.0}  # excludes 6 "Don't know enough to say" and refused
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["F_RELIG", "WEIGHT_W114"] + list(RATED_GROUPS))
    weight = df["WEIGHT_W114"].to_numpy()
    lds = df["F_RELIG"].to_numpy() == LDS_CODE

    results = {}
    for var, label in RATED_GROUPS.items():
        x = df[var].to_numpy()
        valid = lds & np.isin(x, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        fav = valid & np.isin(x, list(FAVORABLE))
        results[label] = {
            "pct": round(100 * weight[fav].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(lds.sum()),
        }
    order = sort_groups(list(results.keys()), lambda label: results[label]["pct"])

    out = {
        "source": "Pew Research Center. American Trends Panel Wave 114, fielded September "
                  "13-18, 2022.",
        "method": "Population is Latter-day Saint respondents only (F_RELIG code 3, 190 "
                  "unweighted). Each row is the share with a very or somewhat favorable view "
                  "of that group (RELFAV_a-f, i) among Latter-day Saints who gave a rating; "
                  "'don't know enough to say' and refused are excluded from the denominator. "
                  "Rows are the groups being rated, not the respondents' own religion. "
                  "Weighted by the dataset's own WEIGHT_W114 variable.",
        "total_unweighted_n": int(lds.sum()),
        "group_order": order,
        "lds_favorable_view_of_group": results,
    }
    with open("docs/datasets/pew-atp-w114-2022/lds-views-of-groups.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:26} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>4})")
    print("\nWrote docs/datasets/pew-atp-w114-2022/lds-views-of-groups.json")


if __name__ == "__main__":
    main()

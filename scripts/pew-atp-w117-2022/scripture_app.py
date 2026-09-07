"""
ATP Wave 117 (November 2022): 'Do you ever use apps or websites that remind
you or help you to read scripture?' (APPUSE1_c_W117), by religious tradition
(F_RELTRAD); share saying yes. Latter-day Saints (59%) are nearly three
times the national 22% - the Church's Gospel Library app and its
app-based Come, Follow Me study schedule, visible in survey data. The
sibling meditation, gratitude, and prayer apps show no LDS distinctiveness
(LDS 20%/19%/12% vs 19%/19%/15%) and are deliberately not charted.

Same F_RELTRAD group set, MIN_VALID_N floor, and JSON shape as
reads_religion_books.py in this folder; group_order sorted via
chart_style.sort_groups (highest to lowest, "All U.S. adults" pinned to the
bottom).

Usage: python scripts/pew-atp-w117-2022/scripture_app.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pyreadstat

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from chart_style import sort_groups  # noqa: E402

SAV = "data/pew-atp-w117-2022/ATP W117.sav"

RELTRAD_CODES = {
    1100.0: "Evangelical Protestant",
    1200.0: "Mainline Protestant",
    1300.0: "Historically Black Protestant",
    10000.0: "Catholic",
    20000.0: "Mormon",
    30000.0: "Orthodox Christian",
    50000.0: "Jewish",
    100000.0: "Unaffiliated",
}
ITEM = "APPUSE1_c_W117"
YES_CODES = {1.0}  # Yes, do use an app or website that does this
VALID_CODES = {1.0, 2.0}  # yes / no; refused excluded
MIN_VALID_N = 30
ALL_LABEL = "All U.S. adults"


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["F_RELTRAD", ITEM, "WEIGHT_W117"])
    weight = df["WEIGHT_W117"].to_numpy()
    reltrad = df["F_RELTRAD"].to_numpy()
    x = df[ITEM].to_numpy()

    results = {}
    for code, label in RELTRAD_CODES.items():
        group_mask = reltrad == code
        valid = group_mask & np.isin(x, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        yes = valid & np.isin(x, list(YES_CODES))
        results[label] = {
            "pct": round(100 * weight[yes].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(x, list(VALID_CODES))
    yes_all = valid_all & np.isin(x, list(YES_CODES))
    results[ALL_LABEL] = {
        "pct": round(100 * weight[yes_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }
    order = sort_groups(list(results.keys()), lambda label: results[label]["pct"])

    out = {
        "source": "Pew Research Center. American Trends Panel Wave 117, fielded November 16-27, 2022.",
        "method": "Population is respondent's religious tradition (F_RELTRAD). Share saying yes, they use apps or websites that remind them or help them to read scripture, APPUSE1_c_W117; refused "
                  "excluded from each row's denominator. Groups under 30 valid respondents "
                  "omitted. Weighted by the dataset's own WEIGHT_W117 variable.",
        "total_weighted_n": float(weight[valid_all].sum()),
        "total_unweighted_n": int(valid_all.sum()),
        "group_order": order,
        "uses_scripture_app": results,
    }
    with open("docs/datasets/pew-atp-w117-2022/scripture-app.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:26} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-atp-w117-2022/scripture-app.json")


if __name__ == "__main__":
    main()

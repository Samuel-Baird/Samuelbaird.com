"""
ATP Wave 70 (July 2020): among monthly religious-service attenders, who heard
a sermon in the past few months - in person, online or on TV - expressing
support for, opposition to, or both about Donald Trump (SERMONTRUMP_W70)?
Share hearing any such sermon (vs. neither). Gated on XATTEND_W70 like
blm_sermons.py in this folder. Latter-day Saints (12%) are the least likely
of any tradition to have heard the sitting president discussed from the
pulpit, vs. 28% of all attenders - the Church's political-neutrality policy
in what members actually hear at church (the Biden item, SERMONBIDEN_W70,
runs 9% vs. 20% and is not charted separately).

Same 7-group F_RELTRAD set, MIN_VALID_N floor, and JSON shape as
blm_sermons.py / prayer_covid_coping.py in this folder; group_order sorted
via chart_style.sort_groups (highest to lowest, the "All attenders" row pinned to
the bottom).

Usage: python scripts/pew-atp-w70-2020/sermon_about_trump.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pyreadstat

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from chart_style import sort_groups  # noqa: E402

SAV = "data/pew-atp-w70-2020/ATP W70.sav"

RELTRAD_CODES = {
    1100.0: "Evangelical Protestant",
    1200.0: "Mainline Protestant",
    1300.0: "Historically Black Protestant",
    10000.0: "Catholic",
    20000.0: "Mormon",
    50000.0: "Jewish",
    100000.0: "Unaffiliated",
}
ITEM = "SERMONTRUMP_W70"
YES_CODES = {1.0, 2.0, 3.0}  # Support / opposition / both
VALID_CODES = {1.0, 2.0, 3.0, 4.0}  # support / opposition / both / neither; refused excluded
MIN_VALID_N = 30
ALL_LABEL = "All attenders"


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["F_RELTRAD", ITEM, "WEIGHT_W70"])
    weight = df["WEIGHT_W70"].to_numpy()
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
        "source": "Pew Research Center. American Trends Panel Wave 70, fielded July 13-19, 2020.",
        "method": "Population is respondent's religious tradition (F_RELTRAD), restricted to respondents who attend religious services at least monthly (gated on XATTEND_W70). Share who heard a sermon in the past few months expressing support for, opposition to, or both about Donald Trump (vs. neither), SERMONTRUMP_W70; refused excluded from each row's denominator. Groups under 30 "
                  "valid respondents omitted. Weighted by the dataset's own WEIGHT_W70 "
                  "variable.",
        "total_weighted_n": float(weight[valid_all].sum()),
        "total_unweighted_n": int(valid_all.sum()),
        "group_order": order,
        "heard_sermon_about_trump": results,
    }
    with open("docs/datasets/pew-atp-w70-2020/sermon-about-trump.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:30} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-atp-w70-2020/sermon-about-trump.json")


if __name__ == "__main__":
    main()

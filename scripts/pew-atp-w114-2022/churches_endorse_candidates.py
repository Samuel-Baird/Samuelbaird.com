"""
ATP Wave 114 (September 2022): 'During political elections, should churches
and other houses of worship come out in favor of one candidate over
another?' (CHURCH_CAND_W114), by religion (F_RELIG); share saying yes.
Latter-day Saints (11%) are the least likely of any religious group to say
churches should endorse candidates (only atheists and agnostics are lower),
vs. 21% nationally - the Church's long-standing
political-neutrality policy (no endorsements, no use of chapels or
membership lists for partisan purposes) reflected in members' own views.

Same F_RELIG frame and JSON shape as essent_attend.py / christian_nation.py in
this folder (Wave 114 has no F_RELTRAD); asked of all respondents, so the full
12-group set plus a "U.S. adults" row is used. group_order sorted via
chart_style.sort_groups (highest to lowest, "U.S. adults" pinned to the
bottom); groups under MIN_VALID_N dropped.

Usage: python scripts/pew-atp-w114-2022/churches_endorse_candidates.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pyreadstat

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from chart_style import sort_groups  # noqa: E402

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
    9.0: "Atheist",
    10.0: "Agnostic",
    11.0: "Other",
    12.0: "Nothing in particular",
}
ITEM = "CHURCH_CAND_W114"
YES_CODES = {1.0}  # Yes, should do this
VALID_CODES = {1.0, 2.0}  # yes / no; refused excluded
MIN_VALID_N = 30
ALL_LABEL = "U.S. adults"


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["F_RELIG", ITEM, "WEIGHT_W114"])
    weight = df["WEIGHT_W114"].to_numpy()
    relig = df["F_RELIG"].to_numpy()
    x = df[ITEM].to_numpy()

    results = {}
    for code, label in RELIG_CODES.items():
        group_mask = relig == code
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
        "source": "Pew Research Center. American Trends Panel Wave 114, fielded September "
                  "13-18, 2022.",
        "method": "Population is respondent's self-reported religious affiliation (F_RELIG) - "
                  "Wave 114 does not carry the finer F_RELTRAD frame variable used in other "
                  "ATP waves in this dataset family. Share saying yes, churches and other houses of worship should come out in favor of one candidate over another during political elections (vs. no), CHURCH_CAND_W114. Refused excluded from each "
                  "row's denominator. Groups under 30 valid respondents omitted. Weighted by "
                  "the dataset's own WEIGHT_W114 variable.",
        "total_weighted_n": float(weight[valid_all].sum()),
        "total_unweighted_n": int(valid_all.sum()),
        "group_order": order,
        "churches_should_endorse_candidates": results,
    }
    with open("docs/datasets/pew-atp-w114-2022/churches-endorse-candidates.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:26} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-atp-w114-2022/churches-endorse-candidates.json")


if __name__ == "__main__":
    main()

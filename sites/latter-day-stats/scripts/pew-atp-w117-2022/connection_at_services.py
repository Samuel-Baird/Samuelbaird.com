"""
ATP Wave 117 (November 2022): 'When you attend religious services in
person, how much of a connection do you feel with the other people in
attendance?' (CNCTPER_W117), by religious tradition (F_RELTRAD); share
saying a great deal. Asked of respondents who attend in person at least
monthly (Latter-day Saint n=163). Latter-day Saints (45%) are above the
35% of all attenders - the ward as a community, in members' own
description of what services feel like.

Same F_RELTRAD group set, MIN_VALID_N floor, and JSON shape as
reads_religion_books.py in this folder; group_order sorted via
chart_style.sort_groups (highest to lowest, "All U.S. adults" pinned to the
bottom).

Usage: python scripts/pew-atp-w117-2022/connection_at_services.py
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
ITEM = "CNCTPER_W117"
YES_CODES = {1.0}  # A great deal of connection
VALID_CODES = {1.0, 2.0, 3.0, 4.0, 5.0}  # a great deal / quite a bit / some / a little / no connection; refused excluded
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
        "method": "Population is respondent's religious tradition (F_RELTRAD). Share of in-person attenders saying they feel a great deal of connection with the other people in attendance when they attend religious services in person (vs. quite a bit, some, a little, or none), CNCTPER_W117; refused "
                  "excluded from each row's denominator. Groups under 30 valid respondents "
                  "omitted. Weighted by the dataset's own WEIGHT_W117 variable.",
        "total_weighted_n": float(weight[valid_all].sum()),
        "total_unweighted_n": int(valid_all.sum()),
        "group_order": order,
        "great_deal_connection_at_services": results,
    }
    with open("docs/datasets/pew-atp-w117-2022/connection-at-services.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:26} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-atp-w117-2022/connection-at-services.json")


if __name__ == "__main__":
    main()

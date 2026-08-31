"""
2007 U.S. Religious Landscape Survey: how often do people work with children
or youth at the church or house of worship where they attend most often
(q28c), by current religious tradition (RELTRAD)? Top box is "at least once
a week." q28c was asked only of respondents who named a usual place of
worship (35,556 total respondents, 26,205 valid on this item), so every
group's N is below its full RELTRAD count but still comfortably clears the
30-valid floor. Latter-day Saint congregations run entirely on lay
volunteers filling weekly callings, including Primary and youth leadership,
so this item checks that structural feature against every other tradition's
own rate of volunteering with children/youth.

Usage: python scripts/pew-rls-2007/volunteer_with_children.py
"""
import json

import numpy as np
import pyreadstat

SAV = "data/pew-rls-2007/Religious Landscape Survey Data - Continental US.sav"

RELTRAD_CODES = {
    1100.0: "Evangelical Protestant Churches",
    1200.0: "Mainline Protestant Churches",
    1300.0: "Historically Black Protestant Churches",
    10000.0: "Catholic",
    20000.0: "Mormon",
    30000.0: "Orthodox",
    40001.0: "Jehovah's Witness",
    50000.0: "Jewish",
    60000.0: "Muslim",
    70000.0: "Buddhist",
    80000.0: "Hindu",
    100000.0: "Unaffiliated",
}
TOP_BOX = {1.0}  # at least once a week
VALID_CODES = {1.0, 2.0, 3.0, 4.0, 5.0}
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["reltrad", "q28c", "weight"])
    weight = df["weight"].to_numpy()
    reltrad = df["reltrad"].to_numpy()
    q28c = df["q28c"].to_numpy()

    results = {}
    for code, label in RELTRAD_CODES.items():
        group_mask = reltrad == code
        valid = group_mask & np.isin(q28c, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        weekly = valid & np.isin(q28c, list(TOP_BOX))
        results[label] = {
            "pct": round(100 * weight[weekly].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(q28c, list(VALID_CODES))
    weekly_all = valid_all & np.isin(q28c, list(TOP_BOX))
    results["All respondents"] = {
        "pct": round(100 * weight[weekly_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(valid_all.sum()),
    }

    order = [label for label in results if label != "All respondents"]
    order.sort(key=lambda label: -results[label]["pct"])
    order.append("All respondents")

    out = {
        "source": 'Pew Research Center. 2008. "U.S. Religious Landscape Survey."',
        "method": "Population is respondents with a usual place of worship (q28c's own valid "
                  "base, smaller than the full RELTRAD sample), classified by current religious "
                  "tradition (RELTRAD). q28c asked how often the respondent works with children "
                  "or youth at that place of worship; top box is \"at least once a week.\" Don't "
                  "know/refused are excluded from each row's denominator. Groups with fewer than "
                  "30 valid respondents are omitted. Weighted by the dataset's own `weight` "
                  "variable.",
        "total_weighted_n": float(weight[valid_all].sum()),
        "total_unweighted_n": int(valid_all.sum()),
        "group_order": order,
        "weekly_works_with_children_youth": results,
    }
    with open(
        "docs/datasets/pew-rls-2007/volunteer-with-children.json", "w", encoding="utf-8"
    ) as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:34} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-rls-2007/volunteer-with-children.json")


if __name__ == "__main__":
    main()

"""
2014 RLS recontact survey: is "having children" very important, somewhat
important, or not important for a successful marriage (qd1e), by current
religious tradition (reltrad); share saying very important. Asked of the
full sample. Sibling of marriage_shared_beliefs.py (qd1g) in this folder;
checks the Church's teaching that "children are an heritage of the Lord"
and central to marriage against how members rank children among the
ingredients of a successful marriage.

Same population/threshold conventions as parents_talked_religion.py in this
folder: groups under 30 valid respondents are dropped (this recontact
reached only 5,000 of the main 2014 RLS's 35,071 respondents). Row order via
chart_style.sort_groups (highest to lowest, "All U.S. adults" pinned to the
bottom).

Usage: python scripts/pew-rls-2014-recontact/marriage_having_children.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pyreadstat

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from chart_style import sort_groups  # noqa: E402

SAV = "data/pew-rls-2014-recontact/RLS II recontact public release.sav"

RELTRAD_CODES = {
    1100.0: "Evangelical Protestant",
    1200.0: "Mainline Protestant",
    1300.0: "Historically Black Protestant",
    10000.0: "Catholic",
    20000.0: "Mormon",
    100000.0: "Unaffiliated",
}
ITEM = "qd1e"
YES_CODES = {1.0}  # Very important
VALID_CODES = {1.0, 2.0, 3.0}  # very / somewhat / not important; DK/refused excluded
MIN_VALID_N = 30
ALL_LABEL = "All U.S. adults"


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["reltrad", ITEM, "rweight"])
    weight = df["rweight"].to_numpy()
    reltrad = df["reltrad"].to_numpy()
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
        "source": 'Pew Research Center. 2016. "One-in-Five U.S. Adults Were Raised in '
                  'Interfaith Homes."',
        "method": "Population is current religious tradition (reltrad). qd1e asks whether having children is very important, somewhat important, or not important for a successful marriage; this reads the 'very important' top box; "
                  "don't know/refused excluded from each row's denominator. Groups under 30 "
                  "valid respondents omitted (this recontact reached only 5,000 of the main "
                  "2014 RLS's 35,071 respondents). Weighted by the dataset's own `rweight` "
                  "variable.",
        "total_weighted_n": float(weight[valid_all].sum()),
        "total_unweighted_n": int(valid_all.sum()),
        "group_order": order,
        "having_children_very_important": results,
    }
    with open("docs/datasets/pew-rls-2014-recontact/marriage-having-children.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:32} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>4})")
    print("\nWrote docs/datasets/pew-rls-2014-recontact/marriage-having-children.json")


if __name__ == "__main__":
    main()

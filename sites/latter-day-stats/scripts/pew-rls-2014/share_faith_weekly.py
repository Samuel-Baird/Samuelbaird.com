"""
2014 Religious Landscape Study: how often respondents "share your faith with
non-believers or people from other religious backgrounds" (qi2g), by current
religious tradition (RELTRAD); share saying at least once a week. Asked of
religiously affiliated respondents only (the unaffiliated were skipped, so
they drop out under the 30-valid floor rather than being shown as zero).
Same weekly+ top-box convention as this site's other qi2-battery charts
(scripture reading outside services, prayer/scripture study groups).

The Church's missionary program is the most visible faith-sharing
institution in American religion, so this checks how often ordinary
members actually do it: Latter-day Saints (33.3%) land 4th of 11
traditions, behind Jehovah's Witnesses (77.4%), Historically Black
Protestants (45.4%), and Evangelical Protestants (36.1%) - a reminder that
formal full-time missions and everyday member faith-sharing are different
things. Row order via chart_style.sort_groups (highest to lowest, "All
U.S. adults" pinned to the bottom).

Usage: python scripts/pew-rls-2014/share_faith_weekly.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pyreadstat

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from chart_style import sort_groups  # noqa: E402

SAV = ("data/pew-rls-2014/"
       "Dataset - Pew Research Center 2014 Religious Landscape Study National Telephone "
       "Survey - Version 1.1 - December 1 2016.sav")

RELTRAD_CODES = {
    1100.0: "Evangelical Protestant",
    1200.0: "Mainline Protestant",
    1300.0: "Historically Black Protestant",
    10000.0: "Catholic",
    20000.0: "Mormon",
    30000.0: "Orthodox Christian",
    40001.0: "Jehovah's Witness",
    50000.0: "Jewish",
    60000.0: "Muslim",
    70000.0: "Buddhist",
    80000.0: "Hindu",
    100000.0: "Unaffiliated",
}
ITEM = "qi2g"
WEEKLY_CODE = {1.0}  # At least once a week
VALID_CODES = {1.0, 2.0, 3.0, 4.0, 5.0}  # weekly ... never; 9 = DK/refused excluded
MIN_VALID_N = 30
ALL_LABEL = "All U.S. adults"


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["RELTRAD", ITEM, "WEIGHT"])
    weight = df["WEIGHT"].to_numpy()
    reltrad = df["RELTRAD"].to_numpy()
    x = df[ITEM].to_numpy()

    results = {}
    for code, label in RELTRAD_CODES.items():
        group_mask = reltrad == code
        valid = group_mask & np.isin(x, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        weekly = valid & np.isin(x, list(WEEKLY_CODE))
        results[label] = {
            "pct": round(100 * weight[weekly].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(x, list(VALID_CODES))
    weekly_all = valid_all & np.isin(x, list(WEEKLY_CODE))
    results[ALL_LABEL] = {
        "pct": round(100 * weight[weekly_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }
    order = sort_groups(list(results.keys()), lambda label: results[label]["pct"])

    out = {
        "source": 'Pew Research Center. 2015. "2014 Religious Landscape Study."',
        "method": "Population is religiously affiliated respondents (qi2g was not asked of the "
                  "unaffiliated), classified by current religious tradition (RELTRAD). Share "
                  "saying they share their faith with non-believers or people from other "
                  "religious backgrounds at least once a week; volunteered don't know/refused "
                  "is excluded from each row's denominator. Groups with fewer than 30 valid "
                  "respondents are omitted. 'All U.S. adults' here means all affiliated "
                  "respondents who were asked. Weighted by the dataset's own national WEIGHT "
                  "variable.",
        "total_weighted_n": float(weight[valid_all].sum()),
        "total_unweighted_n": int(valid_all.sum()),
        "group_order": order,
        "shares_faith_weekly": results,
    }
    with open("docs/datasets/pew-rls-2014/share-faith-weekly.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:38} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-rls-2014/share-faith-weekly.json")


if __name__ == "__main__":
    main()

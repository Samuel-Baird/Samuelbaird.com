"""
Fifth chart for ATP Wave 132 (July 31-Aug. 6, 2023): who has a tattoo or
piercing "for spiritual purposes" (SPIRTHINGS_b_W132), by religious
tradition?

Same F_RELIG frame variable as this dataset's other charts (beyond_this_
world.py, has_cross.py, religious_community.py, spirituality_important.py)
- see beyond_this_world.py's docstring for why F_RELIG is the right frame
here (Wave 132 has no F_RELTRAD).

SPIRTHINGS_b was asked of all respondents as part of the same "Do you have
any of the following for spiritual purposes?" battery already tapped for
has-cross.json (SPIRTHINGS_e). Latter-day Saints report having a tattoo or
piercing for spiritual purposes at just 6.5% - the lowest of any Christian
tradition in the wave (Protestants 8.3%, Catholics 7.8%, Orthodox Christians
10.4%), essentially tied with Atheists (6.0%) and above only Muslims (4.3%)
among all twelve named groups. This tracks a real LDS teaching: the Church
counsels members to keep the body - "a temple" per 1 Corinthians 6:19-20 -
free of tattoos and to use discretion with piercings, unlike most other
Christian traditions which have no comparable body-modification counsel
tied to spiritual practice. Distinct construct from has-cross.json (a
specific religious symbol) and the other SPIRTHINGS sub-items not charted
(jewelry and home shrine/altar, both checked and found weaker/less clean
distinctiveness stories - see this dataset's EXPLORATION_LOG.md entry).

Groups under 30 valid respondents are dropped (MIN_VALID_N, matching every
other chart in this pipeline).

Usage: python scripts/pew-atp-w132-2023/tattoo_piercing_spiritual.py
"""
import json

import numpy as np
import pyreadstat

SAV = "data/pew-atp-w132-2023/ATP W132.sav"

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
YES = 1.0
VALID_CODES = {1.0, 2.0}
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["F_RELIG", "SPIRTHINGS_b_W132", "WEIGHT_W132"])
    weight = df["WEIGHT_W132"].to_numpy()
    relig = df["F_RELIG"].to_numpy()
    tattoo = df["SPIRTHINGS_b_W132"].to_numpy()

    results = {}
    for code, label in RELIG_CODES.items():
        group_mask = relig == code
        valid = group_mask & np.isin(tattoo, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        yes = valid & (tattoo == YES)
        results[label] = {
            "pct": round(100 * weight[yes].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(tattoo, list(VALID_CODES))
    yes_all = valid_all & (tattoo == YES)
    results["All U.S. adults"] = {
        "pct": round(100 * weight[yes_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }

    order = [label for label in results if label != "All U.S. adults"]
    order.sort(key=lambda label: -results[label]["pct"])
    order.append("All U.S. adults")

    out = {
        "source": "Pew Research Center. American Trends Panel Wave 132, fielded July 31-Aug. 6, 2023.",
        "method": "Population is respondent's religion (F_RELIG; this wave has no F_RELTRAD "
                  "frame variable, see this dataset's README). Share answering \"yes\" to "
                  "SPIRTHINGS_b_W132 (has a tattoo or piercing \"for spiritual purposes\", one "
                  "item in a battery asked of all respondents); refused excluded from each "
                  "row's denominator. Groups under 30 valid respondents omitted. Weighted by "
                  "the dataset's own WEIGHT_W132 variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "tattoo_or_piercing_for_spiritual_purposes": results,
    }
    with open("docs/datasets/pew-atp-w132-2023/tattoo-piercing-spiritual.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:26} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-atp-w132-2023/tattoo-piercing-spiritual.json")


if __name__ == "__main__":
    main()

"""
Third flagship chart for ATP Wave 132 (July 31-Aug. 6, 2023): who is
involved in "a religious community, such as a church or religious
congregation" (SPIRCOM1_a_W132), by religious tradition?

Same F_RELIG frame variable as this dataset's other charts (beyond_this_
world.py, has_cross.py) - see beyond_this_world.py's docstring for why
F_RELIG is the right frame here (Wave 132 has no F_RELTRAD).

SPIRCOM1_a was asked of all respondents as part of a battery ("Are you
involved in any of the following types of communities?": a religious
community, a spiritual community, a nonreligious volunteer/community
service group). Latter-day Saints report being involved in a religious
community at 81.4% - the highest rate of any named tradition in the wave,
ahead of Orthodox Christians (77.2%) and well ahead of Protestants (59.0%)
and Catholics (49.6%). This matches the LDS Church's well-known emphasis on
lay congregational participation (ward and stake callings, weekly meetings,
home/visiting teaching-style ministering) rather than being a coincidental
correlation - LDS practice is structurally built around congregational
involvement more than most traditions'.

Groups under 30 valid respondents are dropped (MIN_VALID_N, matching every
other chart in this pipeline).

Usage: python scripts/pew-atp-w132-2023/religious_community.py
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
    df, _ = pyreadstat.read_sav(SAV, usecols=["F_RELIG", "SPIRCOM1_a_W132", "WEIGHT_W132"])
    weight = df["WEIGHT_W132"].to_numpy()
    relig = df["F_RELIG"].to_numpy()
    involved = df["SPIRCOM1_a_W132"].to_numpy()

    results = {}
    for code, label in RELIG_CODES.items():
        group_mask = relig == code
        valid = group_mask & np.isin(involved, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        yes = valid & (involved == YES)
        results[label] = {
            "pct": round(100 * weight[yes].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(involved, list(VALID_CODES))
    yes_all = valid_all & (involved == YES)
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
                  "SPIRCOM1_a_W132 (involved in \"a religious community, such as a church or "
                  "religious congregation,\" one item in a battery asked of all respondents); "
                  "refused excluded from each row's denominator. Groups under 30 valid "
                  "respondents omitted. Weighted by the dataset's own WEIGHT_W132 variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "involved_in_religious_community": results,
    }
    with open("docs/datasets/pew-atp-w132-2023/religious-community.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:26} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-atp-w132-2023/religious-community.json")


if __name__ == "__main__":
    main()

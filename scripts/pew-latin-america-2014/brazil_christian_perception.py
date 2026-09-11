"""
One-off Brazil-angle chart for Religion in Latin America: within Brazil
alone, how do Brazilians rate different groups' claim to the Christian
label? Q63a/Q63b/Q63d/Q63e/Q63f each ask "Do you personally consider
[group] to be followers of the Christian faith, or not?" for Catholics,
Protestants/Evangelicals, Jehovah's Witnesses, Mormons, and Spiritists/
Kardecists in turn. Filtered to Country=Brazil only (unlike
mormons_as_christian.py, which pools all 19 countries/territories and
breaks out by the respondent's own religion) - this is the single-country,
cross-group comparison companion to that pooled, cross-country chart.
Catholics are included as the obvious ceiling case (a respondent's own
tradition, in the majority-Catholic country the survey was fielded in)
against which the other groups' numbers read.

Usage: python scripts/pew-latin-america-2014/brazil_christian_perception.py
"""
import json

import numpy as np
import pyreadstat

SAV = "data/pew-latin-america-2014/Religion in Latin America Dataset.sav"

GROUP_ITEMS = {
    "Q63a": "Catholics",
    "Q63b": "Protestants/Evangelicals",
    "Q63d": "Jehovah's Witnesses",
    "Q63e": "Mormons",
    "Q63f": "Spiritists/Kardecists",
}
YES = 1.0
NO = 2.0
NEVER_HEARD = 3.0
VALID_CODES = {YES, NO, NEVER_HEARD}
BRAZIL_CODE = 3.0

HIGHLIGHT = "Mormons"


def main():
    usecols = ["Country", "WEIGHT", *GROUP_ITEMS.keys()]
    df, _ = pyreadstat.read_sav(SAV, usecols=usecols)
    weight = df["WEIGHT"].to_numpy()
    brazil = df["Country"].to_numpy() == BRAZIL_CODE

    results = {}
    for col, label in GROUP_ITEMS.items():
        item = df[col].to_numpy()
        valid = brazil & np.isin(item, list(VALID_CODES))
        yes = valid & (item == YES)
        results[label] = {
            "pct": round(100 * weight[yes].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
        }

    order = sorted(results, key=lambda label: -results[label]["pct"])

    out = {
        "source": 'Pew Research Center. 2014. "Religion in Latin America: Widespread Change '
                  'in a Historically Catholic Region."',
        "method": "Population is Brazil respondents only (Country=Brazil). Share answering "
                  "\"yes\" to each of Q63a/Q63b/Q63d/Q63e/Q63f (\"Do you personally consider "
                  "[group] to be followers of the Christian faith, or not?\"); don't know/"
                  "refused excluded, \"never heard of group\" retained as a valid non-yes "
                  "response. Weighted by the dataset's own combined base/post-stratification "
                  "WEIGHT.",
        "brazil_weighted_n": float(weight[brazil].sum()),
        "brazil_unweighted_n": int(brazil.sum()),
        "highlight": HIGHLIGHT,
        "group_order": order,
        "consider_christian_brazil": results,
    }
    with open("docs/datasets/pew-latin-america-2014/brazil-christian-perception.json",
              "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:26} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>6})")
    print("\nWrote docs/datasets/pew-latin-america-2014/brazil-christian-perception.json")


if __name__ == "__main__":
    main()

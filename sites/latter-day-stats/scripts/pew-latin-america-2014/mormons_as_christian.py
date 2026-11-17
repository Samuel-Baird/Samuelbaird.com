"""
Flagship chart for Religion in Latin America: do Catholics, Protestants,
and the unaffiliated across the region consider Mormons to be followers of
the Christian faith? Q63e asked "Do you personally consider Mormons to be
followers of the Christian faith, or not?" of all respondents across the
19 countries/territories surveyed; broken out by the respondent's own
current religion (QCURRELrec). "Never heard of group" is treated as its
own outcome, not folded into don't-know, since it's a substantively
different (and, per Q63's own design, expected) response for a small
regional minority most Latin Americans have limited exposure to.

Usage: python scripts/pew-latin-america-2014/mormons_as_christian.py
"""
import json

import numpy as np
import pyreadstat

SAV = "data/pew-latin-america-2014/Religion in Latin America Dataset.sav"

RELIGION_CODES = {1.0: "Catholic", 2.0: "Protestant/Evangelical", 3.0: "Other religion", 4.0: "Unaffiliated"}
YES = 1.0
NO = 2.0
NEVER_HEARD = 3.0
VALID_CODES = {YES, NO, NEVER_HEARD}


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["QCURRELrec", "Q63e", "WEIGHT"])
    weight = df["WEIGHT"].to_numpy()
    religion = df["QCURRELrec"].to_numpy()
    mormon_christian = df["Q63e"].to_numpy()

    results = {}
    for code, label in RELIGION_CODES.items():
        group_mask = religion == code
        valid = group_mask & np.isin(mormon_christian, list(VALID_CODES))
        yes = valid & (mormon_christian == YES)
        results[label] = {
            "pct": round(100 * weight[yes].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(mormon_christian, list(VALID_CODES))
    yes_all = valid_all & (mormon_christian == YES)
    results["All respondents"] = {
        "pct": round(100 * weight[yes_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }

    order = sorted(results, key=lambda label: -results[label]["pct"])
    order.remove("All respondents")
    order.append("All respondents")

    out = {
        "source": 'Pew Research Center. 2014. "Religion in Latin America: Widespread Change '
                  'in a Historically Catholic Region."',
        "method": "Population is respondent's own current religion (QCURRELrec), pooled "
                  "across all 18 Latin American/Caribbean countries and Puerto Rico. Share "
                  "answering \"yes\" to Q63e (\"Do you personally consider Mormons to be "
                  "followers of the Christian faith, or not?\"); don't know/refused excluded, "
                  "\"never heard of group\" retained as a valid non-yes response rather than "
                  "treated as missing. Weighted by the dataset's own combined base/"
                  "post-stratification WEIGHT.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "consider_mormons_christian": results,
    }
    with open("docs/datasets/pew-latin-america-2014/mormons-as-christian.json",
              "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:26} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>6})")
    print("\nWrote docs/datasets/pew-latin-america-2014/mormons-as-christian.json")


if __name__ == "__main__":
    main()

"""
Second flagship-style chart for Religion in Latin America: do people
across the region believe the bread and wine actually become the body and
blood of Christ during communion? Q60m asked "Do you believe that in
communion, the bread and wine actually become the body and blood of
Christ, or not?" of all respondents across the 18 countries/Puerto Rico
surveyed - not Catholics only - broken out by the respondent's own current
religion (QCURRELrec), same group set and weighting as
mormons_as_christian.py in this folder.

Hook: Corpus Christi, May 27 2027.

Usage: python scripts/pew-latin-america-2014/transubstantiation.py
"""
import json

import numpy as np
import pyreadstat

SAV = "data/pew-latin-america-2014/Religion in Latin America Dataset.sav"

RELIGION_CODES = {1.0: "Catholic", 2.0: "Protestant/Evangelical", 3.0: "Other religion", 4.0: "Unaffiliated"}
YES = 1.0
NO = 2.0
VALID_CODES = {YES, NO}


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["QCURRELrec", "Q60m", "WEIGHT"])
    weight = df["WEIGHT"].to_numpy()
    religion = df["QCURRELrec"].to_numpy()
    transub = df["Q60m"].to_numpy()

    results = {}
    for code, label in RELIGION_CODES.items():
        group_mask = religion == code
        valid = group_mask & np.isin(transub, list(VALID_CODES))
        yes = valid & (transub == YES)
        results[label] = {
            "pct": round(100 * weight[yes].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(transub, list(VALID_CODES))
    yes_all = valid_all & (transub == YES)
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
                  "answering \"yes\" to Q60m (\"Do you believe that in communion, the bread "
                  "and wine actually become the body and blood of Christ, or not?\"); don't "
                  "know/refused excluded. Weighted by the dataset's own combined base/"
                  "post-stratification WEIGHT.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "believe_transubstantiation": results,
    }
    with open("docs/datasets/pew-latin-america-2014/transubstantiation.json",
              "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:26} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>6})")
    print("\nWrote docs/datasets/pew-latin-america-2014/transubstantiation.json")


if __name__ == "__main__":
    main()

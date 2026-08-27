"""
Fifth flagship chart for Religion in Latin America: how many people
believe magic, sorcery, or witchcraft can influence people's lives
(Q60h), by the respondent's own current religion (QCURRELrec)? A
folk-belief item that tests how much traditional/syncretic practice
persists alongside official religious affiliation across the region.
Population is pooled across all 18 Latin American/Caribbean countries and
Puerto Rico, same scope as mormons_as_christian.py in this folder.

Usage: python scripts/pew-latin-america-2014/witchcraft_belief.py
"""
import json

import numpy as np
import pyreadstat

SAV = "data/pew-latin-america-2014/Religion in Latin America Dataset.sav"

RELIGION_CODES = {1.0: "Catholic", 2.0: "Protestant/Evangelical", 3.0: "Other religion", 4.0: "Unaffiliated"}
YES = 1.0
VALID_CODES = {1.0, 2.0}


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["QCURRELrec", "Q60h", "WEIGHT"])
    weight = df["WEIGHT"].to_numpy()
    religion = df["QCURRELrec"].to_numpy()
    witchcraft = df["Q60h"].to_numpy()

    results = {}
    for code, label in RELIGION_CODES.items():
        group_mask = religion == code
        valid = group_mask & np.isin(witchcraft, list(VALID_CODES))
        yes = valid & (witchcraft == YES)
        results[label] = {
            "pct": round(100 * weight[yes].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(witchcraft, list(VALID_CODES))
    yes_all = valid_all & (witchcraft == YES)
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
                  "answering \"yes\" to Q60h (\"can magic, sorcery, or witchcraft influence "
                  "people's lives\"); don't know/refused excluded from each row's "
                  "denominator. Weighted by the dataset's own combined base/"
                  "post-stratification WEIGHT.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "believe_witchcraft": results,
    }
    with open("docs/datasets/pew-latin-america-2014/witchcraft-belief.json",
              "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:26} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>6})")
    print("\nWrote docs/datasets/pew-latin-america-2014/witchcraft-belief.json")


if __name__ == "__main__":
    main()

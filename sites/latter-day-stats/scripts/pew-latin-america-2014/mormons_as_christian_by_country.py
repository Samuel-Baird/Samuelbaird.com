"""
One-off Brazil-angle chart for Religion in Latin America: same Q63e item as
mormons_as_christian.py ("Do you personally consider Mormons to be followers
of the Christian faith, or not?"), but read by country instead of by the
respondent's own religion - does a country's LDS presence predict whether
its people consider Mormons Christian? Brazil, home to the region's largest
LDS population, turns out to sit mid-pack (42.7%), well below Chile (56.6%)
and Bolivia (56.0%), each with far smaller LDS communities.

Usage: python scripts/pew-latin-america-2014/mormons_as_christian_by_country.py
"""
import json

import numpy as np
import pyreadstat

SAV = "data/pew-latin-america-2014/Religion in Latin America Dataset.sav"

YES = 1.0
NO = 2.0
NEVER_HEARD = 3.0
VALID_CODES = {YES, NO, NEVER_HEARD}

HIGHLIGHT = "Brazil"


def main():
    df, meta = pyreadstat.read_sav(SAV, usecols=["Country", "Q63e", "WEIGHT"])
    country_labels = meta.variable_value_labels["Country"]
    weight = df["WEIGHT"].to_numpy()
    country = df["Country"].to_numpy()
    mormon_christian = df["Q63e"].to_numpy()

    results = {}
    for code, label in country_labels.items():
        mask = country == code
        valid = mask & np.isin(mormon_christian, list(VALID_CODES))
        yes = valid & (mormon_christian == YES)
        results[label] = {
            "pct": round(100 * weight[yes].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
        }

    order = sorted(results, key=lambda label: -results[label]["pct"])

    out = {
        "source": 'Pew Research Center. 2014. "Religion in Latin America: Widespread Change '
                  'in a Historically Catholic Region."',
        "method": "Share answering \"yes\" to Q63e (\"Do you personally consider Mormons to "
                  "be followers of the Christian faith, or not?\"), by country/territory; "
                  "don't know/refused excluded, \"never heard of group\" retained as a valid "
                  "non-yes response. Weighted by the dataset's own combined base/"
                  "post-stratification WEIGHT.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "highlight": HIGHLIGHT,
        "country_order": order,
        "consider_mormons_christian_by_country": results,
    }
    with open("docs/datasets/pew-latin-america-2014/mormons-as-christian-by-country.json",
              "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:22} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>6})")
    print("\nWrote docs/datasets/pew-latin-america-2014/mormons-as-christian-by-country.json")


if __name__ == "__main__":
    main()

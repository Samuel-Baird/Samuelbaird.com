"""
One-off Brazil-angle chart for Religion in Latin America: how many people in
each of the 19 countries/territories surveyed say they've never heard of
Mormons? Q63e asked "Do you personally consider Mormons to be followers of
the Christian faith, or not?" of all respondents; "never heard of group" is
its own coded response (not folded into don't-know - see
mormons_as_christian.py's own docstring for why), and reading it by country
instead of by own-religion turns the same question into an awareness measure
rather than a Christian-identity measure. Brazil - home to the region's
largest LDS population - comes out at 0.0%, the only country at zero.

Usage: python scripts/pew-latin-america-2014/never_heard_of_mormons.py
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
        never = valid & (mormon_christian == NEVER_HEARD)
        results[label] = {
            "pct": round(100 * weight[never].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
        }

    order = sorted(results, key=lambda label: -results[label]["pct"])

    out = {
        "source": 'Pew Research Center. 2014. "Religion in Latin America: Widespread Change '
                  'in a Historically Catholic Region."',
        "method": "Share answering \"never heard of group\" to Q63e (\"Do you personally "
                  "consider Mormons to be followers of the Christian faith, or not?\"), by "
                  "country/territory. Weighted by the dataset's own combined base/"
                  "post-stratification WEIGHT.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "highlight": HIGHLIGHT,
        "country_order": order,
        "never_heard_of_mormons": results,
    }
    with open("docs/datasets/pew-latin-america-2014/never-heard-of-mormons.json",
              "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:22} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>6})")
    print("\nWrote docs/datasets/pew-latin-america-2014/never-heard-of-mormons.json")


if __name__ == "__main__":
    main()

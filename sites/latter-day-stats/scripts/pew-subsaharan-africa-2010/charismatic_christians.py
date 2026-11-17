"""Flagship chart for Pew's 2010 Sub-Saharan Africa survey: among
respondents who identify as Christian (Q32), what share also describe
themselves as a Charismatic Christian (Q36D)? Broken out by country
(COUNTRY), the survey's natural comparison axis - this is a 19-country
general-population survey, not a U.S./LDS-focused one, so there is no
religious-tradition frame variable here the way pew-atp-w70-2020 has
F_RELTRAD.

Q36D was only asked of respondents who identified as Christian at Q32
(confirmed against the raw missingness pattern: valid Q36D answers total
15,542 across the 19 countries, versus 15,417 respondents coding
Christian at Q32 - the small excess is a handful of Q32 refusals who
still got asked Q36D, not a broken skip pattern). So this chart's
population is self-identified Christians within each country, not each
country's general population.

Djibouti has only 24 valid Christian respondents (it is an overwhelmingly
Muslim country) and is dropped under the site's 30-valid-respondent floor.
Of the remaining 18 countries, only the top 12 by value are charted, to
stay within this pipeline's established row-count precedent (RLS-era
magnitude bars top out around 13 rows) - the other 6 (Mozambique, Kenya,
Chad, Cameroon, Liberia, Tanzania) are noted as omitted in the JSON and
the chart's own caption/README rather than silently dropped.

Usage: python scripts/pew-subsaharan-africa-2010/charismatic_christians.py
"""
import json

import numpy as np
import pyreadstat

SAV = "data/pew-subsaharan-africa-2010/2020update7.31.sav"

CHRISTIAN_CODE = 1.0
YES = 1.0
VALID_CODES = {1.0, 2.0}
MIN_VALID_N = 30
TOP_N = 12


def main():
    df, meta = pyreadstat.read_sav(SAV, usecols=["COUNTRY", "Q32", "Q36D", "WEIGHT"])
    country_labels = meta.variable_value_labels["COUNTRY"]
    weight = df["WEIGHT"].to_numpy()
    country = df["COUNTRY"].to_numpy()
    religion = df["Q32"].to_numpy()
    charismatic = df["Q36D"].to_numpy()

    christian = religion == CHRISTIAN_CODE

    results = {}
    omitted_low_n = []
    for code, label in country_labels.items():
        country_mask = christian & (country == code)
        valid = country_mask & np.isin(charismatic, list(VALID_CODES))
        n = int(valid.sum())
        if n < MIN_VALID_N:
            if n > 0:
                omitted_low_n.append(label)
            continue
        yes = valid & (charismatic == YES)
        results[label] = {
            "pct": round(100 * weight[yes].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": n,
            "group_unweighted_n": int(country_mask.sum()),
        }

    # Rank all eligible countries, then keep only the top TOP_N.
    ranked = sorted(results, key=lambda label: -results[label]["pct"])
    kept = set(ranked[:TOP_N])
    omitted_low_rank = [label for label in ranked if label not in kept]
    results = {label: results[label] for label in kept}
    order = sorted(results, key=lambda label: -results[label]["pct"])

    valid_all = christian & np.isin(charismatic, list(VALID_CODES))
    yes_all = valid_all & (charismatic == YES)
    all_pct = round(100 * weight[yes_all].sum() / weight[valid_all].sum(), 2)

    out = {
        "source": "Pew Research Center's Forum on Religion & Public Life. "
                  "\"Tolerance and Tension: Islam and Christianity in "
                  "Sub-Saharan Africa,\" April 15, 2010. Fielded December "
                  "2008-April 2009, face-to-face, in 19 sub-Saharan African "
                  "countries.",
        "method": "Population is respondents who identify as Christian "
                  "(Q32), by country (COUNTRY). Share also describing "
                  "themselves as a \"Charismatic Christian\" (Q36D: \"Would "
                  "you describe yourself as a Charismatic Christian, or "
                  "not?\"); don't know/refused excluded from each row's "
                  "denominator. Countries under 30 valid respondents "
                  "omitted (Djibouti, n=24). Of the 18 remaining countries "
                  f"only the top {TOP_N} by value are shown; omitted for "
                  "space: " + ", ".join(omitted_low_rank) + ". Weighted by "
                  "the dataset's own WEIGHT variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "countries_omitted_low_n": omitted_low_n,
        "countries_omitted_low_rank": omitted_low_rank,
        "all_christians_pct": all_pct,
        "group_order": order,
        "charismatic_christian_share": results,
    }
    with open(
        "docs/datasets/pew-subsaharan-africa-2010/charismatic-christians.json",
        "w", encoding="utf-8",
    ) as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:35} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print(f"\nAll Christians surveyed: {all_pct:.1f}%")
    print("\nWrote docs/datasets/pew-subsaharan-africa-2010/charismatic-christians.json")


if __name__ == "__main__":
    main()

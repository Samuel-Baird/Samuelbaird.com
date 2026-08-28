"""
Flagship chart for the 2007 Pew Hispanic Center/Pew Forum "Changing Faiths"
survey of U.S. Latinos: among adults in each religious group, what share
converted to that religion rather than being raised in it (qn30, "Have you
always been your RELIGION, or did you convert from another faith or
religion that you practiced in the past?")?

This survey's own "recoded religion" variable (relig) carries an explicit
Mormon category (code 4.0, N=34 unweighted - just over this pipeline's
30-valid-respondent floor), so this chart both tells the survey's real
headline story (Latino religious switching, driven overwhelmingly by
Catholic-to-Protestant conversion) AND gives Latter-day Saints their own
row: 42.5% of Latino Mormons are converts, on par with Protestants (48.6%)
and well above Catholics (2.2%, i.e. almost no one converts INTO
Catholicism among Latinos - all switching among Catholics runs the other
direction, out of the faith).

Note the odd weighted-vs-unweighted gap for the Mormon row (unweighted
19/33 = 57.6% converts, weighted 42.5%): this survey's newweight corrects
for a deliberate oversample of 2,000 non-Catholic respondents (see
Survey Methodology.pdf), so unweighted subgroup shares should never be
read as population estimates on their own.

The base population for every row is adults *currently* in that religion
(relig), restricted to valid qn30 answers (excludes refused - 1 case among
Mormons). Groups under 30 valid respondents are omitted (drops Jehovah's
Witness's own N=104 group here? no - JW clears the floor too; only
Muslim [n=2] and Orthodox [n=3] are dropped for being far under it).

Usage: python scripts/pew-hispanics-religion-2007/latino_religious_converts.py
"""
import json

import numpy as np
import pyreadstat

SAV = (
    "data/pew-hispanics-religion-2007/"
    "Pew Hispanic Center - Pew Forum Religion Survey Data 5-1-2008.sav"
)

RELIG_CODES = {
    1.0: "Catholic",
    2.0: "Protestant",
    3.0: "Jehovah's Witness",
    4.0: "Mormon",
    5.0: "Jewish",
}
CONVERTED = 2.0
VALID_CODES = {1.0, 2.0}
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["relig", "qn30", "newweight"])
    weight = df["newweight"].to_numpy()
    relig = df["relig"].to_numpy()
    q30 = df["qn30"].to_numpy()

    results = {}
    for code, label in RELIG_CODES.items():
        group_mask = relig == code
        valid = group_mask & np.isin(q30, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        converted = valid & (q30 == CONVERTED)
        results[label] = {
            "pct": round(100 * weight[converted].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    order = sorted(results, key=lambda label: -results[label]["pct"])

    out = {
        "source": "Pew Research Center (Pew Hispanic Center and Pew Forum on Religion & "
                  "Public Life). \"Changing Faiths: Latinos and the Transformation of "
                  "American Religion,\" survey of 4,016 U.S. Hispanic adults, fielded "
                  "Aug. 10-Oct. 4, 2006.",
        "method": "Population is Hispanic adults currently belonging to each religious "
                  "group (the survey's own recoded 'relig' variable). Share answering "
                  "\"No, I converted from another religion\" (vs. \"Yes, I have always "
                  "been my RELIGION\") to qn30; refused excluded from each row's "
                  "denominator. Groups under 30 valid respondents omitted. Weighted by "
                  "the dataset's own newweight variable, which corrects for a deliberate "
                  "oversample of 2,000 non-Catholic respondents.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "converted_to_current_religion": results,
    }
    with open(
        "docs/datasets/pew-hispanics-religion-2007/latino-religious-converts.json",
        "w", encoding="utf-8",
    ) as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:18} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-hispanics-religion-2007/latino-religious-converts.json")


if __name__ == "__main__":
    main()

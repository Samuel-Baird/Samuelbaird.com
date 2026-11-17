"""
"Would you describe yourself as a born-again or evangelical Christian, or
not?" (qn25) for the 2007 Pew Hispanic Center/Pew Forum "Changing Faiths"
survey of U.S. Latinos, broken out by the survey's own recoded religion
variable (relig). Reports the share answering "Yes."

Latino Mormons embrace the "born-again" self-label at 61.9% -- 2nd only to
Protestants (83.0%) and far above Catholics (30.3%) and Jehovah's Witnesses
(25.4%). This is a striking contrast with the general U.S. population: the
already-shipped pew-rls-2014 `born-again-identity` chart found only 24.0%
of Mormons overall accept the label, near the bottom of Christian
traditions. Read together, the two charts suggest Latino Mormon converts
carry over an evangelical-style "born-again" self-identification from a
Protestant-dominated religious market much more than Mormons in the
general (largely white, multi-generational) U.S. population do.

Groups under 30 valid respondents are omitted (drops Unaffiliated, Muslim,
Orthodox, and Jewish -- Mormon clears the floor at n=32, matching the
"just over the 30-valid floor" pattern already noted for this dataset's
other charts). Weighted by the dataset's own newweight variable, which
corrects for a deliberate oversample of 2,000 non-Catholic respondents.

Usage: python scripts/pew-hispanics-religion-2007/born_again_identity.py
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
}
YES_CODE = 1.0
VALID_CODES = {1.0, 2.0}
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["relig", "qn25", "newweight"])
    weight = df["newweight"].to_numpy()
    relig = df["relig"].to_numpy()
    q = df["qn25"].to_numpy()

    results = {}
    for code, label in RELIG_CODES.items():
        group_mask = relig == code
        valid = group_mask & np.isin(q, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        yes = valid & (q == YES_CODE)
        results[label] = {
            "pct": round(100 * weight[yes].sum() / weight[valid].sum(), 2),
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
                  "\"Yes\" (vs. \"No\") to qn25, \"Would you describe yourself as a "
                  "born-again or evangelical Christian, or not?\"; don't know/refused "
                  "excluded from each row's denominator. Groups under 30 valid "
                  "respondents omitted. Weighted by the dataset's own newweight "
                  "variable, which corrects for a deliberate oversample of 2,000 "
                  "non-Catholic respondents.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "born_again": results,
    }
    with open(
        "docs/datasets/pew-hispanics-religion-2007/born-again-identity.json",
        "w", encoding="utf-8",
    ) as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:18} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-hispanics-religion-2007/born-again-identity.json")


if __name__ == "__main__":
    main()

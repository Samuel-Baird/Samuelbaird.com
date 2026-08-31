"""
Second flagship-style chart set for the 2015 Survey of U.S. Catholics and
Family Life: qb12a-e asked all respondents (not Catholics only) their
opinion of five household types children are raised in today - divorced
parents, a gay or lesbian couple, a single parent, unmarried cohabiting
parents, and a married mother and father. Each item collapses to "top box"
(acceptable and as good as any other arrangement) vs. everything else,
broken out by present religion (relig) - a general-public sample with a
Catholic oversample, not restricted to Catholics, unlike
annulment_communion.py in this folder.

Small-N groups (Unitarian, Jehovah's Witness, Hindu, Buddhist) drop below
the 30-valid-respondent floor and are omitted, same convention as every
other knowledge/opinion batch in this pipeline. Mormon N is thin (88
total, ~85 valid per item) but clears the floor - flagged in the method
note rather than silently treated as precise.

Hook: Family Proclamation anniversary, Sep 23 2026 - direct hit on "what
kind of household should children be raised in," the Proclamation's own
subject.

Usage: python scripts/pew-catholic-family-2015/household_types.py
"""
import json

import numpy as np
import pyreadstat

SAV = (
    "data/pew-catholic-family-2015/Dataset - Pew Research Center 2015 Survey "
    "of U.S. Catholics and Family Life - Version 1.1 - Mar 1, 2018.sav"
)

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
    11.0: "Something else",
    12.0: "Nothing in particular",
    13.0: "Christian (unspecified)",
    15.0: "Jehovah's Witness",
}
MIN_VALID_N = 30
TOP_BOX = 1.0  # "Acceptable and as good as any other arrangement"
VALID_CODES = {1.0, 2.0, 3.0}  # excludes volunteered "depends"/"best" and DK/refused


def top_box_by_group(col, weight, relig):
    results = {}
    for code, label in RELIG_CODES.items():
        group_mask = relig == code
        valid = group_mask & np.isin(col, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        hit = valid & (col == TOP_BOX)
        results[label] = {
            "pct": round(100 * weight[hit].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }
    valid_all = np.isin(col, list(VALID_CODES))
    hit_all = valid_all & (col == TOP_BOX)
    results["U.S. adults"] = {
        "pct": round(100 * weight[hit_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(col)),
    }
    return results


def main():
    cols = ["relig", "qb12a", "qb12b", "qb12c", "qb12d", "qb12e", "weight"]
    df, _ = pyreadstat.read_sav(SAV, usecols=cols)
    weight = df["weight"].to_numpy()
    relig = df["relig"].to_numpy()

    divorced_parents = top_box_by_group(df["qb12a"].to_numpy(), weight, relig)
    gay_lesbian_couple = top_box_by_group(df["qb12b"].to_numpy(), weight, relig)
    single_parent = top_box_by_group(df["qb12c"].to_numpy(), weight, relig)
    cohabiting_unmarried = top_box_by_group(df["qb12d"].to_numpy(), weight, relig)
    married_mother_father = top_box_by_group(df["qb12e"].to_numpy(), weight, relig)

    out = {
        "source": "Pew Research Center. 2015 Survey of U.S. Catholics and Family Life, "
                  "fielded May 5-June 7, 2015.",
        "method": "Population is all respondents (a general-public sample with a Catholic "
                  "oversample), grouped by present religion (relig). Each item's own "
                  "'depends'/'this is the best arrangement' (volunteered) and don't "
                  "know/refused excluded from its own denominator; share is top box "
                  "('acceptable and as good as any other arrangement') vs. 'acceptable "
                  "but not as good' or 'not an acceptable arrangement.' Groups under 30 "
                  "valid respondents omitted - Mormon N is thin (88 total respondents, "
                  "~85 valid per item) and should be read directionally. Weighted by the "
                  "dataset's own weight variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "raised_by_divorced_parents": divorced_parents,
        "raised_by_gay_lesbian_couple": gay_lesbian_couple,
        "raised_by_single_parent": single_parent,
        "raised_by_cohabiting_unmarried_parents": cohabiting_unmarried,
        "raised_by_married_mother_father": married_mother_father,
    }
    with open(
        "docs/datasets/pew-catholic-family-2015/household-types.json", "w", encoding="utf-8"
    ) as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("Wrote docs/datasets/pew-catholic-family-2015/household-types.json")


if __name__ == "__main__":
    main()

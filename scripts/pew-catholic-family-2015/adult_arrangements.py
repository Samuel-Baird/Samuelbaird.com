"""
Third flagship-style chart set for the 2015 Survey of U.S. Catholics and
Family Life: qb15a-c asked all respondents (not Catholics only) their
opinion of three living arrangements among ADULTS - an unmarried man and
woman living together, a same-sex couple living together, and a husband
and wife who choose not to have children. Same top-box collapse and same
present-religion (relig) breakout as household_types.py's qb12 battery in
this folder, just the adult-arrangements half of the same B-section
sequence (qb12 asks about children being raised in these arrangements;
qb15 asks about the arrangements themselves for adults).

Small-N groups (Unitarian, Jehovah's Witness, Hindu, Buddhist) drop below
the 30-valid-respondent floor and are omitted, same convention as
household_types.py. Mormon N is thin (88 total, ~86 valid per item) but
clears the floor - flagged in the method note rather than silently
treated as precise.

Hook: same Family Proclamation angle as household_types.py - these three
items are the flip side of "what kind of household should children be
raised in," asking instead what adult living arrangements the public
accepts. qb15b (a same-sex couple living together) is a distinct
construct from the site's existing "favor same-sex marriage" charts
(pew-rls-2014, CCES 2016, pew-latin-america-2014) - this asks about
acceptability of a way of life, not support for legal marriage.

Usage: python scripts/pew-catholic-family-2015/adult_arrangements.py
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
TOP_BOX = 1.0  # "Acceptable and as good as any other way of life"
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
    cols = ["relig", "qb15a", "qb15b", "qb15c", "weight"]
    df, _ = pyreadstat.read_sav(SAV, usecols=cols)
    weight = df["weight"].to_numpy()
    relig = df["relig"].to_numpy()

    unmarried_cohabiting_couple = top_box_by_group(df["qb15a"].to_numpy(), weight, relig)
    samesex_couple_living_together = top_box_by_group(df["qb15b"].to_numpy(), weight, relig)
    childless_by_choice = top_box_by_group(df["qb15c"].to_numpy(), weight, relig)

    out = {
        "source": "Pew Research Center. 2015 Survey of U.S. Catholics and Family Life, "
                  "fielded May 5-June 7, 2015.",
        "method": "Population is all respondents (a general-public sample with a Catholic "
                  "oversample), grouped by present religion (relig). Each item's own "
                  "'depends'/'this way of life is the best' (volunteered) and don't "
                  "know/refused excluded from its own denominator; share is top box "
                  "('acceptable and as good as any other way of life') vs. 'acceptable "
                  "but not as good' or 'not an acceptable way of life.' Groups under 30 "
                  "valid respondents omitted - Mormon N is thin (88 total respondents, "
                  "~86 valid per item) and should be read directionally. Weighted by the "
                  "dataset's own weight variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "unmarried_cohabiting_couple": unmarried_cohabiting_couple,
        "samesex_couple_living_together": samesex_couple_living_together,
        "childless_by_choice": childless_by_choice,
    }
    with open(
        "docs/datasets/pew-catholic-family-2015/adult-arrangements.json", "w", encoding="utf-8"
    ) as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("Wrote docs/datasets/pew-catholic-family-2015/adult-arrangements.json")


if __name__ == "__main__":
    main()

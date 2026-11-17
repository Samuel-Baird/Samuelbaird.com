"""
Fourth chart for the 2015 Survey of U.S. Catholics and Family Life: qf6,
"When you pray, do you mainly say prayers that you have memorized ... or do
you mainly have a personal conversation with God?" Asked of the general
public (not Catholics only), broken out by present religion (relig) - same
sample and grouping convention as adult_arrangements.py/household_types.py
in this folder.

Hook: LDS teaching holds that personal prayer is meant to be an informal,
individual conversation with Heavenly Father in one's own words (see, e.g.,
"The Lord's Pattern of Prayer") rather than reciting fixed/memorized
liturgical prayers - the Church has no set congregational prayer text
outside the sacrament prayers, which are themselves scripted verbatim
precisely because they're the exception. qf6 tests that distinctive
directly: 89.8% of Mormons say they mainly have a personal conversation
with God rather than mainly saying memorized prayers, 2nd only to
Jehovah's Witness (96.1%, thinner n=31) among named traditions, and well
above Protestant (83.6%) and far above Catholic (45.9%) - Catholic and
Orthodox liturgical prayer traditions anchor the low end as expected.
Mormon n=87 (unweighted valid), comfortably above the 30-floor.

Denominator excludes only "don't know/refused" (qf6==9); the volunteered
"other/neither" and "both" responses are kept in the denominator (same
treatment as adult_arrangements.py's VALID_CODES pattern) since they're
substantive answers, just not the literal top-box. Top box is qf6==2,
"mainly personal conversation with God."

Note: qf6 has a large skip-gate (683 of 5,122 respondents have no valid
code at all, likely never-prayer/does-not-pray-outside-services
respondents from qf5's skip logic) - "total_weighted_n"/"total_unweighted_n"
below describe the full survey, not the qf6-eligible subsample; each
group's own valid_unweighted_n is the number that actually answered qf6.

Usage: python scripts/pew-catholic-family-2015/prayer_style.py
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
TOP_BOX = 2.0  # "mainly have a personal conversation with God"
VALID_CODES = {1.0, 2.0, 3.0, 4.0}  # excludes only don't know/refused (9)


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
    cols = ["relig", "qf6", "weight"]
    df, _ = pyreadstat.read_sav(SAV, usecols=cols)
    weight = df["weight"].to_numpy()
    relig = df["relig"].to_numpy()

    personal_conversation_prayer = top_box_by_group(df["qf6"].to_numpy(), weight, relig)

    out = {
        "source": "Pew Research Center. 2015 Survey of U.S. Catholics and Family Life, "
                  "fielded May 5-June 7, 2015.",
        "method": "Population is all respondents (a general-public sample with a Catholic "
                  "oversample), grouped by present religion (relig). qf6 asks how "
                  "respondents mainly pray: memorized prayers, a personal conversation "
                  "with God, both (volunteered), or other/neither (volunteered) - only "
                  "don't know/refused is excluded from the denominator. Share is top box "
                  "('mainly have a personal conversation with God'). Groups under 30 "
                  "valid respondents omitted - Mormon N is thin (87 valid respondents) "
                  "and should be read directionally. Weighted by the dataset's own weight "
                  "variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "personal_conversation_prayer": personal_conversation_prayer,
    }
    with open(
        "docs/datasets/pew-catholic-family-2015/prayer-style.json", "w", encoding="utf-8"
    ) as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("Wrote docs/datasets/pew-catholic-family-2015/prayer-style.json")


if __name__ == "__main__":
    main()

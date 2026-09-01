"""
Fifth chart for pew-black-faith-2021 (Pew's "Faith Among Black Americans,"
published Feb. 16, 2021): among Black American adults imagining they were
looking for a new congregation or house of worship, how important is it
that the congregation belongs to their own denomination (CHURCHLOOK_c),
broken out by present religious affiliation (RELIGMOD)?

RELIGMOD code 3.0 ("Mormon/Church of Jesus Christ of Latter-day Saints") has
an unweighted N of 33 valid respondents on CHURCHLOOK_c among Black
respondents in "black faith black respondents.sav" - just over this repo's
30-valid-respondent floor.

This is a genuine LDS-doctrine-vs-data comparison: The Church of Jesus
Christ of Latter-day Saints teaches a restorationist, exclusive-authority
claim (it holds itself to be the sole church carrying priesthood authority
and Christ's full, restored gospel, not one interchangeable option among
many denominations), so a stated preference for staying within one's own
denomination when picking a new congregation should read as a distinctly
LDS-flavored answer relative to other named traditions in this
Black-American-specific sample - and the data bears this out: Mormons rate
"belongs to your denomination" as very important at nearly 1.5x the rate
of Protestants and Catholics, 2nd only to Jehovah's Witnesses (whose own
publications teach a similarly exclusive one-true-organization claim).

Checked the battery's four sibling items (CHURCHLOOK_a "welcoming,"
CHURCHLOOK_b "inspiring sermons," CHURCHLOOK_d/e "shares your race or
ethnicity") for a comparable story: a/b show Mormons mid-pack with no
distinctive story, and d/e are race-of-clergy/congregation items with the
same Black-church-specific racial framing already flagged as a weak LDS
fit for this dataset's COMMINFL1/BLKEQL1_c items in
docs/datasets/EXPLORATION_LOG.md - not used here.

Uses the "black faith black respondents.sav" file (not the "all
respondents" file, which adds a non-Black comparison sample) since every
row in this chart is a subgroup of Black Americans specifically, matching
this dataset's existing women-leaders.json/convert-duty.json/
god-responds.json/turned-to-church-for-help.json charts. Weighted by the
dataset's own WEIGHT variable (the codebook's recommended weight when
analyzing only Black respondents from this file).

Usage: python scripts/pew-black-faith-2021/denomination_loyalty.py
"""
import json

import numpy as np
import pyreadstat

SAV = "data/pew-black-faith-2021/black faith black respondents.sav"

RELIGMOD_CODES = {
    1.0: "Protestant",
    2.0: "Catholic",
    3.0: "Mormon",
    4.0: "Jehovah's Witness",
    6.0: "Muslim",
}
# "Nothing in particular," "Atheist," and "Agnostic" combined into one
# religiously-unaffiliated row - same combination convention used in this
# folder's women_leaders.py/convert_duty.py/god_responds.py.
UNAFFILIATED_CODES = {9.0, 10.0, 12.0}
VERY_IMPORTANT = 1.0
VALID_CODES = {1.0, 2.0, 3.0, 4.0}
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["RELIGMOD", "CHURCHLOOK_c", "WEIGHT"])
    weight = df["WEIGHT"].to_numpy()
    relig = df["RELIGMOD"].to_numpy()
    item = df["CHURCHLOOK_c"].to_numpy()

    def row(mask, label, results):
        valid = mask & np.isin(item, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            return
        very = valid & (item == VERY_IMPORTANT)
        results[label] = {
            "pct": round(100 * weight[very].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(mask.sum()),
        }

    results = {}
    for code, label in RELIGMOD_CODES.items():
        row(relig == code, label, results)
    row(np.isin(relig, list(UNAFFILIATED_CODES)), "Religiously unaffiliated", results)

    valid_all = np.isin(item, list(VALID_CODES))
    very_all = valid_all & (item == VERY_IMPORTANT)
    results["All Black Americans"] = {
        "pct": round(100 * weight[very_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }

    order = [label for label in results if label != "All Black Americans"]
    order.sort(key=lambda label: -results[label]["pct"])
    order.append("All Black Americans")

    out = {
        "source": "Pew Research Center. \"Faith Among Black Americans,\" published Feb. 16, "
                  "2021 (survey fielded Nov. 19, 2019-June 3, 2020).",
        "method": "Population is Black American adults (\"black faith black respondents.sav\"), "
                  "grouped by self-reported present religion (RELIGMOD): named affiliations "
                  "shown individually; Atheist, Agnostic, and Nothing in particular combined "
                  "into \"Religiously unaffiliated.\" Share saying it would be \"very important\" "
                  "that a new congregation \"belongs to your denomination\" if they were looking "
                  "for one (CHURCHLOOK_c); not-answered excluded from each row's denominator. "
                  "Groups under 30 valid respondents omitted. Weighted by the dataset's own "
                  "WEIGHT variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "denomination_very_important": results,
    }
    with open(
        "docs/datasets/pew-black-faith-2021/denomination-loyalty.json", "w", encoding="utf-8"
    ) as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:26} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-black-faith-2021/denomination-loyalty.json")


if __name__ == "__main__":
    main()

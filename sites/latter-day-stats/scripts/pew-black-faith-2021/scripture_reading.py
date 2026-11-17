"""
Seventh chart for pew-black-faith-2021 (Pew's "Faith Among Black Americans,"
published Feb. 16, 2021): how often, if at all, do Black American adults
personally read scripture outside of religious services (PERSDO1_b),
broken out by present religious affiliation (RELIGMOD)?

RELIGMOD code 3.0 ("Mormon/Church of Jesus Christ of Latter-day Saints") has
an unweighted N of 33 valid respondents on PERSDO1_b among Black respondents
in "black faith black respondents.sav" - just over this repo's 30-valid-
respondent floor.

This is a genuine LDS-practice-vs-data comparison: personal and family
scripture study is a core, frequently-taught Latter-day Saint practice (daily
personal/family scripture study, Come Follow Me home study), so a high share
reading scripture at least weekly outside of religious services should read
as a distinctly LDS-flavored result relative to other named traditions in
this Black-American-specific sample - and the data bears this out: Black
Mormons read scripture outside of services at least weekly at the highest
rate of any tradition in the wave (69.9%), edging out Jehovah's Witnesses
(68.8%) and well above Protestants (51.8%) and Catholics (30.3%).

Checked the battery's four sibling items (PERSDO1_a "meditate," PERSDO1_c
"burn candles/incense/sage," PERSDO1_d "pray at a home altar/shrine,"
PERSDO1_e "consult a diviner/reader") in a prior pass per
docs/datasets/EXPLORATION_LOG.md - all four either land Mormons mid-pack
with no distinctive story or show a counter-doctrinal result on thin N; not
re-used here. This item (PERSDO1_b) was the one sibling in that same battery
not yet checked.

Uses the "black faith black respondents.sav" file (not the "all
respondents" file, which adds a non-Black comparison sample) since every
row in this chart is a subgroup of Black Americans specifically, matching
this dataset's existing women-leaders.json/convert-duty.json/
god-responds.json/turned-to-church-for-help.json/denomination-loyalty.json/
job-skills-essential.json charts. Weighted by the dataset's own WEIGHT
variable (the codebook's recommended weight when analyzing only Black
respondents from this file).

Usage: python scripts/pew-black-faith-2021/scripture_reading.py
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
# religiously-unaffiliated row - same combination convention used
# elsewhere in this folder.
UNAFFILIATED_CODES = {9.0, 10.0, 12.0}
# PERSDO1_b codes: 1 several times a day, 2 once a day, 3 a few times a
# week, 4 once a week, 5 a few times a month, 6 seldom, 7 never.
WEEKLY_PLUS_CODES = {1.0, 2.0, 3.0, 4.0}
VALID_CODES = {1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0}
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["RELIGMOD", "PERSDO1_b", "WEIGHT"])
    weight = df["WEIGHT"].to_numpy()
    relig = df["RELIGMOD"].to_numpy()
    item = df["PERSDO1_b"].to_numpy()

    def row(mask, label, results):
        valid = mask & np.isin(item, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            return
        weekly = valid & np.isin(item, list(WEEKLY_PLUS_CODES))
        results[label] = {
            "pct": round(100 * weight[weekly].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(mask.sum()),
        }

    results = {}
    for code, label in RELIGMOD_CODES.items():
        row(relig == code, label, results)
    row(np.isin(relig, list(UNAFFILIATED_CODES)), "Religiously unaffiliated", results)

    valid_all = np.isin(item, list(VALID_CODES))
    weekly_all = valid_all & np.isin(item, list(WEEKLY_PLUS_CODES))
    results["All Black Americans"] = {
        "pct": round(100 * weight[weekly_all].sum() / weight[valid_all].sum(), 2),
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
                  "into \"Religiously unaffiliated.\" Share who read scripture outside of "
                  "religious services at least once a week (PERSDO1_b); not-answered excluded "
                  "from each row's denominator. Groups under 30 valid respondents omitted. "
                  "Weighted by the dataset's own WEIGHT variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "reads_scripture_weekly": results,
    }
    with open(
        "docs/datasets/pew-black-faith-2021/scripture-reading.json", "w", encoding="utf-8"
    ) as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:26} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-black-faith-2021/scripture-reading.json")


if __name__ == "__main__":
    main()

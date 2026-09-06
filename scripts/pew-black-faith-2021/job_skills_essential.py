"""
Sixth chart for pew-black-faith-2021 (Pew's "Faith Among Black Americans,"
published Feb. 16, 2021): among Black American adults, how important is it
for churches and other houses of worship to "teach practical job and life
skills" (ESSENTCHURCH_c), broken out by present religious affiliation
(RELIGMOD)?

RELIGMOD code 3.0 ("Mormon/Church of Jesus Christ of Latter-day Saints") has
an unweighted N of 33 valid respondents on ESSENTCHURCH_c among Black
respondents in "black faith black respondents.sav" - just over this repo's
30-valid-respondent floor.

This is a genuine LDS-doctrine-vs-data comparison: The Church of Jesus
Christ of Latter-day Saints places unusual institutional emphasis on
practical self-reliance and vocational/educational training as a religious
function of the congregation itself - not just spiritual instruction - via
programs like the Church's Self-Reliance Initiative (career workshops,
employment resource centers, budgeting/education courses run through wards
and stakes), the Perpetual Education Fund, and BYU-Pathway Worldwide. So a
belief that houses of worship should teach practical job/life skills, not
just moral or spiritual instruction, should read as a distinctly
LDS-flavored answer relative to other named traditions in this
Black-American-specific sample - and the data bears this out: Mormons rate
this "essential" at 70.5%, the highest of any group by a wide margin (next
closest is Muslim at 50.9%, with Protestant at 47.6% and every other group
under 45%).

Checked the battery's other sibling items for a comparable story:
ESSENTCHURCH_a (moral guidance, Mormon 60.9% - mid-pack, well below
Protestant's 74.2% and Jehovah's Witness's 80.2%), ESSENTCHURCH_d (help the
needy with bills/housing/food, Mormon 53.7% - mid-pack, no highest/lowest
story and thematically close to this dataset's already-shipped
turned-to-church-for-help.json), ESSENTCHURCH_e (sense of community/
fellowship, Mormon 64.9% - mid-pack, below Protestant's 78.2%), and
ESSENTCHURCH_f/g (racial affirmation / political sermons - Black-church-
specific racial/political framing, same weak-LDS-fit concern already
flagged for this dataset's COMMINFL1/BLKEQL1_c/CHURCHLOOK_d/e items in
docs/datasets/EXPLORATION_LOG.md) - none used here. ESSENTCHURCH_c alone
has the clean distinctiveness story.

Uses the "black faith black respondents.sav" file (not the "all
respondents" file, which adds a non-Black comparison sample) since every
row in this chart is a subgroup of Black Americans specifically, matching
this dataset's existing women-leaders.json/convert-duty.json/
god-responds.json/turned-to-church-for-help.json/denomination-loyalty.json
charts. Weighted by the dataset's own WEIGHT variable (the codebook's
recommended weight when analyzing only Black respondents from this file).

Usage: python scripts/pew-black-faith-2021/job_skills_essential.py
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
# throughout this folder's scripts.
UNAFFILIATED_CODES = {9.0, 10.0, 12.0}
ESSENTIAL = 1.0
VALID_CODES = {1.0, 2.0, 3.0, 4.0}
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["RELIGMOD", "ESSENTCHURCH_c", "WEIGHT"])
    weight = df["WEIGHT"].to_numpy()
    relig = df["RELIGMOD"].to_numpy()
    item = df["ESSENTCHURCH_c"].to_numpy()

    def row(mask, label, results):
        valid = mask & np.isin(item, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            return
        essential = valid & (item == ESSENTIAL)
        results[label] = {
            "pct": round(100 * weight[essential].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(mask.sum()),
        }

    results = {}
    for code, label in RELIGMOD_CODES.items():
        row(relig == code, label, results)
    row(np.isin(relig, list(UNAFFILIATED_CODES)), "Religiously unaffiliated", results)

    valid_all = np.isin(item, list(VALID_CODES))
    essential_all = valid_all & (item == ESSENTIAL)
    results["All Black Americans"] = {
        "pct": round(100 * weight[essential_all].sum() / weight[valid_all].sum(), 2),
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
                  "into \"Religiously unaffiliated.\" Share saying it is \"essential\" for "
                  "churches and other houses of worship to \"teach practical job and life "
                  "skills\" (ESSENTCHURCH_c); not-answered excluded from each row's "
                  "denominator. Groups under 30 valid respondents omitted. Weighted by the "
                  "dataset's own WEIGHT variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "job_skills_essential": results,
    }
    with open(
        "docs/datasets/pew-black-faith-2021/job-skills-essential.json", "w", encoding="utf-8"
    ) as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:26} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-black-faith-2021/job-skills-essential.json")


if __name__ == "__main__":
    main()

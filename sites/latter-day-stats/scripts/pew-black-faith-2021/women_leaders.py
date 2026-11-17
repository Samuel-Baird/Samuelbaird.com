"""
Flagship chart for the newly-registered pew-black-faith-2021 dataset (Pew's
"Faith Among Black Americans" report, published Feb. 16, 2021): among Black
American adults, how does support for women serving as a congregation's
senior religious leader (WOMLEAD) vary by religious affiliation (RELIGMOD)?

This dataset's RELIGMOD is a simple self-reported "present religion"
variable, not Pew's F_RELTRAD religious-tradition frame used elsewhere in
this repo's pew-atp-w70-2020 scripts, so it has its own flat set of category
codes (see the codebook) rather than F_RELTRAD's numeric-tier scheme.
RELIGMOD code 3.0 ("Mormon/Church of Jesus Christ of Latter-day Saints")
has an unweighted N of 34 among Black respondents in "black faith black
respondents.sav" - just over this repo's 30-valid-respondent floor, and
confirmed to have zero missingness on WOMLEAD (34 valid of 34 group
members), so it clears MIN_VALID_N on the actual analysis variable too, not
just the raw group count.

WOMLEAD was picked over several other candidate items (ESSENT_a/b/c,
CLERGYSSM, RELIMP, PERSBLV_e - see this folder's exploration) because it is
the one where Black Latter-day Saints read as genuinely distinct from Black
Protestants, Catholics, and the religiously unaffiliated: LDS polity
reserves formal congregational leadership (bishop, stake president, etc.)
for ordained men, unlike the denominations being compared against here, and
the survey response mirrors that - a double-digit-point gap from the other
named-affiliation groups, not a wash. Jehovah's Witnesses are included as
useful comparative context (a religious tradition with an even more
restrictive stance on the same question, and the JW group's own polity
reserves congregation leadership for men only, similar in kind to LDS
polity - see the codebook), not because the chart is about them.

Uses the "black faith black respondents.sav" file (not the "all
respondents" file, which adds a non-Black comparison sample) since every row
in this chart is a subgroup of Black Americans specifically. Weighted by the
dataset's own WEIGHT variable (see the codebook's note that WEIGHT, not
MAINWEIGHT, is the weight to use when analyzing only Black respondents from
this file).

Usage: python scripts/pew-black-faith-2021/women_leaders.py
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
# religiously-unaffiliated row - same combination convention used elsewhere
# in this repo (see chart_style.py's GROUP_COLORS "Religiously unaffiliated"
# entry) rather than three separate small rows for what is, substantively,
# one population.
UNAFFILIATED_CODES = {9.0, 10.0, 12.0}
YES = 1.0
VALID_CODES = {1.0, 2.0}
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["RELIGMOD", "WOMLEAD", "WEIGHT"])
    weight = df["WEIGHT"].to_numpy()
    relig = df["RELIGMOD"].to_numpy()
    womlead = df["WOMLEAD"].to_numpy()

    def row(mask, label, results):
        valid = mask & np.isin(womlead, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            return
        yes = valid & (womlead == YES)
        results[label] = {
            "pct": round(100 * weight[yes].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(mask.sum()),
        }

    results = {}
    for code, label in RELIGMOD_CODES.items():
        row(relig == code, label, results)
    row(np.isin(relig, list(UNAFFILIATED_CODES)), "Religiously unaffiliated", results)

    valid_all = np.isin(womlead, list(VALID_CODES))
    yes_all = valid_all & (womlead == YES)
    results["All Black Americans"] = {
        "pct": round(100 * weight[yes_all].sum() / weight[valid_all].sum(), 2),
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
                  "into \"Religiously unaffiliated.\" Share answering \"yes\" to WOMLEAD (\"Do "
                  "you think women should be allowed to serve as the senior religious leader "
                  "of a congregation?\"); not-answered excluded from each row's denominator. "
                  "Groups under 30 valid respondents omitted. Weighted by the dataset's own "
                  "WEIGHT variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "women_should_lead": results,
    }
    with open("docs/datasets/pew-black-faith-2021/women-leaders.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:26} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-black-faith-2021/women-leaders.json")


if __name__ == "__main__":
    main()

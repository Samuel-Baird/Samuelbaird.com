"""
Third flagship chart for pew-black-faith-2021 (Pew's "Faith Among Black
Americans," published Feb. 16, 2021): among Black American adults, how does
the share saying God ever talks directly with them (GODRESPONDMOD) vary by
religious affiliation (RELIGMOD)?

RELIGMOD code 3.0 ("Mormon/Church of Jesus Christ of Latter-day Saints") has
an unweighted N of 34 among Black respondents in "black faith black
respondents.sav" - just over this repo's 30-valid-respondent floor, and 33
of those 34 answer GODRESPONDMOD validly (1 not-answered), clearing
MIN_VALID_N on the analysis variable too, not just the raw group count.

GODRESPONDMOD is a genuine LDS-distinctiveness item: personal revelation -
the belief that God communicates directly with individuals, not only
through scripture or clergy - is a core, frequently taught LDS doctrine
(see Doctrine and Covenants 8-9 on revelation "in your mind and in your
heart"), so this reads as a defensible doctrine-vs-data comparison, not a
coincidental correlation.

Uses the "black faith black respondents.sav" file (not the "all
respondents" file, which adds a non-Black comparison sample) since every row
in this chart is a subgroup of Black Americans specifically, matching this
dataset's existing women-leaders.json and convert-duty.json charts.
Weighted by the dataset's own WEIGHT variable (the codebook's recommended
weight when analyzing only Black respondents from this file).

Usage: python scripts/pew-black-faith-2021/god_responds.py
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
UNAFFILIATED_CODES = {9.0, 10.0, 12.0}
YES = 1.0
VALID_CODES = {1.0, 2.0}
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["RELIGMOD", "GODRESPONDMOD", "WEIGHT"])
    weight = df["WEIGHT"].to_numpy()
    relig = df["RELIGMOD"].to_numpy()
    item = df["GODRESPONDMOD"].to_numpy()

    def row(mask, label, results):
        valid = mask & np.isin(item, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            return
        yes = valid & (item == YES)
        results[label] = {
            "pct": round(100 * weight[yes].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(mask.sum()),
        }

    results = {}
    for code, label in RELIGMOD_CODES.items():
        row(relig == code, label, results)
    row(np.isin(relig, list(UNAFFILIATED_CODES)), "Religiously unaffiliated", results)

    valid_all = np.isin(item, list(VALID_CODES))
    yes_all = valid_all & (item == YES)
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
                  "into \"Religiously unaffiliated.\" Share answering \"Yes\" to GODRESPONDMOD "
                  "(\"Does God ever talk directly with you, or not?\"); not-answered excluded "
                  "from each row's denominator. Groups under 30 valid respondents omitted. "
                  "Weighted by the dataset's own WEIGHT variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "god_talks_directly": results,
    }
    with open("docs/datasets/pew-black-faith-2021/god-responds.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:26} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-black-faith-2021/god-responds.json")


if __name__ == "__main__":
    main()

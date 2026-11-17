"""
Flagship chart for ATP Wave 114 (September 2022): do Americans think the
U.S. should be a "Christian nation"? NATCHRc_W114 ("Do you think the United
States should be a Christian nation?") is the item behind Pew's October 27,
2022 report "45% of Americans Say U.S. Should Be a 'Christian Nation'"
(https://www.pewresearch.org/religion/2022/10/27/45-of-americans-say-u-s-should-be-a-christian-nation/).
NATCHRc was only asked of a random half of the sample (Pew's own form
split - the other half saw a different item in the NATCHR series), so its
valid N (~5,174) is about half the wave's total 10,588.

Unlike Wave 70 (pew-atp-w70-2020), Wave 114 does NOT carry an F_RELTRAD
frame variable - confirmed against this wave's own .sav, which has no
column named F_RELTRAD at all. The closest available religious-affiliation
variable is F_RELIG (self-reported affiliation, 12 categories incl.
"Mormon (Church of Jesus Christ of Latter-day Saints or LDS)" coded 3.0),
not the finer Evangelical/Mainline/Historically-Black-Protestant/etc. frame
used in ATP waves that do carry F_RELTRAD. So this chart breaks out by
F_RELIG instead. Groups under 30 valid (non-refused) respondents are
dropped, per this repo's standing convention.

Usage: python scripts/pew-atp-w114-2022/christian_nation.py
"""
import json

import numpy as np
import pyreadstat

SAV = "data/pew-atp-w114-2022/ATP W114.sav"

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
    11.0: "Other",
    12.0: "Nothing in particular",
}
YES = 1.0
VALID_CODES = {1.0, 2.0}
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["F_RELIG", "NATCHRc_W114", "WEIGHT_W114"])
    weight = df["WEIGHT_W114"].to_numpy()
    relig = df["F_RELIG"].to_numpy()
    should = df["NATCHRc_W114"].to_numpy()

    results = {}
    for code, label in RELIG_CODES.items():
        group_mask = relig == code
        valid = group_mask & np.isin(should, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        yes = valid & (should == YES)
        results[label] = {
            "pct": round(100 * weight[yes].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(should, list(VALID_CODES))
    yes_all = valid_all & (should == YES)
    results["All U.S. adults"] = {
        "pct": round(100 * weight[yes_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }

    order = [label for label in results if label != "All U.S. adults"]
    order.sort(key=lambda label: -results[label]["pct"])
    order.append("All U.S. adults")

    out = {
        "source": "Pew Research Center. American Trends Panel Wave 114, fielded September "
                  "13-18, 2022. Underlies \"45% of Americans Say U.S. Should Be a 'Christian "
                  "Nation'\" (Pew Research Center, October 27, 2022).",
        "method": "Population is respondent's self-reported religious affiliation (F_RELIG) - "
                  "Wave 114 does not carry the finer F_RELTRAD frame variable used in other "
                  "ATP waves in this dataset family. Share answering \"yes\" to NATCHRc_W114 "
                  "(\"Do you think the United States should be a Christian nation?\"); refused "
                  "excluded from each row's denominator. NATCHRc was asked of a random half of "
                  "the sample only (Pew's own form split), so valid Ns are roughly half of each "
                  "group's total. Groups under 30 valid respondents omitted. Weighted by the "
                  "dataset's own WEIGHT_W114 variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "should_be_christian_nation": results,
    }
    with open("docs/datasets/pew-atp-w114-2022/christian-nation.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:26} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-atp-w114-2022/christian-nation.json")


if __name__ == "__main__":
    main()

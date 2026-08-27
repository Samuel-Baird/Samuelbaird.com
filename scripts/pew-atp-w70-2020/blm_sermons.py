"""
Fifth flagship chart for ATP Wave 70 (July 2020): who heard sermons
expressing support for the Black Lives Matter protests (SERMONISSUE_b_W70),
by religious tradition (F_RELTRAD)? Fielded weeks after the George Floyd
protests began, so this captures a specific summer-2020 moment, not a
standing measure. Companion to online_worship_covid.py in this folder -
same population and threshold conventions (groups under 30 valid
respondents dropped). Unlike most items in this folder, SERMONISSUE was
only asked of respondents who attend religious services at least monthly
(XATTEND_W70's own gate - confirmed against the raw missingness pattern,
not just the questionnaire text) - so this chart's population is
attenders, not all U.S. adults, and its unweighted N is much smaller than
the wave's 10,211 total.

Usage: python scripts/pew-atp-w70-2020/blm_sermons.py
"""
import json

import numpy as np
import pyreadstat

SAV = "data/pew-atp-w70-2020/ATP W70.sav"

RELTRAD_CODES = {
    1100.0: "Evangelical Protestant",
    1200.0: "Mainline Protestant",
    1300.0: "Historically Black Protestant",
    10000.0: "Catholic",
    20000.0: "Mormon",
    50000.0: "Jewish",
    100000.0: "Unaffiliated",
}
YES = 1.0
VALID_CODES = {1.0, 2.0}
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["F_RELTRAD", "SERMONISSUE_b_W70", "WEIGHT_W70"])
    weight = df["WEIGHT_W70"].to_numpy()
    reltrad = df["F_RELTRAD"].to_numpy()
    heard = df["SERMONISSUE_b_W70"].to_numpy()

    results = {}
    for code, label in RELTRAD_CODES.items():
        group_mask = reltrad == code
        valid = group_mask & np.isin(heard, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        yes = valid & (heard == YES)
        results[label] = {
            "pct": round(100 * weight[yes].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(heard, list(VALID_CODES))
    yes_all = valid_all & (heard == YES)
    results["All attenders"] = {
        "pct": round(100 * weight[yes_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }

    order = [label for label in results if label != "All attenders"]
    order.sort(key=lambda label: -results[label]["pct"])
    order.append("All attenders")

    out = {
        "source": "Pew Research Center. American Trends Panel Wave 70, fielded July 13-19, 2020.",
        "method": "Population is respondent's religious tradition (F_RELTRAD), restricted "
                  "to respondents who attend religious services at least monthly (the "
                  "survey's own SERMONISSUE skip pattern, gated on XATTEND_W70). Share "
                  "answering \"yes\" to SERMONISSUE_b_W70 (\"in the past few months have "
                  "you heard any sermons in person, online, or on TV expressing support "
                  "for the recent Black Lives Matter protests\"); refused excluded from "
                  "each row's denominator. Groups under 30 valid respondents omitted. "
                  "Weighted by the dataset's own WEIGHT_W70 variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "heard_blm_support_sermon": results,
    }
    with open("docs/datasets/pew-atp-w70-2020/blm-sermons.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:26} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-atp-w70-2020/blm-sermons.json")


if __name__ == "__main__":
    main()

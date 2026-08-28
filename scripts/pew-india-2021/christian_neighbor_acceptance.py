"""
Flagship chart for Pew's 2019-2020 India Religion Survey (2021 report
"Religion in India: Tolerance and Segregation"): are Indians of other faiths
willing to accept a Christian as a neighbor (Q63c)?

Q63c is only asked of respondents who are NOT themselves Christian - the
questionnaire skips a respondent's own religion in the Q63 neighbor-
acceptance battery (confirmed against the raw missingness pattern: Q63c is
null for exactly the 1,011 Christian respondents, no more no less). So this
chart's population is India's Hindu, Muslim, Sikh, Buddhist, and Jain
respondents being asked specifically about Christians, not Christians'
own experience - a direct read on how tolerated India's ~2% Christian
minority is among its other major religious communities. QRELSING is the
respondent's own religion; weight is the dataset's final analysis weight.

Usage: python scripts/pew-india-2021/christian_neighbor_acceptance.py
"""
import json

import numpy as np
import pyreadstat

SAV = "data/pew-india-2021/India Religion Public Data - Pew Research Center (All Vars).sav"

RELIGION_CODES = {
    1.0: "Hindu",
    2.0: "Muslim",
    4.0: "Sikh",
    5.0: "Buddhist",
    6.0: "Jain",
}
YES = 1.0
VALID_CODES = {1.0, 2.0}  # Yes / No - excludes "other/both/neither", DK, refused
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["QRELSING", "Q63c", "weight"])
    weight = df["weight"].to_numpy()
    religion = df["QRELSING"].to_numpy()
    accept = df["Q63c"].to_numpy()

    results = {}
    for code, label in RELIGION_CODES.items():
        group_mask = religion == code
        valid = group_mask & np.isin(accept, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        yes = valid & (accept == YES)
        results[label] = {
            "pct": round(100 * weight[yes].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    # "All non-Christian adults" - everyone actually asked the question,
    # i.e. every respondent except the 1,011 Christians the item skips.
    asked_mask = religion != 3.0
    valid_all = asked_mask & np.isin(accept, list(VALID_CODES))
    yes_all = valid_all & (accept == YES)
    results["All non-Christian adults"] = {
        "pct": round(100 * weight[yes_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(asked_mask.sum()),
    }

    order = [label for label in results if label != "All non-Christian adults"]
    order.sort(key=lambda label: -results[label]["pct"])
    order.append("All non-Christian adults")

    out = {
        "source": "Pew Research Center. India Religion Survey, fielded November 17, 2019-March 23, 2020.",
        "method": "Population is the respondent's own religion (QRELSING), restricted to "
                  "respondents actually asked Q63c - the survey skips a respondent's own "
                  "religion in its neighbor-acceptance battery, so Christian respondents "
                  "(N=1,011) were never asked whether they'd accept a Christian neighbor. "
                  "Share answering \"yes\" to Q63c (\"Would you be willing to accept a "
                  "Christian as a neighbor?\"); \"other/both/neither/depends,\" don't know, "
                  "and refused excluded from each row's denominator. Groups under 30 valid "
                  "respondents omitted. Weighted by the dataset's own weight variable.",
        "total_weighted_n": float(weight[asked_mask].sum()),
        "total_unweighted_n": int(asked_mask.sum()),
        "group_order": order,
        "accept_christian_neighbor": results,
    }
    with open("docs/datasets/pew-india-2021/christian-neighbor-acceptance.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:26} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-india-2021/christian-neighbor-acceptance.json")


if __name__ == "__main__":
    main()

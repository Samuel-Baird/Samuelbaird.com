"""
Flagship chart for the 2015 Survey of U.S. Catholics and Family Life: should
divorced Catholics who remarry without getting an annulment be allowed to
receive Communion (Q.J31e / qj31e)? Restricted to respondents who are
Catholic by religion (RELIG=2 / relig==2.0) - a nationally representative
5,122-adult general-public survey with a Catholic oversample, not a
Catholic-only sample, so filtering to relig==2 is what makes this "U.S.
Catholics say..." rather than "U.S. adults say...". Broken out by how often
the respondent attends religious services (ATTEND), collapsed into the
survey's own three-bucket grouping (Weekly or more / Monthly-yearly /
Seldom-never) - this is the same collapse the codebook's own margin-of-error
table on p.2 uses, not an invented cutpoint.

Usage: python scripts/pew-catholic-family-2015/annulment_communion.py
"""
import json

import numpy as np
import pyreadstat

SAV = (
    "data/pew-catholic-family-2015/Dataset - Pew Research Center 2015 Survey "
    "of U.S. Catholics and Family Life - Version 1.1 - Mar 1, 2018.sav"
)

ATTEND_GROUPS = {
    "Attend weekly or more": {1.0, 2.0},
    "Attend monthly or yearly": {3.0, 4.0},
    "Seldom/never attend": {5.0, 6.0},
}
YES = 1.0
VALID_CODES = {1.0, 2.0}


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["relig", "attend", "qj31e", "weight"])
    cath = df[df["relig"] == 2.0].reset_index(drop=True)
    weight = cath["weight"].to_numpy()
    attend = cath["attend"].to_numpy()
    opinion = cath["qj31e"].to_numpy()

    results = {}
    for label, codes in ATTEND_GROUPS.items():
        group_mask = np.isin(attend, list(codes))
        valid = group_mask & np.isin(opinion, list(VALID_CODES))
        yes = valid & (opinion == YES)
        results[label] = {
            "pct": round(100 * weight[yes].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(opinion, list(VALID_CODES))
    yes_all = valid_all & (opinion == YES)
    results["All U.S. Catholics"] = {
        "pct": round(100 * weight[yes_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(cath)),
    }

    order = [label for label in results if label != "All U.S. Catholics"]
    order.sort(key=lambda label: -results[label]["pct"])
    order.append("All U.S. Catholics")

    out = {
        "source": "Pew Research Center. 2015 Survey of U.S. Catholics and Family Life, "
                  "fielded May 5-June 7, 2015.",
        "method": "Population is respondents who are Catholic by religion (RELIG=2), "
                  "broken out by how often they attend religious services (ATTEND), "
                  "collapsed into the survey's own three-bucket grouping (weekly or "
                  "more; monthly or yearly; seldom or never). Share saying the "
                  "Catholic Church should (Q.J31e: \"Allow divorced Catholics who "
                  "remarry without getting an annulment to receive Communion\"); "
                  "don't know/refused excluded from each row's denominator. Weighted "
                  "by the dataset's own WEIGHT variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(cath)),
        "group_order": order,
        "should_allow_communion_after_remarriage": results,
    }
    with open(
        "docs/datasets/pew-catholic-family-2015/annulment-communion.json", "w", encoding="utf-8"
    ) as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:28} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>4})")
    print("\nWrote docs/datasets/pew-catholic-family-2015/annulment-communion.json")


if __name__ == "__main__":
    main()

"""
2014 Religious Landscape Study: among people who did volunteer work in the
past seven days (qi3=1), was that volunteering mainly through a church or
other religious organization (qi3b), by current religious tradition
(RELTRAD). This is distinct from the general qi3 volunteering item (which
this site doesn't chart on its own, since a bare "who volunteers" number
carries no religious dimension) - qi3b asks specifically whether volunteers
route that service through their faith community. Latter-day Saint culture
emphasizes organized congregational service (temple and family history
service, ward welfare assignments, humanitarian projects coordinated
through local wards), so this checks whether that shows up as a distinctly
high share of LDS volunteering being channeled through the Church itself,
relative to other traditions' volunteers.

Usage: python scripts/pew-rls-2014/volunteer_through_church.py
"""
import json

import numpy as np
import pyreadstat

SAV = ("data/pew-rls-2014/"
       "Dataset - Pew Research Center 2014 Religious Landscape Study National Telephone "
       "Survey - Version 1.1 - December 1 2016.sav")

RELTRAD_CODES = {
    1100.0: "Evangelical Protestant",
    1200.0: "Mainline Protestant",
    1300.0: "Historically Black Protestant",
    10000.0: "Catholic",
    20000.0: "Mormon",
    30000.0: "Orthodox Christian",
    40001.0: "Jehovah's Witness",
    50000.0: "Jewish",
    60000.0: "Muslim",
    70000.0: "Buddhist",
    80000.0: "Hindu",
    100000.0: "Unaffiliated",
}
# qi3b: 1 = mainly through church/religious org, 3 = (VOL) both through
# religious org and another way. Both count as "volunteering that involved
# a religious organization." 2 = not mainly through a religious org.
THROUGH_CHURCH_CODES = {1.0, 3.0}
VALID_CODES = {1.0, 2.0, 3.0}
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["RELTRAD", "qi3", "qi3b", "WEIGHT"])
    weight = df["WEIGHT"].to_numpy()
    reltrad = df["RELTRAD"].to_numpy()
    qi3 = df["qi3"].to_numpy()
    qi3b = df["qi3b"].to_numpy()

    # qi3b is only asked of qi3==1.0 (did volunteer work in past 7 days).
    volunteers = qi3 == 1.0

    results = {}
    for code, label in RELTRAD_CODES.items():
        group_mask = reltrad == code
        valid = group_mask & volunteers & np.isin(qi3b, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        through_church = valid & np.isin(qi3b, list(THROUGH_CHURCH_CODES))
        results[label] = {
            "pct": round(100 * weight[through_church].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = volunteers & np.isin(qi3b, list(VALID_CODES))
    through_church_all = valid_all & np.isin(qi3b, list(THROUGH_CHURCH_CODES))
    results["All volunteers"] = {
        "pct": round(100 * weight[through_church_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(valid_all.sum()),
    }

    order = [label for label in results if label != "All volunteers"]
    order.sort(key=lambda label: -results[label]["pct"])
    order.append("All volunteers")

    out = {
        "source": 'Pew Research Center. 2015. "2014 Religious Landscape Study."',
        "method": "Population is respondents who did volunteer work in the past seven days "
                  "(qi3=1), classified by current religious tradition (RELTRAD). qi3b asked "
                  "whether that volunteering was mainly through a church or other religious "
                  "organization; a volunteered \"both through a religious organization and in "
                  "another way\" response is counted alongside \"mainly through a religious "
                  "organization.\" Don't know/refused are excluded from each row's denominator. "
                  "Groups with fewer than 30 valid respondents are omitted. Weighted by the "
                  "dataset's own national WEIGHT variable.",
        "total_weighted_n": float(weight[valid_all].sum()),
        "total_unweighted_n": int(valid_all.sum()),
        "group_order": order,
        "volunteered_through_religious_org": results,
    }
    with open(
        "docs/datasets/pew-rls-2014/volunteer-through-church.json", "w", encoding="utf-8"
    ) as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:38} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-rls-2014/volunteer-through-church.json")


if __name__ == "__main__":
    main()

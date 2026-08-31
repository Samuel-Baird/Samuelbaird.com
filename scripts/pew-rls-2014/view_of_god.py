"""
2014 Religious Landscape Study: is God a person one can have a relationship
with, or an impersonal force (qg1c), by current religious tradition
(RELTRAD)? Latter-day Saint theology teaches an embodied, personal God the
Father with whom people can literally have a relationship (as opposed to a
wholly transcendent/impersonal conception) - this item checks that teaching
against real survey data. Unlike qh2/born (asked only of Christians), qg1c
was asked of the full sample, so every tradition including Unaffiliated
clears the 30-valid-respondent floor easily. Groups with n < 30 valid
respondents are dropped, same convention as certainty_of_god.py in this
folder.

Usage: python scripts/pew-rls-2014/view_of_god.py
"""
import json

import numpy as np
import pyreadstat

SAV = ("data/pew-rls-2014/"
       "Dataset - Pew Research Center 2014 Religious Landscape Study National Telephone "
       "Survey - Version 1.1 - December 1 2016.sav")

RELTRAD_CODES = {
    1100.0: "Evangelical Protestant Tradition",
    1200.0: "Mainline Protestant Tradition",
    1300.0: "Historically Black Protestant Tradition",
    10000.0: "Catholic",
    20000.0: "Mormon",
    30000.0: "Orthodox Christian",
    40001.0: "Jehovah's Witness",
    50000.0: "Jewish",
    60000.0: "Muslim",
    70000.0: "Buddhist",
    80000.0: "Hindu",
    100000.0: "Unaffiliated (religious \"nones\")",
}
PERSON_CODE = {1.0}
VALID_CODES = {1.0, 2.0}
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["RELTRAD", "qg1c", "WEIGHT"])
    weight = df["WEIGHT"].to_numpy()
    reltrad = df["RELTRAD"].to_numpy()
    qg1c = df["qg1c"].to_numpy()

    results = {}
    for code, label in RELTRAD_CODES.items():
        group_mask = reltrad == code
        valid = group_mask & np.isin(qg1c, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        person = valid & np.isin(qg1c, list(PERSON_CODE))
        results[label] = {
            "pct": round(100 * weight[person].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(qg1c, list(VALID_CODES))
    person_all = valid_all & np.isin(qg1c, list(PERSON_CODE))
    results["All U.S. adults"] = {
        "pct": round(100 * weight[person_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }

    order = [label for label in results if label != "All U.S. adults"]
    order.sort(key=lambda label: -results[label]["pct"])
    order.append("All U.S. adults")

    out = {
        "source": 'Pew Research Center. 2015. "2014 Religious Landscape Study."',
        "method": "Population is current religious tradition (RELTRAD). qg1c asks "
                  "respondents who believe in God or a universal spirit to pick between "
                  "\"God is a person with whom people can have a relationship\" and \"God "
                  "is an impersonal force\" (a small volunteered \"both/neither\" share is "
                  "excluded, along with don't know/refused). Groups with fewer than 30 "
                  "valid respondents are omitted. Weighted by the dataset's own national "
                  "WEIGHT variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "god_is_a_person": results,
    }
    with open("docs/datasets/pew-rls-2014/view-of-god.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:38} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-rls-2014/view-of-god.json")


if __name__ == "__main__":
    main()

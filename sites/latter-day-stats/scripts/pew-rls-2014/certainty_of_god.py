"""
Third flagship chart for the 2014 Religious Landscape Study: how certain
are people that God exists (qg1b), by current religious tradition
(RELTRAD)? qg1b was only asked of respondents who said they believe in
God (skip pattern means non-believers fall outside VALID_CODES and are
excluded automatically). Top box is "Absolutely certain." Companion chart
to certainty_of_god.py in scripts/pew-rls-2007/ - same question,
2007-vs-2014 comparable in spirit though not identically worded. Groups
with n < 30 valid respondents are dropped, same convention as
weekly_attendance.py in this folder.

Usage: python scripts/pew-rls-2014/certainty_of_god.py
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
TOP_BOX = {1.0}
VALID_CODES = {1.0, 2.0, 3.0, 4.0}
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["RELTRAD", "qg1b", "WEIGHT"])
    weight = df["WEIGHT"].to_numpy()
    reltrad = df["RELTRAD"].to_numpy()
    certainty = df["qg1b"].to_numpy()

    results = {}
    for code, label in RELTRAD_CODES.items():
        group_mask = reltrad == code
        valid = group_mask & np.isin(certainty, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        top = valid & np.isin(certainty, list(TOP_BOX))
        results[label] = {
            "pct": round(100 * weight[top].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(certainty, list(VALID_CODES))
    top_all = valid_all & np.isin(certainty, list(TOP_BOX))
    results["All U.S. adults"] = {
        "pct": round(100 * weight[top_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }

    order = [label for label in results if label != "All U.S. adults"]
    order.sort(key=lambda label: -results[label]["pct"])
    order.append("All U.S. adults")

    out = {
        "source": 'Pew Research Center. 2015. "2014 Religious Landscape Study."',
        "method": "Population is current religious tradition (RELTRAD). qg1b (\"how "
                  "certain are you\") was asked only of respondents who said they believe "
                  "in God; non-believers and don't know/refused are excluded from each "
                  "row's denominator since they fall outside qg1b's valid range. Top box "
                  "is \"absolutely certain.\" Groups with fewer than 30 valid respondents "
                  "are omitted. Weighted by the dataset's own national WEIGHT variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "absolutely_certain": results,
    }
    with open("docs/datasets/pew-rls-2014/certainty-of-god.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:38} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-rls-2014/certainty-of-god.json")


if __name__ == "__main__":
    main()

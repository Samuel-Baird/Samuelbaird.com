"""
2014 Religious Landscape Study: is your scripture ("the Bible/the Torah/the
Koran/the Holy Scripture," worded to match the respondent's own tradition)
the word of God, or a book written by men (qg7), by current religious
tradition (RELTRAD). Asked of the full sample (each respondent gets the
version of the question worded for their own faith's scripture, or a
generic "the Holy Scripture" wording for smaller/unaffiliated groups), so
all 12 RELTRAD groups clear the 30-valid floor comfortably. Latter-day
Saints hold a strong doctrine of scripture as literal revealed word,
extending it to the Book of Mormon alongside the Bible - this item checks
where Latter-day Saints land on "word of God" framing relative to other
traditions.

Usage: python scripts/pew-rls-2014/scripture_word_of_god.py
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
WORD_OF_GOD_CODE = {1.0}
VALID_CODES = {1.0, 2.0}
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["RELTRAD", "qg7", "WEIGHT"])
    weight = df["WEIGHT"].to_numpy()
    reltrad = df["RELTRAD"].to_numpy()
    qg7 = df["qg7"].to_numpy()

    results = {}
    for code, label in RELTRAD_CODES.items():
        group_mask = reltrad == code
        valid = group_mask & np.isin(qg7, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        word_of_god = valid & np.isin(qg7, list(WORD_OF_GOD_CODE))
        results[label] = {
            "pct": round(100 * weight[word_of_god].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(qg7, list(VALID_CODES))
    word_of_god_all = valid_all & np.isin(qg7, list(WORD_OF_GOD_CODE))
    results["All U.S. adults"] = {
        "pct": round(100 * weight[word_of_god_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }

    order = [label for label in results if label != "All U.S. adults"]
    order.sort(key=lambda label: -results[label]["pct"])
    order.append("All U.S. adults")

    out = {
        "source": 'Pew Research Center. 2015. "2014 Religious Landscape Study."',
        "method": "Population is the full sample, classified by current religious tradition "
                  "(RELTRAD). qg7 asked whether the respondent's own scripture (worded to "
                  "match their tradition - the Bible, Torah, Koran, or generically \"the Holy "
                  "Scripture\") is the word of God, or a book written by men and not the word "
                  "of God; volunteered \"other\" and don't know/refused are excluded from each "
                  "row's denominator. Groups with fewer than 30 valid respondents are omitted. "
                  "Weighted by the dataset's own national WEIGHT variable.",
        "total_weighted_n": float(weight[valid_all].sum()),
        "total_unweighted_n": int(valid_all.sum()),
        "group_order": order,
        "scripture_is_word_of_god": results,
    }
    with open(
        "docs/datasets/pew-rls-2014/scripture-word-of-god.json", "w", encoding="utf-8"
    ) as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:38} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-rls-2014/scripture-word-of-god.json")


if __name__ == "__main__":
    main()

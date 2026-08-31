"""
2014 Religious Landscape Study: among respondents who say their own
scripture ("the Bible/the Torah/the Koran/the Holy Scripture," worded to
match the respondent's tradition) is the word of God (qg7=1), is it to be
taken literally, word for word, or not everything in it should be taken
literally (qg7b), by current religious tradition (RELTRAD). qg7b is
skip-gated to qg7=1 respondents only, so this reads "among Mormons who
already call scripture the word of God, how many also call it literal."
A natural follow-up to the already-shipped scripture-word-of-god chart
(qg7 itself): Latter-day Saints affirm scripture as revealed word at a
very high rate (93.8%, shipped), but this item asks a different question -
whether that word is meant word-for-word literally. LDS scripture includes
its own doctrine of imperfect transmission ("as far as it is translated
correctly," Articles of Faith 1:8) and ongoing modern revelation
supplementing ancient text, which could plausibly pull literalism down
even among a strongly "word of God" tradition.

Usage: python scripts/pew-rls-2014/scripture_literalism.py
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
LITERAL_CODE = {1.0}
VALID_CODES = {1.0, 2.0}
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["RELTRAD", "qg7b", "WEIGHT"])
    weight = df["WEIGHT"].to_numpy()
    reltrad = df["RELTRAD"].to_numpy()
    qg7b = df["qg7b"].to_numpy()

    results = {}
    for code, label in RELTRAD_CODES.items():
        group_mask = reltrad == code
        valid = group_mask & np.isin(qg7b, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        literal = valid & np.isin(qg7b, list(LITERAL_CODE))
        results[label] = {
            "pct": round(100 * weight[literal].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(qg7b, list(VALID_CODES))
    literal_all = valid_all & np.isin(qg7b, list(LITERAL_CODE))
    results["All U.S. adults"] = {
        "pct": round(100 * weight[literal_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }

    order = [label for label in results if label != "All U.S. adults"]
    order.sort(key=lambda label: -results[label]["pct"])
    order.append("All U.S. adults")

    out = {
        "source": 'Pew Research Center. 2015. "2014 Religious Landscape Study."',
        "method": "Population is respondents who said their own scripture (the Bible, Torah, "
                  "Koran, or generically \"the Holy Scripture,\" worded to match their "
                  "tradition) is the word of God (qg7=1), classified by current religious "
                  "tradition (RELTRAD); qg7b is skip-gated to this subsample. qg7b asked "
                  "whether that scripture is to be taken literally, word for word, or whether "
                  "not everything in it should be taken literally; volunteered \"other\" and "
                  "don't know/refused are excluded from each row's denominator. Groups with "
                  "fewer than 30 valid respondents are omitted. Weighted by the dataset's own "
                  "national WEIGHT variable.",
        "total_weighted_n": float(weight[valid_all].sum()),
        "total_unweighted_n": int(valid_all.sum()),
        "group_order": order,
        "scripture_taken_literally": results,
    }
    with open(
        "docs/datasets/pew-rls-2014/scripture-literalism.json", "w", encoding="utf-8"
    ) as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:38} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-rls-2014/scripture-literalism.json")


if __name__ == "__main__":
    main()

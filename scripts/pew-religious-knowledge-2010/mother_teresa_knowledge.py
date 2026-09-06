"""
Companion chart to joseph_smith_knowledge.py for the 2010 U.S. Religious
Knowledge Survey: who knows Mother Teresa was Catholic? qn48a asked all
respondents to identify Mother Teresa's religion (Catholic, Jewish,
Buddhist, Mormon, Hindu, or Other) - the correct answer is "Catholic".
Broken out by the respondent's own present religion (qn20), same
construction as joseph_smith_knowledge.py (that script's docstring covers
why the oversample design makes this usable even though Mormons are a
small share of the population). Where the Joseph Smith item asks whether
people know a fact ABOUT Latter-day Saints, this item flips the lens:
how well do Latter-day Saints themselves know a basic fact about another
tradition (Catholicism)?

Groups with n < 30 valid respondents are dropped rather than shown with an
unreliable estimate, same convention as the founding-date and Joseph
Smith charts.

Usage: python scripts/pew-religious-knowledge-2010/mother_teresa_knowledge.py
"""
import json

import numpy as np
import pyreadstat

SAV = ("data/pew-religious-knowledge-2010/"
       "Dataset - Pew Forum on Religion & Public Life 2010 US Religious Knowledge Survey.sav")

RELIGION_CODES = {
    1.0: "Protestant",
    2.0: "Catholic",
    3.0: "Mormon",
    4.0: "Orthodox Christian",
    5.0: "Jewish",
    6.0: "Muslim",
    9.0: "Atheist",
    10.0: "Agnostic",
    12.0: "Unaffiliated",
}
VALID_CODES = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
CORRECT_CODE = 1.0  # "Catholic"
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["qn20", "qn48a", "weight"])
    weight = df["weight"].to_numpy()
    religion = df["qn20"].to_numpy()
    answer = df["qn48a"].to_numpy()

    results = {}
    for code, label in RELIGION_CODES.items():
        group_mask = religion == code
        valid = group_mask & np.isin(answer, VALID_CODES)
        if valid.sum() < MIN_VALID_N:
            continue
        correct = valid & (answer == CORRECT_CODE)
        results[label] = {
            "pct": round(100 * weight[correct].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(answer, VALID_CODES)
    correct_all = valid_all & (answer == CORRECT_CODE)
    results["All U.S. adults"] = {
        "pct": round(100 * weight[correct_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }

    order = [label for label in results if label != "All U.S. adults"]
    order.sort(key=lambda label: -results[label]["pct"])
    order.append("All U.S. adults")

    out = {
        "source": 'Pew Research Center. 2010. "U.S. Religious Knowledge Survey."',
        "method": "qn48a asked all respondents to identify Mother Teresa's religion "
                  "(Catholic, Jewish, Buddhist, Mormon, or Hindu); the correct answer is "
                  "\"Catholic\". Broken out by the respondent's own present religion (qn20); "
                  "don't know/refused excluded from each row's denominator. Groups with "
                  "fewer than 30 valid respondents are omitted. Weighted by the dataset's "
                  "own `weight` variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "correct_pct": results,
    }
    with open("docs/datasets/pew-religious-knowledge-2010/mother-teresa-knowledge.json",
              "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:20} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>4})")
    print("\nWrote docs/datasets/pew-religious-knowledge-2010/mother-teresa-knowledge.json")


if __name__ == "__main__":
    main()

"""
New flagship chart for the 2010 U.S. Religious Knowledge Survey: who has
ever taken a college-level religion course? qn64 asked all respondents a
simple yes/no. Broken out by the respondent's own present religion (qn20),
same construction as mormon_founding_knowledge.py and its siblings in this
folder.

Unlike this folder's knowledge-quiz items, qn64 has no "correct" answer -
it's a self-reported experience item - but it fits the dataset's own
convention of a single item broken out by present religion, and Mormons
stand out sharply: the Church's institute-of-religion program places
Church Educational System religion classes alongside secular college
coursework for many Latter-day Saint young adults, a distinctive
institutional feature most other traditions in this survey don't have.

Groups with n < 30 valid respondents are dropped rather than shown with an
unreliable estimate, same convention as the other knowledge charts.

Usage: python scripts/pew-religious-knowledge-2010/college_religion_courses.py
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
VALID_CODES = [1.0, 2.0]
YES_CODE = 1.0
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["qn20", "qn64", "weight"])
    weight = df["weight"].to_numpy()
    religion = df["qn20"].to_numpy()
    answer = df["qn64"].to_numpy()

    results = {}
    for code, label in RELIGION_CODES.items():
        group_mask = religion == code
        valid = group_mask & np.isin(answer, VALID_CODES)
        if valid.sum() < MIN_VALID_N:
            continue
        yes = valid & (answer == YES_CODE)
        results[label] = {
            "pct": round(100 * weight[yes].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(answer, VALID_CODES)
    yes_all = valid_all & (answer == YES_CODE)
    results["All U.S. adults"] = {
        "pct": round(100 * weight[yes_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }

    order = [label for label in results if label != "All U.S. adults"]
    order.sort(key=lambda label: -results[label]["pct"])
    order.append("All U.S. adults")

    out = {
        "source": 'Pew Research Center. 2010. "U.S. Religious Knowledge Survey."',
        "method": "qn64 asked all respondents whether they have ever taken any "
                  "college-level religion course; don't know/refused excluded from each "
                  "row's denominator. Broken out by the respondent's own present religion "
                  "(qn20). Groups with fewer than 30 valid respondents are omitted. "
                  "Weighted by the dataset's own `weight` variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "correct_pct": results,
    }
    with open("docs/datasets/pew-religious-knowledge-2010/college-religion-courses.json",
              "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:20} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>4})")
    print("\nWrote docs/datasets/pew-religious-knowledge-2010/college-religion-courses.json")


if __name__ == "__main__":
    main()

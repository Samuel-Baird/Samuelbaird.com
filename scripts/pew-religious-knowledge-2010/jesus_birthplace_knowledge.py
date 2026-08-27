"""
Fifth flagship chart for the 2010 U.S. Religious Knowledge Survey: who
knows where the Bible says Jesus was born? qn41 asked all respondents to
choose from Bethlehem, Jericho, Jerusalem, or Nazareth - the correct
answer is "Bethlehem." Broken out by the respondent's own present religion
(qn20), same construction as mormon_founding_knowledge.py,
joseph_smith_knowledge.py, and book_of_mormon_knowledge.py in this folder.

Groups with n < 30 valid respondents are dropped, same convention as the
other by-religion knowledge charts.

Usage: python scripts/pew-religious-knowledge-2010/jesus_birthplace_knowledge.py
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
VALID_CODES = [1.0, 2.0, 3.0, 4.0]
CORRECT_CODE = 1.0  # "Bethlehem"
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["qn20", "qn41", "weight"])
    weight = df["weight"].to_numpy()
    religion = df["qn20"].to_numpy()
    answer = df["qn41"].to_numpy()

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
        "method": "qn41 asked all respondents where the Bible says Jesus was born "
                  "(Bethlehem, Jericho, Jerusalem, or Nazareth); the correct answer is "
                  "\"Bethlehem.\" Broken out by the respondent's own present religion "
                  "(qn20); don't know/refused excluded from each row's denominator. Groups "
                  "with fewer than 30 valid respondents are omitted. Weighted by the "
                  "dataset's own `weight` variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "correct_pct": results,
    }
    with open("docs/datasets/pew-religious-knowledge-2010/jesus-birthplace-knowledge.json",
              "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:20} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>4})")
    print("\nWrote docs/datasets/pew-religious-knowledge-2010/jesus-birthplace-knowledge.json")


if __name__ == "__main__":
    main()

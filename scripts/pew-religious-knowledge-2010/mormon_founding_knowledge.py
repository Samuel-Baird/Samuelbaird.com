"""
Flagship chart for the 2010 U.S. Religious Knowledge Survey: who actually
knows when the Mormon religion was founded? qn42 asked all respondents
"When was the Mormon religion founded?" with three options - the correct
answer is "Sometime after 1800" (Joseph Smith organized the Church in
1830). Broken out by the respondent's own present religion (qn20), which
this survey's own oversample design (recontacting self-identified Jewish,
Mormon, and atheist/agnostic respondents from earlier surveys) makes usable
even though Mormons are a small share of the general population.

Groups with n < 30 valid respondents are dropped rather than shown with an
unreliable estimate - this knowledge item wasn't stratified for smaller
world religions the way it was for the three oversampled groups.

Usage: python scripts/pew-religious-knowledge-2010/mormon_founding_knowledge.py
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
CORRECT_CODE = 3.0  # "Sometime after 1800"
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["qn20", "qn42", "weight"])
    weight = df["weight"].to_numpy()
    religion = df["qn20"].to_numpy()
    answer = df["qn42"].to_numpy()

    results = {}
    for code, label in RELIGION_CODES.items():
        group_mask = religion == code
        valid = group_mask & np.isin(answer, [1.0, 2.0, 3.0])
        if valid.sum() < MIN_VALID_N:
            continue
        correct = valid & (answer == CORRECT_CODE)
        results[label] = {
            "pct": round(100 * weight[correct].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(answer, [1.0, 2.0, 3.0])
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
        "method": "qn42 asked all respondents when the Mormon religion was founded; the "
                  "correct answer is \"sometime after 1800\" (1830). Broken out by the "
                  "respondent's own present religion (qn20); don't know/refused excluded "
                  "from each row's denominator. Groups with fewer than 30 valid respondents "
                  "are omitted. Weighted by the dataset's own `weight` variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "correct_pct": results,
    }
    with open("docs/datasets/pew-religious-knowledge-2010/mormon-founding-knowledge.json",
              "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:20} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>4})")
    print("\nWrote docs/datasets/pew-religious-knowledge-2010/mormon-founding-knowledge.json")


if __name__ == "__main__":
    main()

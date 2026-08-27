"""
Sixth flagship chart for the 2010 U.S. Religious Knowledge Survey: Pew's
own headline finding - the full 32-item knowledge score, by religious
group. Reproduces Pew's own composite from
"Answers to Knowledge Questions - Pew Forum on Religion & Public Life
2010 US Religious Knowledge Survey.pdf" (in this dataset's own folder),
which lists the correct answer for every scored item; the mapping below
transcribes that PDF's answer key against each item's own value labels.
Don't know/refused counts as incorrect, matching Pew's own published
scoring (the report's average-number-correct figures are lower than a
"among those who answered" average would produce).

This average-number-correct score (out of 32) is a per-respondent count
across the 32 items below - NOT a top-box share like every other chart in
this pipeline, so this script computes a mean rather than a %, and its
render script (render_overall_score_chart.py) passes value_suffix=""
instead of the shared default "%".

Usage: python scripts/pew-religious-knowledge-2010/overall_score.py
"""
import json

import numpy as np
import pyreadstat

SAV = ("data/pew-religious-knowledge-2010/"
       "Dataset - Pew Forum on Religion & Public Life 2010 US Religious Knowledge Survey.sav")

# item -> correct code(s). Every item scores don't-know/refused/other as
# incorrect (see docstring), so no separate "valid codes" set is needed -
# np.isin against the correct code(s) alone gives 0 for every other value.
ITEMS = {
    "qn15": {1.0},
    "qn17": {3.0},
    "qn35": {1.0},
    "qn36": {1.0},
    "qn37a": {2.0},
    "qn37b": {2.0},
    "qn38a": {2.0},
    "qn38b": {3.0},
    "qn39": {1.0},
    "qn40": {1.0},
    "qn41": {1.0},
    "qn42": {3.0},
    "qn43": {1.0},
    "qn44": {1.0},
    "qn45": {1.0},
    "qn46": {2.0},
    "qn47a": {1.0},
    "qn47c": {3.0},
    "qn47d": {4.0},
    "qn48a": {1.0},
    "qn48b": {3.0},
    "qn48c": {4.0},
    "qn48d": {2.0},
    "qn49": {2.0},
    "qn50a": {2.0},
    "qn50b": {1.0},
    "qn50c": {1.0},
    "qn55a": {2.0},
    "qn55b": {3.0},
    "qn55d": {3.0},
    "qn60": {1.0},
    "qn63": {1.0},
}

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
MIN_VALID_N = 30


def main():
    usecols = ["qn20", "weight", *ITEMS.keys()]
    df, _ = pyreadstat.read_sav(SAV, usecols=usecols)
    weight = df["weight"].to_numpy()
    religion = df["qn20"].to_numpy()

    # Per-respondent correct count across all 32 items; don't know/refused
    # (and any code outside that item's own valid set) scores as incorrect,
    # not excluded - matching Pew's own published scoring.
    n = len(df)
    correct_count = np.zeros(n)
    for item, correct_codes in ITEMS.items():
        answer = df[item].to_numpy()
        correct_count += np.isin(answer, list(correct_codes))

    def weighted_mean(mask):
        return float(np.average(correct_count[mask], weights=weight[mask]))

    results = {}
    for code, label in RELIGION_CODES.items():
        group_mask = religion == code
        if group_mask.sum() < MIN_VALID_N:
            continue
        results[label] = {
            "mean_correct": round(weighted_mean(group_mask), 2),
            "unweighted_n": int(group_mask.sum()),
        }

    results["All U.S. adults"] = {
        "mean_correct": round(weighted_mean(np.ones(n, dtype=bool)), 2),
        "unweighted_n": n,
    }

    order = [label for label in results if label != "All U.S. adults"]
    order.sort(key=lambda label: -results[label]["mean_correct"])
    order.append("All U.S. adults")

    out = {
        "source": 'Pew Research Center. 2010. "U.S. Religious Knowledge Survey."',
        "method": "Average number correct (out of 32 scored items) per respondent, by "
                  "present religion (qn20). Correct-answer key transcribed from this "
                  "dataset's own \"Answers to Knowledge Questions\" PDF. Don't know/"
                  "refused (and any other non-matching response) scores as incorrect, "
                  "matching Pew's own published scoring - not excluded from the item. "
                  "Groups with fewer than 30 respondents are omitted. Weighted by the "
                  "dataset's own `weight` variable.",
        "n_items": len(ITEMS),
        "total_unweighted_n": n,
        "group_order": order,
        "results": results,
    }
    with open("docs/datasets/pew-religious-knowledge-2010/overall-score.json",
              "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:20} {r['mean_correct']:5.1f} of 32  (n={r['unweighted_n']:>4})")
    print("\nWrote docs/datasets/pew-religious-knowledge-2010/overall-score.json")


if __name__ == "__main__":
    main()

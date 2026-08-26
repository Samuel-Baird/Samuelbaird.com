"""
Computes "Feel like a stranger in my own country" by religion, 2017 wave,
for the Data Explorer's Ryan Burge / VOTER Survey Panel graphics - the
first of four items in
docs/datasets/ryan-burge/GRAPHICS_TODO.md's "VOTER Survey Panel" section.

Verbatim question stem, pulled from the Voter Study Group's own VOTER
Survey codebook (not paraphrased, per this backlog item's own instruction):
"How much do you agree or disagree with this statement? - These days I
feel like a stranger in my own country." 4-point scale: Strongly agree /
Mostly agree / Mostly disagree / Strongly disagree.

Population/grouping: `religpew_2017` (matches the wave this item was asked
in), per the backlog item's own recommended default over
`religpew_baseline`. Weighted by `weight_2017`.

**Design decision**: three of the twelve religpew_2017 categories are too
thin to respectably show individually - Orthodox (n=18), Muslim (n=13),
Hindu (n=3) - well below every other group shown here (next-smallest is
Buddhist at n=51) and below any group this project has shown individually
elsewhere (the thinnest kept anywhere so far is Pew RLS's "Other world
religions" at n=99). Excluded from the chart; noted in its own JSON key and
the render script's caption rather than silently dropped.

Usage: python scripts/ryan-burge/voter_stranger.py
"""
import json

import numpy as np
import pandas as pd
import pyreadstat

DTA = "data/ryan-burge/tier1-strong/voter_survey_panel.dta"

RELIGION_LABELS = {
    1: "Protestant", 2: "Catholic", 3: "Mormon", 5: "Jewish",
    7: "Buddhist", 9: "Atheist", 10: "Agnostic",
    11: "Nothing in particular", 12: "Something else",
}
EXCLUDED_TOO_THIN = {4: "Orthodox (n=18)", 6: "Muslim (n=13)", 8: "Hindu (n=3)"}
GROUP_ORDER = ["Mormon", "Protestant", "Catholic", "Jewish", "Buddhist",
               "Atheist", "Agnostic", "Nothing in particular", "Something else"]

STRANGER_LABELS = {1: "Strongly agree", 2: "Mostly agree", 3: "Mostly disagree", 4: "Strongly disagree"}
STRANGER_ORDER = list(STRANGER_LABELS.values())
INVALID_CODES = {8, 9}  # Skipped / Not Asked


def main():
    df, _ = pyreadstat.read_dta(
        DTA, usecols=["religpew_2017", "stranger_2017", "weight_2017"],
        apply_value_formats=False,
    )
    religion = df["religpew_2017"].to_numpy(dtype=float)
    stranger = df["stranger_2017"].to_numpy(dtype=float)
    weight = df["weight_2017"].to_numpy(dtype=float)

    results = {}
    for code, label in RELIGION_LABELS.items():
        group_mask = religion == code
        valid = group_mask & ~np.isin(stranger, list(INVALID_CODES)) & ~np.isnan(stranger)
        base_w = weight[valid].sum()
        shares = {}
        for scode, slabel in STRANGER_LABELS.items():
            w = weight[valid & (stranger == scode)].sum()
            shares[slabel] = round(100 * w / base_w, 2) if base_w else None
        results[label] = {
            "shares_pct": {label2: shares[label2] for label2 in STRANGER_ORDER},
            "valid_n": int(valid.sum()),
            "group_n": int(group_mask.sum()),
        }

    out = {
        "source": "Democracy Fund Voter Study Group / YouGov, VOTER (Views of the Electorate "
                   "Research) Survey Panel, 2017 wave, via Ryan Burge (github.com/ryanburge).",
        "via": "Ryan Burge",
        "question": "How much do you agree or disagree with this statement? - These days I "
                    "feel like a stranger in my own country.",
        "question_source": "Voter Study Group VOTER Survey codebook (verbatim, not paraphrased).",
        "method": "Population: religpew_2017 (wave-matched religion), weighted by weight_2017. "
                  "Excludes three categories too thin to show individually - see "
                  "excluded_too_thin below.",
        "excluded_too_thin": EXCLUDED_TOO_THIN,
        "group_order": GROUP_ORDER,
        "stranger_order": STRANGER_ORDER,
        "results": results,
    }
    with open("docs/datasets/ryan-burge/voter-stranger.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print("\n=== Feel like a stranger in my own country, by religion (2017) ===")
    for group in GROUP_ORDER:
        r = results[group]
        shares = ", ".join(f"{k} {v:.0f}%" for k, v in r["shares_pct"].items())
        print(f"{group:24} {shares}  (n={r['valid_n']})")

    print("\nWrote docs/datasets/ryan-burge/voter-stranger.json")


if __name__ == "__main__":
    main()

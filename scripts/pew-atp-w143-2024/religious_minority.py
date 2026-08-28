"""
Flagship chart for ATP Wave 143 (February 2024): who thinks of themselves as
part of a religious minority (RELIGMINORITY_W143), broken out by religion?

This wave does NOT carry the usual F_RELTRAD frame variable that other ATP
waves in this repo (e.g. pew-atp-w70-2020) use for the by-religion group -
checked the .sav metadata directly, not just the readme/questionnaire text,
and F_RELTRAD is simply absent from this wave's 140-variable list. The
closest substitute is F_RELIG, Pew's own religious-affiliation variable for
this wave, which classifies Latter-day Saints as code 3.0 ("Mormon (Church
of Jesus Christ of Latter-day Saints or LDS)") rather than F_RELTRAD's usual
20000. Groups here are therefore religions (Protestant, Catholic, Mormon,
Orthodox Christian, Jewish, Muslim, Buddhist, Hindu, Atheist, Agnostic,
Other, Nothing in particular), not the coarser Evangelical/Mainline/
Historically Black Protestant tradition buckets F_RELTRAD would give -
matches this wave's own building block, not a false equivalence to W70's
charts.

RELIGMINORITY_W143 asks: "Do you think of yourself as part of a minority
group because of your religious beliefs?" Latter-day Saints (59%) stand out
sharply above every other Christian group in this wave (Protestants 29%,
Catholics 25%, Orthodox Christians 49%) - closer to Muslims (57%) and Hindus
(56%) than to other Christians, second only to Jewish respondents (84%).
That gap is the flagship story here.

Usage: python scripts/pew-atp-w143-2024/religious_minority.py
"""
import json

import numpy as np
import pyreadstat

SAV = "data/pew-atp-w143-2024/ATP W143.sav"

RELIG_CODES = {
    1.0: "Protestant",
    2.0: "Catholic",
    3.0: "Mormon",
    4.0: "Orthodox Christian",
    5.0: "Jewish",
    6.0: "Muslim",
    7.0: "Buddhist",
    8.0: "Hindu",
    9.0: "Atheist",
    10.0: "Agnostic",
    11.0: "Other",
    12.0: "Nothing in particular",
}
YES = 1.0
VALID_CODES = {1.0, 2.0}
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["F_RELIG", "RELIGMINORITY_W143", "WEIGHT_W143"])
    weight = df["WEIGHT_W143"].to_numpy()
    relig = df["F_RELIG"].to_numpy()
    minority = df["RELIGMINORITY_W143"].to_numpy()

    results = {}
    for code, label in RELIG_CODES.items():
        group_mask = relig == code
        valid = group_mask & np.isin(minority, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        yes = valid & (minority == YES)
        results[label] = {
            "pct": round(100 * weight[yes].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(minority, list(VALID_CODES))
    yes_all = valid_all & (minority == YES)
    results["U.S. adults"] = {
        "pct": round(100 * weight[yes_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }

    out = {
        "source": "Pew Research Center. American Trends Panel Wave 143, fielded Feb. 13-25, 2024.",
        "method": "Population is all respondents, grouped by religious affiliation (F_RELIG) - "
                  "this wave does not carry the F_RELTRAD frame variable other ATP waves in this "
                  "repo use. Share answering \"yes\" to RELIGMINORITY_W143 (\"Do you think of "
                  "yourself as part of a minority group because of your religious beliefs?\"); "
                  "refused excluded from each row's denominator. Groups under 30 valid respondents "
                  "omitted. Weighted by the dataset's own WEIGHT_W143 variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": list(results.keys()),
        "religious_minority": results,
    }
    with open("docs/datasets/pew-atp-w143-2024/religious-minority.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label, r in sorted(results.items(), key=lambda kv: -kv[1]["pct"]):
        print(f"{label:24} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-atp-w143-2024/religious-minority.json")


if __name__ == "__main__":
    main()

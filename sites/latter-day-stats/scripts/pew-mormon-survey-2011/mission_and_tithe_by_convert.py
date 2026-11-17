"""
Fifth flagship chart for the 2011 National Survey of Mormons: do converts
and lifelong Mormons differ in whether they served a full-time mission
(q413) or pay a full tithe (q416)? Convert status is q430 ("in what
religion were you raised") - raised Mormon (code 3) is "Lifelong," anyone
else (excluding don't know/refused) is "Convert." Two items grouped into
one ranking chart rather than two single-bar charts, matching this site's
"which of these items" single-population convention (see
reasons_joined_lds.py in scripts/pew-faith-in-flux-2008/) but split into
two rows per group.

Usage: python scripts/pew-mormon-survey-2011/mission_and_tithe_by_convert.py
"""
import json

import numpy as np
import pyreadstat

SAV = ("data/pew-mormon-survey-2011/"
       "Dataset - Pew Forum on Religion & Public Life 2011 National Survey of Mormons.sav")

RAISED_MORMON = 3.0
RAISED_VALID = {v for v in range(1, 15) if v != 3} | {3.0}


def convert_status(raised):
    lifelong = raised == RAISED_MORMON
    convert = np.isin(raised, list(RAISED_VALID)) & ~lifelong
    return lifelong, convert


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["q430", "q413", "q416", "weight"])
    weight = df["weight"].to_numpy()
    raised = df["q430"].to_numpy()
    mission = df["q413"].to_numpy()
    tithe = df["q416"].to_numpy()

    lifelong, convert = convert_status(raised)

    def share(mask, item, valid_codes, yes_code):
        valid = mask & np.isin(item, valid_codes)
        yes = valid & (item == yes_code)
        return {
            "pct": round(100 * weight[yes].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
        }

    results = {
        "Served a full-time mission — Lifelong Mormons": share(lifelong, mission, [1.0, 2.0], 1.0),
        "Served a full-time mission — Converts": share(convert, mission, [1.0, 2.0], 1.0),
        "Pay a full tithe — Lifelong Mormons": share(lifelong, tithe, [1.0, 2.0], 1.0),
        "Pay a full tithe — Converts": share(convert, tithe, [1.0, 2.0], 1.0),
    }
    order = ["Served a full-time mission — Lifelong Mormons",
             "Served a full-time mission — Converts",
             "Pay a full tithe — Lifelong Mormons",
             "Pay a full tithe — Converts"]

    out = {
        "source": 'Pew Research Center. 2012. "2011 National Survey of Mormons."',
        "method": "Convert status from q430 (\"in what religion were you raised\"): "
                  "\"Lifelong\" is raised Mormon, \"Convert\" is raised anything else "
                  "(don't know/refused on q430 excluded from both groups). Each item's own "
                  "don't know/refused excluded from its own denominator. Weighted by the "
                  "dataset's own `weight` variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "lifelong_unweighted_n": int(lifelong.sum()),
        "convert_unweighted_n": int(convert.sum()),
        "row_order": order,
        "results": results,
    }
    with open("docs/datasets/pew-mormon-survey-2011/mission-and-tithe-by-convert.json",
              "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:44} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>4})")
    print("\nWrote docs/datasets/pew-mormon-survey-2011/mission-and-tithe-by-convert.json")


if __name__ == "__main__":
    main()

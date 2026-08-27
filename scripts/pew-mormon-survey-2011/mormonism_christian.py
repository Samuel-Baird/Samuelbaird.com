"""
Second chart for the 2011 National Survey of Mormons: is Mormonism a
Christian religion? q442 asked Mormon respondents directly. Unlike this
dataset's other items, "don't know/refused" is kept IN the base here
rather than excluded - Pew's own published topline for this question
reports Yes/No/Don't know as three segments of the full 100%, and that's
exactly what this chart reproduces (weighted: 97.3/1.7/1.0, which rounds
to Pew's published 97/2/1).

The "U.S. general public" comparison bar is NOT computed from this
dataset - Pew's own November 2011 report ("Mormons in America") paired
q442 against a same-worded question run on non-Mormons in a separate
general-population survey we don't hold the microdata for. Those three
numbers (51/32/17) are copied verbatim from Pew's own published chart and
recorded here with their own explicit source note, not derived from
data/pew-mormon-survey-2011/ - if that companion survey's microdata is
ever obtained, replace this constant with a real computation.

Usage: python scripts/pew-mormon-survey-2011/mormonism_christian.py
"""
import json

import numpy as np
import pyreadstat

SAV = ("data/pew-mormon-survey-2011/"
       "Dataset - Pew Forum on Religion & Public Life 2011 National Survey of Mormons.sav")

SEGMENT_ORDER = ["Yes", "No", "Don't know"]

# Pew Research Center. 2012. "Mormons in America." Q.442 topline, general
# public comparison figure (November 2011 survey of non-Mormons) - not
# computed here; see module docstring.
GENERAL_PUBLIC_PCT = {"Yes": 51.0, "No": 32.0, "Don't know": 17.0}


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["q442", "weight"])
    weight = df["weight"].to_numpy()
    answer = df["q442"].to_numpy()

    base = np.isin(answer, [1.0, 2.0, 9.0])
    base_w = weight[base].sum()
    mormons_pct = {
        "Yes": round(100 * weight[answer == 1.0].sum() / base_w, 1),
        "No": round(100 * weight[answer == 2.0].sum() / base_w, 1),
        "Don't know": round(100 * weight[answer == 9.0].sum() / base_w, 1),
    }

    out = {
        "source": 'Pew Research Center. 2012. "Mormons in America."',
        "method": "q442 (\"do you think of Mormonism as a Christian religion, or is it not a "
                  "Christian religion?\") asked of Mormon respondents; don't know/refused kept "
                  "IN the base as its own segment (not excluded), matching Pew's own published "
                  "topline treatment of this question. Weighted by the dataset's own `weight` "
                  "variable. The \"U.S. general public\" row is copied verbatim from Pew's own "
                  "published comparison (a November 2011 survey of non-Mormons this site does "
                  "not hold microdata for) - not computed from this dataset.",
        "segment_order": SEGMENT_ORDER,
        "row_order": ["U.S. Mormons", "U.S. general public"],
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "mormons_unweighted_n": int(base.sum()),
        "results": {
            "U.S. Mormons": mormons_pct,
            "U.S. general public": GENERAL_PUBLIC_PCT,
        },
    }
    with open("docs/datasets/pew-mormon-survey-2011/mormonism-christian.json",
              "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for row in out["row_order"]:
        vals = out["results"][row]
        print(f"{row:22} " + "  ".join(f"{seg}={vals[seg]:.1f}%" for seg in SEGMENT_ORDER))
    print("\nWrote docs/datasets/pew-mormon-survey-2011/mormonism-christian.json")


if __name__ == "__main__":
    main()

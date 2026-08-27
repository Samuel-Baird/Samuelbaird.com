"""
Flagship chart for Faith in Flux: among the survey's 38 respondents who
converted TO Mormonism (CURREL2 = 20000), which reasons do they give for
joining? Unlike the other flagship charts in this batch, this one isn't a
by-group comparison - it's a single population (LDS converts) broken out
by which of six candidate reasons (q17a/b/e/f/g/h) they call "an important
reason," matching the survey's own yes/not-important framing. n=38 is
small (this is a specific-conversion subgroup of a 2,867-respondent
recontact survey - see docs/datasets/pew-faith-in-flux-2008/README.md), so
this leans on the site's own convention of showing a small-n LDS result
with its n stated rather than omitting it (see e.g. the VOTER Survey
Panel's 84-141 respondent LDS breakouts).

Usage: python scripts/pew-faith-in-flux-2008/reasons_joined_lds.py
"""
import json

import numpy as np
import pyreadstat

SAV = ("data/pew-faith-in-flux-2008/"
       "Dataset - Pew Forum on Religion & Public Life 2008 Conversion Recontact Survey.sav")

REASON_ITEMS = {
    "q17g": "Felt called by God",
    "q17f": "Enjoyed the services and style of worship",
    "q17a": "Married someone of that religion",
    "q17h": "Asked to join by a member of the religion",
    "q17e": "Attracted by a particular minister or pastor",
    "q17b": "Moved to a new community",
}
CURREL2_MORMON = 20000.0
IMPORTANT = 1.0
VALID_CODES = {1.0, 2.0}


def main():
    usecols = ["CURREL2", "weight", *REASON_ITEMS.keys()]
    df, _ = pyreadstat.read_sav(SAV, usecols=usecols)
    weight = df["weight"].to_numpy()
    is_lds_convert = (df["CURREL2"].to_numpy() == CURREL2_MORMON)
    n_converts = int(is_lds_convert.sum())

    results = {}
    for col, label in REASON_ITEMS.items():
        item = df[col].to_numpy()
        valid = is_lds_convert & np.isin(item, list(VALID_CODES))
        important = valid & (item == IMPORTANT)
        results[label] = {
            "pct": round(100 * weight[important].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
        }

    order = sorted(results, key=lambda label: -results[label]["pct"])

    out = {
        "source": 'Pew Research Center. 2009. "Faith in Flux: Changes in Religious '
                  'Affiliation in the U.S."',
        "method": "Population is the subset of respondents who converted TO Mormonism "
                  "(CURREL2 = 20000), a small subgroup of this 2,867-respondent recontact "
                  "survey. Each reason's own don't know/refused excluded from its own "
                  "denominator. Weighted by the dataset's own `weight` variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "lds_converts_unweighted_n": n_converts,
        "reason_order": order,
        "important_reason_pct": results,
    }
    with open("docs/datasets/pew-faith-in-flux-2008/reasons-joined-lds.json",
              "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"LDS converts in sample: n={n_converts}")
    for label in order:
        r = results[label]
        print(f"{label:44} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>3})")
    print("\nWrote docs/datasets/pew-faith-in-flux-2008/reasons-joined-lds.json")


if __name__ == "__main__":
    main()

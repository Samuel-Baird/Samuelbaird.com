"""
Seventh flagship chart for Faith in Flux: across the survey's q22 battery
("Please tell me which, if any, you have ever identified with at any point
in your life"), what share of religious switchers have EVER passed through
each named identity - not necessarily their childhood religion (FRMREL) or
current religion (CURREL), just anywhere along the way? Unlike every other
chart built from this dataset, this one is a single-population item-battery
ranking across a set of NAMED IDENTITIES rather than reasons or a two-way
split, so it uses `highlight_rows` (not `group_identity`) to pick out just
the Mormon row, the same convention as w44KnowsAMormonGraphic and other
single-item-highlighted-in-a-battery charts elsewhere on the site.

The finding: at 2.7%, Mormon is the least-often-passed-through named
identity in the battery - respondents are far more likely to report having
ever identified as Baptist (13.3%), Nondenominational Christian (27.5%),
or "nothing in particular" (34.3%) at some point than as Mormon. Read
together with reasons_joined_lds.py (only 38 respondents in this whole
2,867-person recontact survey ever became Mormon at all), this is more
evidence LDS identity is rarely a way station on a longer path of
religious searching, for better or worse - people who try it tend to have
arrived there directly rather than passed through it en route elsewhere.

Each item has its own valid-response base (the survey's own skip logic
means not everyone was asked about every identity, e.g. people already
Catholic likely weren't asked "have you ever been Catholic"), so `results`
stores each item's own weighted pct and unweighted valid n rather than a
shared denominator.

Usage: python scripts/pew-faith-in-flux-2008/ever_identified_with.py
"""
import json

import numpy as np
import pyreadstat

SAV = ("data/pew-faith-in-flux-2008/"
       "Dataset - Pew Forum on Religion & Public Life 2008 Conversion Recontact Survey.sav")

IDENTITY_ITEMS = {
    "q22a": "Baptist",
    "q22b": "Methodist",
    "q22c": "Nondenominational Christian",
    "q22d": "Lutheran",
    "q22e": "Other Protestant",
    "q22f": "Catholic",
    "q22g": "Mormon",
    "q22h": "Jewish",
    "q22h2": "Nothing in particular",
    "q22i": "Atheist",
    "q22j": "Agnostic",
    "q22l": "Other religion",
}
YES = 1.0
VALID_CODES = {1.0, 2.0}


def main():
    usecols = ["weight", *IDENTITY_ITEMS.keys()]
    df, _ = pyreadstat.read_sav(SAV, usecols=usecols)
    weight = df["weight"].to_numpy()

    results = {}
    for col, label in IDENTITY_ITEMS.items():
        item = df[col].to_numpy()
        valid = np.isin(item, list(VALID_CODES))
        yes = valid & (item == YES)
        results[label] = {
            "pct": round(100 * weight[yes].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
        }

    order = sorted(results, key=lambda label: -results[label]["pct"])

    out = {
        "source": 'Pew Research Center. 2009. "Faith in Flux: Changes in Religious '
                  'Affiliation in the U.S."',
        "method": "Population is all 2,867 respondents in this recontact survey of "
                  "religious switchers. Each item in the q22 battery asks whether the "
                  "respondent has EVER identified with a named religion/identity at any "
                  "point in their life, not just as their childhood (FRMREL) or current "
                  "(CURREL) religion; each item has its own valid-response base due to the "
                  "survey's own skip logic and don't know/refused exclusions. Weighted by "
                  "the dataset's own `weight` variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "identity_order": order,
        "ever_identified_pct": results,
    }
    with open("docs/datasets/pew-faith-in-flux-2008/ever-identified-with.json",
              "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:30} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>4})")
    print("\nWrote docs/datasets/pew-faith-in-flux-2008/ever-identified-with.json")


if __name__ == "__main__":
    main()

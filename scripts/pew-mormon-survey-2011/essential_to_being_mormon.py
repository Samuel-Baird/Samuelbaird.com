"""
Third flagship chart for the 2011 National Survey of Mormons: which of five
candidate beliefs/practices do Mormons themselves call "essential for being
a good Mormon" (q411a/c/e/f/g)? A single-population ranking, like Faith in
Flux's "reasons joined" chart, not a by-group comparison. Each item's own
don't know/refused (9) is excluded from that item's own denominator; "not
too important" and "not at all important" are collapsed into "essential"
vs. everything else, matching the survey's own four-point framing collapsed
to a single yes/no share (same convention as ordination_by_activity.py).

Usage: python scripts/pew-mormon-survey-2011/essential_to_being_mormon.py
"""
import json

import numpy as np
import pyreadstat

SAV = ("data/pew-mormon-survey-2011/"
       "Dataset - Pew Forum on Religion & Public Life 2011 National Survey of Mormons.sav")

ITEMS = {
    "q411a": "Believing Joseph Smith saw God the Father and Jesus Christ",
    "q411e": "Working to help the poor and needy",
    "q411f": "Having regular family home evenings or family nights",
    "q411c": "Not drinking coffee and tea",
    "q411g": "Not watching R-rated movies",
}
VALID_CODES = {1.0, 2.0, 3.0, 4.0}
ESSENTIAL = 1.0


def main():
    usecols = ["weight", *ITEMS.keys()]
    df, _ = pyreadstat.read_sav(SAV, usecols=usecols)
    weight = df["weight"].to_numpy()

    results = {}
    for col, label in ITEMS.items():
        item = df[col].to_numpy()
        valid = np.isin(item, list(VALID_CODES))
        essential = valid & (item == ESSENTIAL)
        results[label] = {
            "pct": round(100 * weight[essential].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
        }

    order = sorted(results, key=lambda label: -results[label]["pct"])

    out = {
        "source": 'Pew Research Center. 2012. "2011 National Survey of Mormons."',
        "method": "Population is all respondents (self-identified Mormons by the survey's "
                  "own design). Each item's own don't know/refused excluded from its own "
                  "denominator; \"essential\" is the top of a four-point scale (essential, "
                  "important but not essential, not too important, not at all important). "
                  "Weighted by the dataset's own `weight` variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "item_order": order,
        "essential_pct": results,
    }
    with open("docs/datasets/pew-mormon-survey-2011/essential-to-being-mormon.json",
              "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:60} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>4})")
    print("\nWrote docs/datasets/pew-mormon-survey-2011/essential-to-being-mormon.json")


if __name__ == "__main__":
    main()

"""
Do Mormons see polygamy as morally acceptable? (q208d) A single-population
distribution across the item's own four response options, in the style of
essential_to_being_mormon.py - not a by-group comparison. Own don't
know/refused (9) excluded from the denominator.

Hook: Sep 25, 2026 (Woodruff Manifesto, 136th anniversary) / Oct 6 (Church
membership accepts the Manifesto at General Conference, 136th anniversary).

Usage: python scripts/pew-mormon-survey-2011/polygamy_morality.py
"""
import json

import numpy as np
import pyreadstat

SAV = ("data/pew-mormon-survey-2011/"
       "Dataset - Pew Forum on Religion & Public Life 2011 National Survey of Mormons.sav")

OPTIONS = {
    2.0: "Morally wrong",
    3.0: "Not a moral issue",
    1.0: "Morally acceptable",
    4.0: "Depends on the situation",
}


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["q208d", "weight"])
    weight = df["weight"].to_numpy()
    col = df["q208d"].to_numpy()
    valid = np.isin(col, list(OPTIONS.keys()))
    base_w = weight[valid].sum()

    results = {}
    for code, label in OPTIONS.items():
        hit = valid & (col == code)
        results[label] = {
            "pct": round(100 * weight[hit].sum() / base_w, 2),
            "valid_unweighted_n": int(hit.sum()),
        }

    order = sorted(OPTIONS.values(), key=lambda label: -results[label]["pct"])

    out = {
        "source": 'Pew Research Center. 2012. "2011 National Survey of Mormons."',
        "method": "Population is all respondents (self-identified Mormons by the survey's "
                  "own design). Don't know/refused excluded from the denominator. Weighted "
                  "by the dataset's own `weight` variable.",
        "total_weighted_n": float(weight[valid].sum()),
        "total_unweighted_n": int(valid.sum()),
        "item_order": order,
        "polygamy_view_pct": results,
    }
    with open("docs/datasets/pew-mormon-survey-2011/polygamy-morality.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:28} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>4})")
    print("\nWrote docs/datasets/pew-mormon-survey-2011/polygamy-morality.json")


if __name__ == "__main__":
    main()

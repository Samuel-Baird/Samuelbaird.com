"""
Fourth flagship chart for the 2010 U.S. Religious Knowledge Survey: how
well do Americans know what the Supreme Court has ruled public school
teachers can and can't do regarding religion? Three items (qn50a/b/c),
each asked of all respondents; correct answers are "not permitted" for
qn50a (leading a class in prayer) and "permitted" for qn50b (reading the
Bible as literature) and qn50c (a comparative-religion class). Unlike
mormon_founding_knowledge.py and its siblings in this folder (each a
single item broken out by religion), this is a single-population ranking
across three items, matching the "which of these" convention used
elsewhere on the site (e.g. reasons_joined_lds.py in
scripts/pew-faith-in-flux-2008/).

Usage: python scripts/pew-religious-knowledge-2010/church_state_law.py
"""
import json

import numpy as np
import pyreadstat

SAV = ("data/pew-religious-knowledge-2010/"
       "Dataset - Pew Forum on Religion & Public Life 2010 US Religious Knowledge Survey.sav")

ITEMS = {
    "qn50a": ("Lead a class in prayer", 2.0),
    "qn50c": ("Teach a class comparing world religions", 1.0),
    "qn50b": ("Read from the Bible as an example of literature", 1.0),
}
VALID_CODES = {1.0, 2.0}


def main():
    usecols = ["weight", *ITEMS.keys()]
    df, _ = pyreadstat.read_sav(SAV, usecols=usecols)
    weight = df["weight"].to_numpy()

    results = {}
    for col, (label, correct_code) in ITEMS.items():
        item = df[col].to_numpy()
        valid = np.isin(item, list(VALID_CODES))
        correct = valid & (item == correct_code)
        results[label] = {
            "pct": round(100 * weight[correct].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
        }

    order = sorted(results, key=lambda label: -results[label]["pct"])

    out = {
        "source": 'Pew Research Center. 2010. "U.S. Religious Knowledge Survey."',
        "method": "Population is all U.S. adults. Each item asks whether the U.S. "
                  "Constitution, per Supreme Court rulings, permits a public school "
                  "teacher to do the named thing; don't know/refused excluded from each "
                  "item's own base. Weighted by the dataset's own `weight` variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "item_order": order,
        "correct_pct": results,
    }
    with open("docs/datasets/pew-religious-knowledge-2010/church-state-law.json",
              "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:52} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>4})")
    print("\nWrote docs/datasets/pew-religious-knowledge-2010/church-state-law.json")


if __name__ == "__main__":
    main()

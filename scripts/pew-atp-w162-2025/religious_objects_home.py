"""
ATP Wave 162 (February 2025): whether respondents have religious objects or
artwork displayed in their home (RELART_W162), broken out by present religion
(RELIG_W162 - see religious_conflict.py's module docstring for why this wave
uses RELIG_W162 rather than an F_RELTRAD frame variable).

RELART_W162 is asked of the full sample (all 9,544 respondents, incl. all 135
unweighted Mormons) as a single yes/no item, not part of the split-sample
PRACTICEA_* "how often do you do each of the following" battery (that battery
randomizes some sub-items, e.g. PRACTICEA_BIB_W162 vs PRACTICEA_OTHSCRPT_W162,
across respondents, which would make a same-item cross-tradition comparison
unreliable - RELART_W162 has no such split and is asked identically of every
respondent). The item's own examples ("a cross, crucifix, or pictures of Jesus
or the saints") are Catholic/Christian-coded, but distinct in construct from
the already-shipped devotion-to-saints.png (PRACTICEA_SAINTS_W162, an active
devotional-practice frequency item) - this is a passive home-display item, not
a practice. Despite the Catholic-coded wording, Latter-day Saints report the
highest rate of any tradition with an adequate sample (Hindu's 88.9% is higher
but n=9, below the 30-valid floor).

Usage: python scripts/pew-atp-w162-2025/religious_objects_home.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pyreadstat

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from chart_style import sort_groups  # noqa: E402

SAV = "data/pew-atp-w162-2025/ATP W162.sav"

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
    11.0: "Something else",
    12.0: "Nothing in particular",
}
VALID_CODES = {1.0, 2.0}
YES_CODE = {1.0}
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(
        SAV, usecols=["RELIG_W162", "RELART_W162", "WEIGHT_W162"]
    )
    weight = df["WEIGHT_W162"].to_numpy()
    relig = df["RELIG_W162"].to_numpy()
    relart = df["RELART_W162"].to_numpy()

    results = {}
    for code, label in RELIG_CODES.items():
        group_mask = relig == code
        valid = group_mask & np.isin(relart, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        yes = valid & np.isin(relart, list(YES_CODE))
        results[label] = {
            "pct": round(100 * weight[yes].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(relart, list(VALID_CODES))
    yes_all = valid_all & np.isin(relart, list(YES_CODE))
    results["All U.S. adults"] = {
        "pct": round(100 * weight[yes_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }

    order = sort_groups(list(results.keys()), lambda label: results[label]["pct"])

    out = {
        "source": "Pew Research Center. American Trends Panel Wave 162, fielded February 3-9, 2025.",
        "method": "Population is respondent's present religion (RELIG_W162; this wave has no "
                  "F_RELTRAD frame variable). Share who have religious objects or artwork "
                  "displayed in their home, e.g. a cross, crucifix, or pictures of Jesus or "
                  "the saints (RELART_W162); don't know/refused excluded from each row's "
                  "denominator. Groups under 30 valid respondents omitted. Weighted by the "
                  "dataset's own WEIGHT_W162 variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "religious_objects_at_home": results,
    }
    with open(
        "docs/datasets/pew-atp-w162-2025/religious-objects-home.json", "w", encoding="utf-8"
    ) as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:24} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-atp-w162-2025/religious-objects-home.json")


if __name__ == "__main__":
    main()

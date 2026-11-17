"""
Holiday-calendar-driven batch for ATP Wave 162 (Feb. 2025): conflict
between one's own religious beliefs and mainstream American culture
(RELIGCONFLICT_W162 - hook: International Day of Peace, Sept 21 2026),
and devotion to the Virgin Mary or a favorite saint (PRACTICEA_SAINTS_W162
- hook: Feast of St. Francis of Assisi Oct 4 2026 / Our Lady of Guadalupe
Dec 12 2026). Group variable is RELIG_W162 (this wave's own backcoded
religion item) - this wave carries no F_RELTRAD/F_RELIG frame variable
either, same situation as pew-atp-w143-2024 (see that wave's
religious_minority.py docstring).

Usage: python scripts/pew-atp-w162-2025/holiday_batch.py
"""
import json

import numpy as np
import pyreadstat

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
    11.0: "Other",
    12.0: "Nothing in particular",
}
MIN_VALID_N = 30


def binary_by_group(col, weight, relig, hit_codes, valid_codes):
    results = {}
    for code, label in RELIG_CODES.items():
        group_mask = relig == code
        valid = group_mask & np.isin(col, list(valid_codes))
        if valid.sum() < MIN_VALID_N:
            continue
        hit = valid & np.isin(col, list(hit_codes))
        results[label] = {
            "pct": round(100 * weight[hit].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }
    valid_all = np.isin(col, list(valid_codes))
    hit_all = valid_all & np.isin(col, list(hit_codes))
    results["U.S. adults"] = {
        "pct": round(100 * weight[hit_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(col)),
    }
    return results


def main():
    cols = ["RELIG_W162", "RELIGCONFLICT_W162", "PRACTICEA_SAINTS_W162", "WEIGHT_W162"]
    df, _ = pyreadstat.read_sav(SAV, usecols=cols)
    weight = df["WEIGHT_W162"].to_numpy()
    relig = df["RELIG_W162"].to_numpy()

    conflict = binary_by_group(
        df["RELIGCONFLICT_W162"].to_numpy(), weight, relig, {1.0, 2.0}, {1.0, 2.0, 3.0, 4.0})
    saints = binary_by_group(
        df["PRACTICEA_SAINTS_W162"].to_numpy(), weight, relig, {1.0, 2.0}, {1.0, 2.0, 3.0, 4.0, 5.0})

    out = {
        "source": "Pew Research Center. American Trends Panel Wave 162, fielded Feb. 3-9, 2025.",
        "method": "Population is all respondents, grouped by religious affiliation (RELIG_W162, "
                  "this wave's own backcoded item - no F_RELTRAD/F_RELIG frame variable on this "
                  "wave). RELIGCONFLICT: a great deal + some conflict (top two box); refused "
                  "excluded. PRACTICEA_SAINTS: daily + weekly (top two box); refused excluded. "
                  "Groups under 30 valid respondents omitted. Weighted by the dataset's own "
                  "WEIGHT_W162 variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "religion_culture_conflict": conflict,
        "devotion_to_saints_weekly_plus": saints,
    }
    with open("docs/datasets/pew-atp-w162-2025/holiday-batch.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("Wrote docs/datasets/pew-atp-w162-2025/holiday-batch.json")


if __name__ == "__main__":
    main()

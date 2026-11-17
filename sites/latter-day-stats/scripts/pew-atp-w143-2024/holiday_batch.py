"""
Holiday-calendar-driven batch for ATP Wave 143 (Feb. 2024): fasting for
holy times and lighting candles/incense for spiritual reasons
(PRACTICE_FAST_W143/PRACTICE_CNDL_W143 - hooks: Yom Kippur/Sukkot Sept-Oct
2026, Hanukkah Dec 2026), plus perceived discrimination against Muslims and
Jewish Americans (DISCRRIM_MUS_W143/DISCRRIM_JEW_W143 - hooks: Patriot
Day/9-11 Sept 11 2026, International Holocaust Remembrance Day Jan 27
2027). Same F_RELIG group set and by-group construction as
religious_minority.py in this folder - see that file's own docstring for
why F_RELIG (not F_RELTRAD) is this wave's group variable.

Usage: python scripts/pew-atp-w143-2024/holiday_batch.py
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
MIN_VALID_N = 30
VALID = {1.0, 2.0}
YES = 1.0
DISCRIM_VALID = {1.0, 2.0, 3.0, 4.0}
DISCRIM_A_LOT = 1.0


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
    cols = ["F_RELIG", "PRACTICE_FAST_W143", "PRACTICE_CNDL_W143",
            "DISCRRIM_MUS_W143", "DISCRRIM_JEW_W143", "WEIGHT_W143"]
    df, _ = pyreadstat.read_sav(SAV, usecols=cols)
    weight = df["WEIGHT_W143"].to_numpy()
    relig = df["F_RELIG"].to_numpy()

    fast = binary_by_group(df["PRACTICE_FAST_W143"].to_numpy(), weight, relig, {YES}, VALID)
    cndl = binary_by_group(df["PRACTICE_CNDL_W143"].to_numpy(), weight, relig, {YES}, VALID)
    discrim_mus = binary_by_group(df["DISCRRIM_MUS_W143"].to_numpy(), weight, relig,
                                   {DISCRIM_A_LOT}, DISCRIM_VALID)
    discrim_jew = binary_by_group(df["DISCRRIM_JEW_W143"].to_numpy(), weight, relig,
                                   {DISCRIM_A_LOT}, DISCRIM_VALID)

    out = {
        "source": "Pew Research Center. American Trends Panel Wave 143, fielded Feb. 13-25, 2024.",
        "method": "Population is all respondents, grouped by religious affiliation (F_RELIG). "
                  "Fasting/candle items: share answering \"yes, I do\"; refused excluded. "
                  "Discrimination items: share saying groups face \"a lot\" of discrimination "
                  "today; refused excluded. Groups under 30 valid respondents omitted. Weighted "
                  "by the dataset's own WEIGHT_W143 variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "fasts_for_holy_times": fast,
        "lights_candles_incense": cndl,
        "discrimination_against_muslims": discrim_mus,
        "discrimination_against_jews": discrim_jew,
    }
    with open("docs/datasets/pew-atp-w143-2024/holiday-batch.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("Wrote docs/datasets/pew-atp-w143-2024/holiday-batch.json")


if __name__ == "__main__":
    main()

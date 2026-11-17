"""
Second holiday-calendar-driven batch for ATP Wave 143 (Feb. 2024): views
on a president's religious beliefs (PRES1_STRREL_W143/PRES1_SAMEREL_W143 -
hook: Joseph Smith's 1844 presidential run, anniversary Jan 29 2027), and
two afterlife/spiritual-belief items (AFTDTH_W143 top box, BELIEVE_SPRT_W143
- hooks: Halloween Oct 31 2026). Same F_RELIG group set and by-group
construction as religious_minority.py / holiday_batch.py in this folder.

Usage: python scripts/pew-atp-w143-2024/holiday_batch_2.py
"""
import json

import numpy as np
import pyreadstat

from holiday_batch import RELIG_CODES, MIN_VALID_N, binary_by_group

SAV = "data/pew-atp-w143-2024/ATP W143.sav"


def main():
    cols = ["F_RELIG", "PRES1_STRREL_W143", "PRES1_SAMEREL_W143",
            "AFTDTH_W143", "BELIEVE_SPRT_W143", "WEIGHT_W143"]
    df, _ = pyreadstat.read_sav(SAV, usecols=cols)
    weight = df["WEIGHT_W143"].to_numpy()
    relig = df["F_RELIG"].to_numpy()

    pres_strong = binary_by_group(df["PRES1_STRREL_W143"].to_numpy(), weight, relig,
                                   {1.0}, {1.0, 2.0, 3.0, 4.0})
    pres_same = binary_by_group(df["PRES1_SAMEREL_W143"].to_numpy(), weight, relig,
                                 {1.0}, {1.0, 2.0, 3.0, 4.0})
    afterlife = binary_by_group(df["AFTDTH_W143"].to_numpy(), weight, relig,
                                 {1.0}, {1.0, 2.0, 3.0, 4.0})
    ancestor_spirits = binary_by_group(df["BELIEVE_SPRT_W143"].to_numpy(), weight, relig,
                                        {1.0}, {1.0, 2.0})

    out = {
        "source": "Pew Research Center. American Trends Panel Wave 143, fielded Feb. 13-25, 2024.",
        "method": "Population is all respondents, grouped by religious affiliation (F_RELIG). "
                  "PRES1 items: share saying 'very important' (top box). AFTDTH: share saying "
                  "'there is definitely life after death' (top box). BELIEVE_SPRT: share "
                  "answering yes. Refused excluded from each item's own denominator. Groups "
                  "under 30 valid respondents omitted. Weighted by WEIGHT_W143.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "president_strong_beliefs_important": pres_strong,
        "president_same_beliefs_important": pres_same,
        "definitely_life_after_death": afterlife,
        "believe_ancestor_spirits": ancestor_spirits,
    }
    with open("docs/datasets/pew-atp-w143-2024/holiday-batch-2.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("Wrote docs/datasets/pew-atp-w143-2024/holiday-batch-2.json")


if __name__ == "__main__":
    main()

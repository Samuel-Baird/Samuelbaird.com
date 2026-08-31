"""
Third holiday-calendar-driven batch for ATP Wave 143 (Feb. 2024):
discrimination perceived against Black Americans (DISCRRIM_BLACK_W143 -
hook: Black History Month, Feb 2027), and wearing religious items/symbols
(PRACTICE_WEAR_W143 - hook: Ramadan begins, Feb 8 2027). Same F_RELIG
group set and by-group construction as holiday_batch.py in this folder.

Usage: python scripts/pew-atp-w143-2024/holiday_batch_3.py
"""
import json

import pyreadstat

from holiday_batch import binary_by_group

SAV = "data/pew-atp-w143-2024/ATP W143.sav"


def main():
    cols = ["F_RELIG", "DISCRRIM_BLACK_W143", "PRACTICE_WEAR_W143", "WEIGHT_W143"]
    df, _ = pyreadstat.read_sav(SAV, usecols=cols)
    weight = df["WEIGHT_W143"].to_numpy()
    relig = df["F_RELIG"].to_numpy()

    discrim_black = binary_by_group(df["DISCRRIM_BLACK_W143"].to_numpy(), weight, relig,
                                     {1.0}, {1.0, 2.0, 3.0, 4.0})
    wears_religious_items = binary_by_group(df["PRACTICE_WEAR_W143"].to_numpy(), weight, relig,
                                             {1.0}, {1.0, 2.0})

    out = {
        "source": "Pew Research Center. American Trends Panel Wave 143, fielded Feb. 13-25, 2024.",
        "method": "Population is all respondents, grouped by religious affiliation (F_RELIG). "
                  "Discrimination item: share saying Black people face 'a lot' of discrimination "
                  "today; refused excluded. Practice item: share answering 'yes, I do' to wearing "
                  "or carrying religious items/symbols; refused excluded. Groups under 30 valid "
                  "respondents omitted. Weighted by WEIGHT_W143.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "discrimination_against_black_americans": discrim_black,
        "wears_religious_items": wears_religious_items,
    }
    with open("docs/datasets/pew-atp-w143-2024/holiday-batch-3.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("Wrote docs/datasets/pew-atp-w143-2024/holiday-batch-3.json")


if __name__ == "__main__":
    main()

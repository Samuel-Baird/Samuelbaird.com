"""
Fourth batch for ATP Wave 143 (Feb. 2024): belief in reincarnation
(BELIEVE_REIN_W143) and consulting a fortune teller/horoscope/other way to
see the future (PRACTICE_FUTR_W143). Same F_RELIG group set and by-group
construction as holiday_batch.py in this folder.

Usage: python scripts/pew-atp-w143-2024/holiday_batch_4.py
"""
import json

import pyreadstat

from holiday_batch import binary_by_group

SAV = "data/pew-atp-w143-2024/ATP W143.sav"


def main():
    cols = ["F_RELIG", "BELIEVE_REIN_W143", "PRACTICE_FUTR_W143", "WEIGHT_W143"]
    df, _ = pyreadstat.read_sav(SAV, usecols=cols)
    weight = df["WEIGHT_W143"].to_numpy()
    relig = df["F_RELIG"].to_numpy()

    believe_reincarnation = binary_by_group(
        df["BELIEVE_REIN_W143"].to_numpy(), weight, relig, {1.0}, {1.0, 2.0}
    )
    consults_fortune_teller = binary_by_group(
        df["PRACTICE_FUTR_W143"].to_numpy(), weight, relig, {1.0}, {1.0, 2.0}
    )

    out = {
        "source": "Pew Research Center. American Trends Panel Wave 143, fielded Feb. 13-25, 2024.",
        "method": "Population is all respondents, grouped by religious affiliation (F_RELIG). "
                  "Reincarnation item: share answering 'yes, I believe' that people will be "
                  "reborn in this world again and again; refused excluded. Fortune-teller item: "
                  "share answering 'yes, I do' to consulting a fortune teller, horoscope, or "
                  "other way to see the future; refused excluded. Groups under 30 valid "
                  "respondents omitted. Weighted by WEIGHT_W143.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "believes_in_reincarnation": believe_reincarnation,
        "consults_fortune_teller": consults_fortune_teller,
    }
    with open("docs/datasets/pew-atp-w143-2024/holiday-batch-4.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("Wrote docs/datasets/pew-atp-w143-2024/holiday-batch-4.json")


if __name__ == "__main__":
    main()

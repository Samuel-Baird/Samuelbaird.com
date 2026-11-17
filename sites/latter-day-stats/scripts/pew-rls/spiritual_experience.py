"""
Computes the "spiritual experience" numbers for the Data Explorer's Pew RLS
graphics - GRAPHICS_TODO.md's "Spiritual experience" section: thinking
about life's meaning/purpose, feeling spiritual peace, and feeling the
presence of something beyond this world, all weekly+ (each item's own
"At least once a week" top category).

Population: Christian, per the section's own header ("Christian, unless
noted") - the six Christian CURREL groups + a weighted Christian average,
same set as every other Christian-only chart on this page.

Usage: python scripts/pew-rls/spiritual_experience.py
"""
import json

import numpy as np
import pandas as pd

CSV = "data/pew-rls-2023-24/2023-24 RLS Public Use File Feb 19.csv"

CHRISTIAN_CODES = {
    "1000": "Protestant",
    "10000": "Catholic",
    "20000": "Latter-day Saint",
    "30000": "Orthodox Christian",
    "40001": "Jehovah's Witness",
    "40002": "Other Christian",
}
DK = "99"
WEEKLY_PLUS = "1"

REPWT_COLS = [f"REPWT_{i:03d}" for i in range(1, 501)]
USECOLS = ["CURREL", "EXP_G", "EXP_A", "EXP_D", "WEIGHT", *REPWT_COLS]


def group_masks(currel: np.ndarray) -> dict[str, np.ndarray]:
    masks = {label: (currel == code) for code, label in CHRISTIAN_CODES.items()}
    masks["Christian average"] = np.isin(currel, list(CHRISTIAN_CODES.keys()))
    return masks


def binary_share(col: np.ndarray, weight: np.ndarray, group_mask: np.ndarray) -> dict:
    valid = group_mask & (col != DK)
    hit = valid & (col == WEEKLY_PLUS)
    return {
        "pct": round(100 * weight[hit].sum() / weight[valid].sum(), 2),
        "valid_unweighted_n": int(valid.sum()),
        "group_unweighted_n": int(group_mask.sum()),
    }


def main():
    print("Loading CSV (this takes a bit - 502 columns, 36,908 rows)...")
    dtypes = {c: str for c in ["CURREL", "EXP_G", "EXP_A", "EXP_D"]}
    df = pd.read_csv(CSV, usecols=USECOLS, dtype=dtypes)
    weight = df["WEIGHT"].to_numpy()
    currel = df["CURREL"].to_numpy()
    masks = group_masks(currel)

    meaning_results = {label: binary_share(df["EXP_G"].to_numpy(), weight, mask)
                        for label, mask in masks.items()}
    peace_results = {label: binary_share(df["EXP_A"].to_numpy(), weight, mask)
                      for label, mask in masks.items()}
    presence_results = {label: binary_share(df["EXP_D"].to_numpy(), weight, mask)
                         for label, mask in masks.items()}

    out = {
        "source": "Pew Research Center. 2025. “2023-24 Religious Landscape Study "
                   "(RLS) Dataset.” doi: 10.58094/3kwb-bf52.",
        "method": "Population: Christian (six CURREL groups + a weighted Christian average), "
                  "per this section's own header. Weekly+ is each item's own \"at least once a "
                  "week\" top category; don't know/refused excluded from each item's own "
                  "denominator.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "meaning_purpose_weekly_plus": meaning_results,
        "spiritual_peace_weekly_plus": peace_results,
        "presence_beyond_weekly_plus": presence_results,
    }
    with open("docs/datasets/pew-rls-2023-24/spiritual-experience.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    def show(label, results):
        print(f"\n=== {label} ===")
        for group, r in results.items():
            print(f"{group:20} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")

    show("Think about meaning/purpose of life, weekly+ (EXP_G)", meaning_results)
    show("Feel spiritual peace and well-being, weekly+ (EXP_A)", peace_results)
    show("Feel presence of something beyond this world, weekly+ (EXP_D)", presence_results)

    print("\nWrote docs/datasets/pew-rls-2023-24/spiritual-experience.json")


if __name__ == "__main__":
    main()

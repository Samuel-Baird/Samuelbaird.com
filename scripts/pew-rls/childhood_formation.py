"""
Computes the "childhood formation" numbers for the Data Explorer's Pew RLS
graphics: church attendance, family religious importance, and religious
education received - all describing the respondent's own childhood, per
GRAPHICS_TODO.md's "Childhood formation" section.

Population, per that item's own note: **people raised Christian** - the six
FRMREL groups switching_rates.py already uses (Protestant combined, per
that script's FRMREL2-is-restricted-use note), not the respondent's current
tradition. A weighted "Christian average" pools all six groups' totals.

Each item excludes DON'T KNOW/REFUSED (value 99) from its own denominator -
the base for a given item is "people in this FRMREL group who gave a valid
answer to this item," not "everyone in this FRMREL group." The three items
have independent missingness, so each gets its own valid-response base
rather than sharing one across all three.

Usage: python scripts/pew-rls/childhood_formation.py
"""
import json

import numpy as np
import pandas as pd

CSV = "data/pew-rls-2023-24/2023-24 RLS Public Use File Feb 19.csv"

GROUPS = {
    "1000": "Protestant",
    "10000": "Catholic",
    "20000": "Latter-day Saint",
    "30000": "Orthodox Christian",
    "40001": "Jehovah's Witness",
    "40002": "Other Christian",
}

# CHATTEND: "monthly or more" = the first three categories (More than once
# a week / Once a week / Once or twice a month), per the TODO item's note.
CHATTEND_MONTHLY_PLUS = {"1", "2", "3"}
CHATTEND_DK = "99"

CHIMPREL_VERY_IMPORTANT = "1"
CHIMPREL_DK = "99"

CHEDU2_LABELS = {"1": "None", "2": "1-3 years", "3": "4-6 years", "4": "7 years or more"}
CHEDU2_ORDER = ["None", "1-3 years", "4-6 years", "7 years or more"]
CHEDU2_DK = "99"

REPWT_COLS = [f"REPWT_{i:03d}" for i in range(1, 501)]
USECOLS = ["FRMREL", "CHATTEND", "CHIMPREL_B", "CHEDU2", "WEIGHT", *REPWT_COLS]


def group_masks(frmrel: np.ndarray) -> dict[str, np.ndarray]:
    """One boolean mask per label, plus a pooled 'Christian average' mask."""
    masks = {label: (frmrel == code) for code, label in GROUPS.items()}
    masks["Christian average"] = np.isin(frmrel, list(GROUPS.keys()))
    return masks


def binary_share(col: np.ndarray, weight: np.ndarray, group_mask: np.ndarray,
                  hit_codes: set[str], dk_code: str) -> dict:
    """% of GROUP_MASK's valid (non-DK) respondents whose item is in hit_codes."""
    valid = group_mask & (col != dk_code)
    hit = valid & np.isin(col, list(hit_codes))
    base_w = weight[valid].sum()
    return {
        "pct": round(100 * weight[hit].sum() / base_w, 2),
        "valid_unweighted_n": int(valid.sum()),
        "group_unweighted_n": int(group_mask.sum()),
    }


def distribution(col: np.ndarray, weight: np.ndarray, group_mask: np.ndarray,
                  labels: dict[str, str], order: list[str], dk_code: str) -> dict:
    """Full-distribution shares (sum to 100) among GROUP_MASK's valid respondents."""
    valid = group_mask & (col != dk_code)
    base_w = weight[valid].sum()
    shares = {}
    for code, label in labels.items():
        w = weight[valid & (col == code)].sum()
        shares[label] = round(100 * w / base_w, 2)
    return {
        "shares_pct": {label: shares[label] for label in order},
        "valid_unweighted_n": int(valid.sum()),
        "group_unweighted_n": int(group_mask.sum()),
    }


def main():
    print("Loading CSV (this takes a bit - 502 columns, 36,908 rows)...")
    df = pd.read_csv(
        CSV, usecols=USECOLS,
        dtype={"FRMREL": str, "CHATTEND": str, "CHIMPREL_B": str, "CHEDU2": str},
    )
    weight = df["WEIGHT"].to_numpy()
    frmrel = df["FRMREL"].to_numpy()
    chattend = df["CHATTEND"].to_numpy()
    chimprel = df["CHIMPREL_B"].to_numpy()
    chedu2 = df["CHEDU2"].to_numpy()

    masks = group_masks(frmrel)

    attend_results = {
        label: binary_share(chattend, weight, mask, CHATTEND_MONTHLY_PLUS, CHATTEND_DK)
        for label, mask in masks.items()
    }
    importance_results = {
        label: binary_share(chimprel, weight, mask, {CHIMPREL_VERY_IMPORTANT}, CHIMPREL_DK)
        for label, mask in masks.items()
    }
    education_results = {
        label: distribution(chedu2, weight, mask, CHEDU2_LABELS, CHEDU2_ORDER, CHEDU2_DK)
        for label, mask in masks.items()
    }

    out = {
        "source": "Pew Research Center. 2025. “2023-24 Religious Landscape Study "
                   "(RLS) Dataset.” doi: 10.58094/3kwb-bf52.",
        "method": "Population: respondents raised in one of six Christian FRMREL groups "
                  "(Protestant combined, per switching_rates.py's own FRMREL2-restricted-use "
                  "note), weighted by WEIGHT. 'Christian average' pools weighted totals across "
                  "all six before taking ratios, not an unweighted mean of the six percentages. "
                  "Each item's own DON'T KNOW/REFUSED (99) respondents are excluded from that "
                  "item's own denominator only.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "chattend_monthly_plus": attend_results,
        "chimprel_very_important": importance_results,
        "chedu2_distribution": education_results,
        "chedu2_order": CHEDU2_ORDER,
    }
    with open("docs/datasets/pew-rls-2023-24/childhood-formation.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print("\n=== Grew up attending church monthly+ (CHATTEND 1-3) ===")
    for label, r in attend_results.items():
        print(f"{label:20} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")

    print("\n=== Religion very important to family growing up (CHIMPREL_B=1) ===")
    for label, r in importance_results.items():
        print(f"{label:20} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")

    print("\n=== Religious education received (CHEDU2 distribution) ===")
    for label, r in education_results.items():
        shares = ", ".join(f"{k} {v:.0f}%" for k, v in r["shares_pct"].items())
        print(f"{label:20} {shares}  (n={r['valid_unweighted_n']:>5})")

    print("\nWrote docs/datasets/pew-rls-2023-24/childhood-formation.json")


if __name__ == "__main__":
    main()

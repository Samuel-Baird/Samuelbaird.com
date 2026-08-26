"""
Computes the "family and household" numbers for the Data Explorer's Pew RLS
graphics: share with children under 18 at home, and share who pray or read
scripture with their children - per GRAPHICS_TODO.md's "Family and
household" section.

Population is CURRENT tradition (CURREL), not FRMREL - unlike
childhood_formation.py, these two items ask about the respondent's life
today, not their upbringing.

Two different population rules, per the TODO item's own note:
- CHILDREN (share with kids at home): the six Christian CURREL groups +
  a weighted Christian average, same set as every other Pew RLS chart here.
- KIDACT_A (pray/read scripture with kids): the request explicitly widens
  this one to the six Christian groups + an "other religions" bucket
  (Jewish/Muslim/Buddhist/Hindu/other world religions/other faiths) + a
  religiously-affiliated average across all of those (Christian and
  non-Christian alike, excluding the unaffiliated). It's also **filtered to
  parents only** (CHILDREN=Yes) - the denominator for every group is that
  group's own parents, not everyone in the group, per the RLS readme's own
  filter documentation for this item.

Usage: python scripts/pew-rls/family_household.py
"""
import json

import numpy as np
import pandas as pd

CSV = "data/pew-rls-2023-24/2023-24 RLS Public Use File Feb 19.csv"

CHRISTIAN_GROUPS = {
    "1000": "Protestant",
    "10000": "Catholic",
    "20000": "Latter-day Saint",
    "30000": "Orthodox Christian",
    "40001": "Jehovah's Witness",
    "40002": "Other Christian",
}
OTHER_RELIGION_CODES = ["50000", "60000", "70000", "80000", "90001", "90002"]

CHILDREN_YES = "1"
CHILDREN_DK = "99"
KIDACT_YES = "1"
KIDACT_DK = "99"

REPWT_COLS = [f"REPWT_{i:03d}" for i in range(1, 501)]
USECOLS = ["CURREL", "CHILDREN", "KIDACT_A", "WEIGHT", *REPWT_COLS]


def binary_share(hit_mask: np.ndarray, valid_mask: np.ndarray, weight: np.ndarray) -> dict:
    base_w = weight[valid_mask].sum()
    return {
        "pct": round(100 * weight[hit_mask].sum() / base_w, 2),
        "valid_unweighted_n": int(valid_mask.sum()),
    }


def main():
    print("Loading CSV (this takes a bit - 502 columns, 36,908 rows)...")
    df = pd.read_csv(
        CSV, usecols=USECOLS,
        dtype={"CURREL": str, "CHILDREN": str, "KIDACT_A": str},
    )
    weight = df["WEIGHT"].to_numpy()
    currel = df["CURREL"].to_numpy()
    children = df["CHILDREN"].to_numpy()
    kidact = df["KIDACT_A"].to_numpy()

    # --- CHILDREN: six Christian groups + Christian average ----------------
    children_masks = {label: (currel == code) for code, label in CHRISTIAN_GROUPS.items()}
    children_masks["Christian average"] = np.isin(currel, list(CHRISTIAN_GROUPS.keys()))

    children_results = {}
    for label, group_mask in children_masks.items():
        valid = group_mask & (children != CHILDREN_DK)
        hit = valid & (children == CHILDREN_YES)
        children_results[label] = {
            **binary_share(hit, valid, weight),
            "group_unweighted_n": int(group_mask.sum()),
        }

    # --- KIDACT_A: six Christian groups + "Other religions" + a religiously-
    # --- affiliated average, filtered to parents (CHILDREN=Yes) only -------
    is_parent = children == CHILDREN_YES

    kidact_group_masks = {label: (currel == code) for code, label in CHRISTIAN_GROUPS.items()}
    kidact_group_masks["Other religions"] = np.isin(currel, OTHER_RELIGION_CODES)
    affiliated_codes = list(CHRISTIAN_GROUPS.keys()) + OTHER_RELIGION_CODES
    kidact_group_masks["Religiously affiliated average"] = np.isin(currel, affiliated_codes)

    kidact_results = {}
    for label, group_mask in kidact_group_masks.items():
        parent_mask = group_mask & is_parent
        valid = parent_mask & (kidact != KIDACT_DK)
        hit = valid & (kidact == KIDACT_YES)
        kidact_results[label] = {
            **binary_share(hit, valid, weight),
            "group_unweighted_n": int(group_mask.sum()),
            "parent_unweighted_n": int(parent_mask.sum()),
        }

    out = {
        "source": "Pew Research Center. 2025. “2023-24 Religious Landscape Study "
                   "(RLS) Dataset.” doi: 10.58094/3kwb-bf52.",
        "method": "children_with_kids_at_home: population is each group's CURREL (current "
                  "tradition, not raised-in), weighted by WEIGHT, excluding don't know/refused. "
                  "pray_or_read_scripture_with_kids: same CURREL population but filtered to "
                  "parents only (CHILDREN=Yes) - the denominator is that group's own parents, "
                  "per the RLS readme's documented filter for this item; 'Other religions' pools "
                  "Jewish/Muslim/Buddhist/Hindu/other-world/other-faiths CURREL codes, and "
                  "'Religiously affiliated average' pools all six Christian groups plus Other "
                  "religions (excluding the unaffiliated) before taking the ratio.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "children_with_kids_at_home": children_results,
        "pray_or_read_scripture_with_kids": kidact_results,
    }
    with open("docs/datasets/pew-rls-2023-24/family-household.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print("\n=== Parent/guardian of kids under 18 at home (CHILDREN=Yes) ===")
    for label, r in children_results.items():
        print(f"{label:20} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")

    print("\n=== Of parents, pray/read scripture with their kids (KIDACT_A=Yes) ===")
    for label, r in kidact_results.items():
        print(f"{label:30} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")

    print("\nWrote docs/datasets/pew-rls-2023-24/family-household.json")


if __name__ == "__main__":
    main()

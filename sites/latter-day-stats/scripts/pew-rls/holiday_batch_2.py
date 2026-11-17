"""
Second holiday-calendar-driven batch on the Pew RLS 2023-24 dataset (see
holiday_batch.py's own docstring for the group set/weighting approach,
reused unchanged here). Three items:

- RELMATCH: share whose spouse/partner shares their current religion
  (CURREL) - excludes unmarried/no-partner respondents (RELMATCH is NaN
  for them in the source file). Hook: Valentine's Day, Feb 14 2027.
- RACECMB: share identifying as Asian or Asian-American. Hook: AANHPI
  Heritage Month, May 2027.
- FERTREC: share with 2 or more children ever born. Hook: Mother's/
  Father's Day, May 9/Jun 20 2027.

Usage: python scripts/pew-rls/holiday_batch_2.py
"""
import json

import numpy as np
import pandas as pd

from practice import ALL_RELIGIOUS_CODES

CSV = "data/pew-rls-2023-24/2023-24 RLS Public Use File Feb 19.csv"
DK = "99"

GROUP_CODES = {**ALL_RELIGIOUS_CODES, "100000": "Religiously unaffiliated"}

USECOLS = ["CURREL", "RELMATCH", "RACECMB", "FERTREC", "WEIGHT"]


def masks_all(currel: np.ndarray) -> dict:
    m = {label: (currel == code) for code, label in GROUP_CODES.items()}
    m["All groups average"] = np.isin(currel, list(GROUP_CODES.keys()))
    return m


def binary_share(col, weight, group_mask, hit_codes, valid_codes) -> dict:
    valid = group_mask & np.isin(col, list(valid_codes))
    hit = valid & np.isin(col, list(hit_codes))
    n_valid = int(valid.sum())
    return {
        "pct": round(100 * weight[hit].sum() / weight[valid].sum(), 2) if n_valid else None,
        "valid_unweighted_n": n_valid,
        "group_unweighted_n": int(group_mask.sum()),
    }


def run_binary(col, weight, masks, hit_codes, valid_codes) -> dict:
    return {label: binary_share(col, weight, mask, hit_codes, valid_codes) for label, mask in masks.items()}


def main():
    print("Loading RLS CSV subset...")
    dtypes = {c: str for c in ["CURREL", "RELMATCH", "RACECMB", "FERTREC"]}
    df = pd.read_csv(CSV, usecols=USECOLS, dtype=dtypes)
    weight = df["WEIGHT"].to_numpy()
    currel = df["CURREL"].to_numpy()
    m = masks_all(currel)

    out = {
        "group_order": list(GROUP_CODES.values()) + ["All groups average"],
        "total_n": int(len(df)),
        "same_faith_spouse": run_binary(df["RELMATCH"].to_numpy(), weight, m, {"0"}, {"0", "1"}),
        "asian_or_asian_american": run_binary(df["RACECMB"].to_numpy(), weight, m, {"3"}, {"1", "2", "3", "4", "5"}),
        "two_or_more_children": run_binary(df["FERTREC"].to_numpy(), weight, m, {"2", "3", "4"}, {"0", "1", "2", "3", "4"}),
    }

    out_path = "docs/datasets/pew-rls-2023-24/holiday-batch-2.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()

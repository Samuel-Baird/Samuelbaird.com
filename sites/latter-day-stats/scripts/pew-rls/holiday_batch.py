"""
Computes numbers for a batch of holiday-calendar-driven Data Explorer
graphics on the Pew RLS 2023-24 dataset (see the "highest-leverage builds"
list in the 2026-08-31 chat that scoped this batch). Same
compute-then-render split, weighting, and CURREL group set as
scripts/pew-rls/practice.py - reuses that file's ALL_RELIGIOUS_CODES so
group labels/order stay identical across every RLS chart on the site.

Adds "Religiously unaffiliated" (CURREL 100000) as its own row on every
chart here, since none of these items are Christian-only asks and the
holiday hooks (Labor Day, mental health days, Constitution Day) are all
"how does this compare across the whole population" questions, not
"within Christianity" ones - unlike practice.py's population-scoped items.

Usage: python scripts/pew-rls/holiday_batch.py
"""
import json

import numpy as np
import pandas as pd

from practice import ALL_RELIGIOUS_CODES

CSV = "data/pew-rls-2023-24/2023-24 RLS Public Use File Feb 19.csv"
DK = "99"

GROUP_CODES = {**ALL_RELIGIOUS_CODES, "100000": "Religiously unaffiliated"}

USECOLS = [
    "CURREL", "HAPPY", "EMPLSIT", "HISP", "CHRNAT", "PAR2CHILD", "RELDISP",
    "SCPRY1", "WEIGHT",
]


def masks_all(currel: np.ndarray) -> dict:
    m = {label: (currel == code) for code, label in GROUP_CODES.items()}
    m["All groups average"] = np.isin(currel, list(GROUP_CODES.keys()))
    return m


def binary_share(col, weight, group_mask, hit_codes) -> dict:
    valid = group_mask & (col != DK)
    hit = valid & np.isin(col, list(hit_codes))
    return {
        "pct": round(100 * weight[hit].sum() / weight[valid].sum(), 2),
        "valid_unweighted_n": int(valid.sum()),
        "group_unweighted_n": int(group_mask.sum()),
    }


def run_binary(col, weight, masks, hit_codes) -> dict:
    return {label: binary_share(col, weight, mask, hit_codes) for label, mask in masks.items()}


def main():
    print("Loading RLS CSV subset...")
    dtypes = {c: str for c in
              ["CURREL", "HAPPY", "EMPLSIT", "HISP", "CHRNAT", "PAR2CHILD", "RELDISP", "SCPRY1"]}
    df = pd.read_csv(CSV, usecols=USECOLS, dtype=dtypes)
    weight = df["WEIGHT"].to_numpy()
    currel = df["CURREL"].to_numpy()
    m = masks_all(currel)

    out = {
        "group_order": list(GROUP_CODES.values()) + ["All groups average"],
        "total_n": int(len(df)),
        # Labor Day: not currently working for pay + unable to work + retired,
        # inverted framing dropped - report "works full or part time for pay"
        # as the positive/comparable share instead (closer to a "labor force
        # participation" read than an attitudinal one).
        "works_for_pay": run_binary(df["EMPLSIT"].to_numpy(), weight, m, {"1", "2"}),
        # World Mental Health Day / Suicide Prevention Day
        "very_happy": run_binary(df["HAPPY"].to_numpy(), weight, m, {"1"}),
        # Hispanic Heritage Month
        "hispanic": run_binary(df["HISP"].to_numpy(), weight, m, {"1"}),
        # Constitution Day - favor declaring US a Christian nation (top two box)
        "christian_nation_favor": run_binary(df["CHRNAT"].to_numpy(), weight, m, {"1", "2"}),
        # Family Proclamation anniversary - stay-at-home-parent view (option 1)
        "stay_home_parent_better": run_binary(df["PAR2CHILD"].to_numpy(), weight, m, {"1"}),
        # Human Rights Day / Religious Freedom Day - favor religious symbols on public property
        "religious_symbols_favor": run_binary(df["RELDISP"].to_numpy(), weight, m, {"1", "2"}),
        # Constitution Day - favor teacher-led Jesus-referencing school prayer
        "school_prayer_favor": run_binary(df["SCPRY1"].to_numpy(), weight, m, {"1", "2"}),
    }

    out_path = "docs/datasets/pew-rls-2023-24/holiday-batch.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()

"""
Computes the "switching, generalized" numbers for the Data Explorer's Pew
RLS graphic: a fuller view of the same FRMREL/CURREL cross-tab
switching_rates.py already uses, but composition rather than a single
net-change number.

GRAPHICS_TODO.md's "Switching, generalized" item asks for two things per
tradition, not one:
  1. Of today's members, what share were raised in it (retained-in) vs.
     converted in? (both as % of CURRENT membership, summing to 100%)
  2. Of those raised in it, what share are still in it (stayed) vs. left?
     (both as % of the RAISED cohort, summing to 100%)

The TODO leaves the exact chart form as an open decision between a single
per-tradition stacked bar and a small-multiples pair. This ships the
small-multiples pair: two separate 100%-stacked panels (current-membership
composition, and raised-cohort outcome), because the two questions have
different denominators (current members vs. people raised in the
tradition) and collapsing them into one bar would either hide one
denominator or force a misleading shared axis. The "stayed" segment is the
same weighted headcount in both panels (raised in a tradition AND still in
it today) - just read against two different bases - so the two in-app
figures that read this JSON (src/components/charts/figures/
switching-current-composition-figure.tsx and switching-raised-cohort-
figure.tsx, per docs/CHARTS.md) give it one shared color across both
rather than four unrelated segment colors.

Population: same six-group Christian set as switching_rates.py (Protestant
combined, per that script's own FRMREL2-is-restricted-use note), plus a
weighted Christian-overall average across all six.

Usage: python scripts/pew-rls/switching_generalized.py
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

REPWT_COLS = [f"REPWT_{i:03d}" for i in range(1, 501)]
USECOLS = ["FRMREL", "CURREL", "WEIGHT", *REPWT_COLS]


def composition(stayed_w: float, raised_w: float, current_w: float) -> dict:
    """Both panels' numbers for one group, given weighted totals."""
    return {
        # Panel 1: current-membership composition (sums to 100).
        "retained_in_pct": round(100 * stayed_w / current_w, 2),
        "converted_in_pct": round(100 * (current_w - stayed_w) / current_w, 2),
        # Panel 2: raised-cohort outcome (sums to 100).
        "stayed_pct": round(100 * stayed_w / raised_w, 2),
        "left_pct": round(100 * (raised_w - stayed_w) / raised_w, 2),
    }


def main():
    print("Loading CSV (this takes a bit - 502 columns, 36,908 rows)...")
    df = pd.read_csv(CSV, usecols=USECOLS, dtype={"FRMREL": str, "CURREL": str})
    weight = df["WEIGHT"].to_numpy()
    frmrel, currel = df["FRMREL"].to_numpy(), df["CURREL"].to_numpy()

    results = {}
    for code, label in GROUPS.items():
        raised_w = weight[frmrel == code].sum()
        current_w = weight[currel == code].sum()
        stayed_w = weight[(frmrel == code) & (currel == code)].sum()
        results[label] = {
            **composition(stayed_w, raised_w, current_w),
            "raised_unweighted_n": int((frmrel == code).sum()),
            "current_unweighted_n": int((currel == code).sum()),
            "stayed_unweighted_n": int(((frmrel == code) & (currel == code)).sum()),
        }

    # Weighted Christian-overall average: pool all six groups' weighted
    # totals before taking the ratio, not an average of the six percentages
    # (which would over-weight small groups like Jehovah's Witness).
    codes = list(GROUPS.keys())
    raised_mask = np.isin(frmrel, codes)
    current_mask = np.isin(currel, codes)
    stayed_mask = raised_mask & current_mask & (frmrel == currel)
    raised_w = weight[raised_mask].sum()
    current_w = weight[current_mask].sum()
    stayed_w = weight[stayed_mask].sum()
    results["Christian average"] = {
        **composition(stayed_w, raised_w, current_w),
        "raised_unweighted_n": int(raised_mask.sum()),
        "current_unweighted_n": int(current_mask.sum()),
        "stayed_unweighted_n": int(stayed_mask.sum()),
    }

    out = {
        "source": "Pew Research Center. 2025. “2023-24 Religious Landscape Study "
                   "(RLS) Dataset.” doi: 10.58094/3kwb-bf52.",
        "method": "Two 100%-stacked compositions per tradition from the FRMREL/CURREL "
                  "cross-tab, both weighted by WEIGHT: (1) current membership split into "
                  "retained-in (raised in it, still in it) vs. converted-in, as % of "
                  "CURREL==group; (2) the raised cohort split into stayed vs. left, as % "
                  "of FRMREL==group. The 'Christian average' pools weighted totals across "
                  "all six groups before taking ratios, not an unweighted mean of the six "
                  "percentages. Chart form (small-multiples pair over a single merged bar) "
                  "chosen per this dataset's GRAPHICS_TODO.md.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "switching_generalized": results,
    }
    with open("docs/datasets/pew-rls-2023-24/switching-generalized.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print("\n=== Current-membership composition (retained-in vs. converted-in) ===")
    for label, r in results.items():
        print(f"{label:20} retained-in {r['retained_in_pct']:5.1f}%  "
              f"converted-in {r['converted_in_pct']:5.1f}%  (n={r['current_unweighted_n']:>5})")

    print("\n=== Raised-cohort outcome (stayed vs. left) ===")
    for label, r in results.items():
        print(f"{label:20} stayed {r['stayed_pct']:5.1f}%  "
              f"left {r['left_pct']:5.1f}%  (n={r['raised_unweighted_n']:>5})")

    print("\nWrote docs/datasets/pew-rls-2023-24/switching-generalized.json")


if __name__ == "__main__":
    main()

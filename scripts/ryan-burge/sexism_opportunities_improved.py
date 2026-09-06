"""
Single-item pull-out from voter_ideas_matrices.py's gender-role attitudes
matrix: share agreeing society has made it easier for women to get ahead
and improved their quality of life, by religion (sexism6_2016, VOTER
Survey Panel 2016 wave). Same population/top-two-box convention as that
file's share_matrix() (see its own docstring) - unweighted, matching the
sexism battery's existing convention there. This is the same underlying
number already live inside the "Gender-role attitudes, by religion"
heatmap, pulled into its own single-statement magnitude bar rather than
recomputed with a different method.

Usage: python scripts/ryan-burge/sexism_opportunities_improved.py
"""
import json

import numpy as np
import pyreadstat

from voter_ideas_common import DTA, RELIGION_LABELS

DK = {8, 9}  # Skipped, Not Asked - matches voter_ideas_matrices.py's DK_2
AGREE = {1, 2}  # strongly + somewhat agree (top-two-box)


def main():
    df, _ = pyreadstat.read_dta(
        DTA, usecols=["religpew_2016", "sexism6_2016"], apply_value_formats=False,
    )
    religion = df["religpew_2016"].to_numpy(dtype=float)
    item = df["sexism6_2016"].to_numpy(dtype=float)

    results = {}
    for code, label in RELIGION_LABELS.items():
        group_mask = religion == code
        valid = group_mask & ~np.isin(item, list(DK)) & ~np.isnan(item)
        agree = valid & np.isin(item, list(AGREE))
        base = int(valid.sum())
        results[label] = {
            "pct": round(100 * int(agree.sum()) / base, 2) if base else None,
            "valid_unweighted_n": base,
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = ~np.isin(item, list(DK)) & ~np.isnan(item) & np.isin(religion, list(RELIGION_LABELS.keys()))
    agree_all = valid_all & np.isin(item, list(AGREE))
    base_all = int(valid_all.sum())
    results["All respondents"] = {
        "pct": round(100 * int(agree_all.sum()) / base_all, 2),
        "valid_unweighted_n": base_all,
        "group_unweighted_n": base_all,
    }

    out = {
        "source": "Democracy Fund Voter Study Group / YouGov, VOTER Survey Panel, 2016 wave, "
                  "via Ryan Burge (github.com/ryanburge).",
        "via": "Ryan Burge",
        "method": "Population: religpew_2016, unweighted (matching voter_ideas_matrices.py's "
                  "sexism battery). Share who strongly or somewhat agree (top-two-box) that "
                  "opportunities for women have improved their quality of life; don't know/"
                  "skipped excluded. Orthodox, Muslim, and Hindu excluded as too thin, matching "
                  "voter_ideas_common.py's convention.",
        "total_unweighted_n": int(len(df)),
        "group_order": list(RELIGION_LABELS.values()) + ["All respondents"],
        "opportunities_improved_agree": results,
    }
    with open("docs/datasets/ryan-burge/sexism-opportunities-improved.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in out["group_order"]:
        r = results[label]
        print(f"{label:24} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>4})")
    print("\nWrote docs/datasets/ryan-burge/sexism-opportunities-improved.json")


if __name__ == "__main__":
    main()

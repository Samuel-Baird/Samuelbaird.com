"""
CCES 2016 (Ryan Burge's 33-variable extract, cces2016_small_cces.csv): the
two batteries cces2016_by_religion.py left untouched — 2016 presidential
vote choice (CC16_410a) and gun regulation (CC16_330a/d/e) — by the same
full 12-category `religion` variable, same population and conventions as
that script (see its docstring: all 12 groups shown individually, and
**unweighted** because this file carries no survey weight column — good for
shape/direction, not exact figures).

Vote choice: base is respondents who reported voting for a named
candidate (Trump, Clinton, Johnson, Stein, McMullin, or "Other");
"Didn't vote" (6), "Not sure" (7), skipped/not asked (98/99) and missing
are excluded. Shown as a four-segment distribution: Trump, Clinton,
McMullin, and "Other candidate" (Johnson + Stein + Other combined — each
is under 8% in every group and would not clear the stacked-label floor on
its own). McMullin is kept as his own segment because he is the story: the
independent conservative from Utah drew 14% of Latter-day Saint voters in
this file and under 1% of every other group.

Gun items are support/oppose (1/2); code 8 (not asked/skipped) excluded.
CC16_330b ("prohibit governments from publishing gun owners' names and
addresses") is skipped — its double-negative wording makes "support" hard
to read on a chart.

Usage: python scripts/ryan-burge/cces2016_vote_guns.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))  # run from the repo root, like its siblings
from cces2016_by_religion import (  # noqa: E402
    CSV, GROUP_ORDER, RELIGION_LABELS, SUPPORT, binary_share, group_masks,
)

VOTE_LABELS = {1: "Trump", 2: "Clinton", 8: "McMullin", 3: "Johnson", 4: "Stein", 5: "Other"}
VOTE_ORDER = ["Trump", "Clinton", "McMullin", "Other candidate"]
OTHER_CODES = {3, 4, 5}
GUN_DK = {8}


def vote_distribution(col: np.ndarray, group_mask: np.ndarray) -> dict:
    valid = group_mask & np.isin(col, list(VOTE_LABELS.keys()))
    n_valid = int(valid.sum())
    counts = {
        "Trump": int((valid & (col == 1)).sum()),
        "Clinton": int((valid & (col == 2)).sum()),
        "McMullin": int((valid & (col == 8)).sum()),
        "Other candidate": int((valid & np.isin(col, list(OTHER_CODES))).sum()),
    }
    return {
        "shares_pct": {k: (round(100 * v / n_valid, 2) if n_valid else None) for k, v in counts.items()},
        "valid_n": n_valid,
        "group_n": int(group_mask.sum()),
    }


def main():
    df = pd.read_csv(CSV, usecols=["religion", "vote16", "background", "assaultban", "conceal"])
    religion = df["religion"].to_numpy()
    masks = group_masks(religion)

    vote_results = {l: vote_distribution(df["vote16"].to_numpy(), m) for l, m in masks.items()}
    background_results = {l: binary_share(df["background"].to_numpy(), m, SUPPORT, GUN_DK) for l, m in masks.items()}
    assaultban_results = {l: binary_share(df["assaultban"].to_numpy(), m, SUPPORT, GUN_DK) for l, m in masks.items()}
    conceal_results = {l: binary_share(df["conceal"].to_numpy(), m, SUPPORT, GUN_DK) for l, m in masks.items()}

    out = {
        "source": "Ryan Burge (github.com/ryanburge), CCES 2016 common content extract "
                  "(cces2016_small_cces.csv).",
        "via": "Ryan Burge",
        "method": "Population: all 12 religpew categories individually (not collapsed - see "
                  "cces2016_by_religion.py's docstring for why). Unweighted (this file carries "
                  "no survey weight column) - good for shape/direction, not exact figures. "
                  "Vote choice (CC16_410a): base is respondents naming a candidate; didn't "
                  "vote / not sure / skipped excluded; Johnson, Stein, and 'Other' combined as "
                  "'Other candidate'. Gun items (CC16_330a/d/e) are support/oppose; not "
                  "asked/skipped excluded.",
        "total_n": int(len(df)),
        "vote16_distribution": vote_results,
        "vote16_order": VOTE_ORDER,
        "background_support": background_results,
        "assaultban_support": assaultban_results,
        "conceal_support": conceal_results,
    }
    with open("docs/datasets/ryan-burge/cces2016-vote-guns.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print("=== 2016 presidential vote (voters naming a candidate) ===")
    for group in GROUP_ORDER:
        r = vote_results[group]
        shares = ", ".join(f"{k} {v:.0f}%" for k, v in r["shares_pct"].items())
        print(f"{group:24} {shares}  (n={r['valid_n']:>5})")
    for label, results in [("Background checks, support", background_results),
                           ("Ban assault rifles, support", assaultban_results),
                           ("Easier concealed-carry permits, support", conceal_results)]:
        print(f"\n=== {label} ===")
        for group in GROUP_ORDER:
            r = results[group]
            print(f"{group:24} {r['pct']:5.1f}%  (n={r['valid_n']:>5})")
    print("\nWrote docs/datasets/ryan-burge/cces2016-vote-guns.json")


if __name__ == "__main__":
    main()

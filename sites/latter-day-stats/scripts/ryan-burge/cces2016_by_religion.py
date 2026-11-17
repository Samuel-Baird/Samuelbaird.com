"""
Computes the "CCES 2016 — by religion" numbers for the Data Explorer's
Ryan Burge graphics: four immigration items (select-all), two abortion
items, one same-sex marriage item, and religious attendance (full
distribution) — all by the full 12-category `religion` variable, per
docs/datasets/ryan-burge/GRAPHICS_TODO.md's "CCES 2016" section.

Population: all 12 `religion` categories (Protestant, Catholic, Mormon,
Orthodox, Jewish, Muslim, Buddhist, Hindu, Atheist, Agnostic, Nothing in
particular, Something else) - not just LDS vs. everyone else, per the
item's own note. **Design decision**: shown individually, not collapsed,
even though a few groups are thin (Muslim N=436, Hindu N=299) - the same
call this project already made for Pew RLS's even-thinner "Other world
religions" (n=99); flagged here rather than silently collapsing.

This file has **no survey weight column** (see the file's own codebook) -
every number below is a raw unweighted share, good for shape/direction,
not a number that needs to be exact to the decimal.

Usage: python scripts/ryan-burge/cces2016_by_religion.py
"""
import json

import numpy as np
import pandas as pd

CSV = "data/ryan-burge/tier1-strong/cces2016_small_cces.csv"

RELIGION_LABELS = {
    1: "Protestant", 2: "Catholic", 3: "Mormon", 4: "Orthodox",
    5: "Jewish", 6: "Muslim", 7: "Buddhist", 8: "Hindu",
    9: "Atheist", 10: "Agnostic", 11: "Nothing in particular", 12: "Something else",
}
GROUP_ORDER = [
    "Mormon", "Protestant", "Catholic", "Orthodox", "Jewish", "Muslim",
    "Buddhist", "Hindu", "Atheist", "Agnostic", "Nothing in particular",
    "Something else",
]

SELECTED = 1
NOT_SELECTED = 2
SUPPORT = 1
OPPOSE = 2
FAVOR = 1

ATTEND_LABELS = {
    1: "More than once a week", 2: "Once a week", 3: "Once or twice a month",
    4: "A few times a year", 5: "Seldom", 6: "Never",
}
ATTEND_ORDER = list(ATTEND_LABELS.values())
ATTEND_DK = 7

USECOLS = ["religion", "pathway", "border", "dreamer", "deport",
           "prochoice", "prolife", "gaym", "attend", "union"]

UNION_CURRENTLY = 1


def group_masks(religion: np.ndarray) -> dict[str, np.ndarray]:
    return {label: (religion == code) for code, label in RELIGION_LABELS.items()}


def binary_share(col: np.ndarray, group_mask: np.ndarray, hit_code: int, dk_codes: set[int]) -> dict:
    valid = group_mask & ~np.isin(col, list(dk_codes))
    hit = valid & (col == hit_code)
    n_valid = int(valid.sum())
    return {
        "pct": round(100 * hit.sum() / n_valid, 2) if n_valid else None,
        "valid_n": n_valid,
        "group_n": int(group_mask.sum()),
    }


def distribution(col: np.ndarray, group_mask: np.ndarray, labels: dict[int, str],
                  order: list[str], dk_code: int) -> dict:
    valid = group_mask & (col != dk_code) & np.isin(col, list(labels.keys()))
    n_valid = int(valid.sum())
    shares = {}
    for code, label in labels.items():
        n = int((valid & (col == code)).sum())
        shares[label] = round(100 * n / n_valid, 2) if n_valid else None
    return {
        "shares_pct": {label: shares[label] for label in order},
        "valid_n": n_valid,
        "group_n": int(group_mask.sum()),
    }


def main():
    df = pd.read_csv(CSV, usecols=USECOLS)
    religion = df["religion"].to_numpy()
    masks = group_masks(religion)

    pathway_results = {l: binary_share(df["pathway"].to_numpy(), m, SELECTED, set()) for l, m in masks.items()}
    border_results = {l: binary_share(df["border"].to_numpy(), m, SELECTED, set()) for l, m in masks.items()}
    dreamer_results = {l: binary_share(df["dreamer"].to_numpy(), m, SELECTED, set()) for l, m in masks.items()}
    deport_results = {l: binary_share(df["deport"].to_numpy(), m, SELECTED, set()) for l, m in masks.items()}
    prochoice_results = {l: binary_share(df["prochoice"].to_numpy(), m, SUPPORT, set()) for l, m in masks.items()}
    prolife_results = {l: binary_share(df["prolife"].to_numpy(), m, SUPPORT, set()) for l, m in masks.items()}
    gaym_results = {l: binary_share(df["gaym"].to_numpy(), m, FAVOR, set()) for l, m in masks.items()}
    attend_results = {l: distribution(df["attend"].to_numpy(), m, ATTEND_LABELS, ATTEND_ORDER, ATTEND_DK)
                       for l, m in masks.items()}
    union_results = {l: binary_share(df["union"].to_numpy(), m, UNION_CURRENTLY, set()) for l, m in masks.items()}

    out = {
        "source": "Ryan Burge (github.com/ryanburge), CCES 2016 common content extract "
                   "(cces2016_small_cces.csv).",
        "via": "Ryan Burge",
        "method": "Population: all 12 religpew categories individually (not collapsed - see "
                  "this script's own docstring for why). Unweighted (this file carries no "
                  "survey weight column) - good for shape/direction, not exact figures. "
                  "Immigration items are a select-all battery (CC16_331_1/2/3/7): share is "
                  "'selected' vs. 'not selected'. Abortion items (CC16_332a/f) and same-sex "
                  "marriage (CC16_335) are support/oppose or favor/oppose.",
        "total_n": int(len(df)),
        "pathway_selected": pathway_results,
        "border_selected": border_results,
        "dreamer_selected": dreamer_results,
        "deport_selected": deport_results,
        "prochoice_support": prochoice_results,
        "prolife_support": prolife_results,
        "gaym_favor": gaym_results,
        "attend_distribution": attend_results,
        "attend_order": ATTEND_ORDER,
        "union_currently": union_results,
    }
    with open("docs/datasets/ryan-burge/cces2016-by-religion.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    def show(label, results):
        print(f"\n=== {label} ===")
        for group in GROUP_ORDER:
            r = results[group]
            if "pct" in r:
                print(f"{group:24} {r['pct']:5.1f}%  (n={r['valid_n']:>5})")
            else:
                shares = ", ".join(f"{k} {v:.0f}%" for k, v in r["shares_pct"].items())
                print(f"{group:24} {shares}  (n={r['valid_n']:>5})")

    show("Pathway to legal status (select-all)", pathway_results)
    show("Increase border patrols (select-all)", border_results)
    show("Dreamer legal status (select-all)", dreamer_results)
    show("Identify and deport (select-all)", deport_results)
    show("Always allow abortion, support", prochoice_results)
    show("Make abortion illegal, support", prolife_results)
    show("Favor same-sex marriage", gaym_results)
    show("Attendance distribution", attend_results)
    show("Currently a labor union member", union_results)

    print("\nWrote docs/datasets/ryan-burge/cces2016-by-religion.json")


if __name__ == "__main__":
    main()

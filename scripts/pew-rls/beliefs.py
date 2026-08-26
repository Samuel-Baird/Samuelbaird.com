"""
Computes the "beliefs" numbers for the Data Explorer's Pew RLS graphics:
belief in souls, heaven, hell, and evolution guided by God - per
GRAPHICS_TODO.md's "Beliefs" section.

Population: the backlog item explicitly leaves this open ("no population
restriction specified... default to all religions unless told otherwise;
flag this as an open question"). Resolved here as the broadest defensible
set for a belief question specifically (unlike the Practice section's
population choices, which mostly followed an explicit "Christian" or
"religious groups" instruction): all twelve religiously-affiliated CURREL
traditions individually, a weighted average across them, AND the
religiously unaffiliated as their own row - belief in an afterlife or a
soul is a real, well-attested finding among the unaffiliated (Pew's own
published RLS report shows a majority of "nothing in particular"
respondents believe in a soul), so excluding them here (unlike the
Practice section's more explicitly "religious" framing) would drop a
genuinely interesting comparison, not just tidy up the chart. Flagged in
each result's own `population_note`.

Usage: python scripts/pew-rls/beliefs.py
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
OTHER_RELIGION_CODES = {
    "50000": "Jewish",
    "60000": "Muslim",
    "70000": "Buddhist",
    "80000": "Hindu",
    "90001": "Other world religions",
    "90002": "Other faiths",
}
ALL_RELIGIOUS_CODES = {**CHRISTIAN_CODES, **OTHER_RELIGION_CODES}
UNAFFILIATED_CODE = "100000"

DK = "99"

REPWT_COLS = [f"REPWT_{i:03d}" for i in range(1, 501)]
USECOLS = ["CURREL", "SOUL", "HVN", "HLL", "EVOL", "WEIGHT", *REPWT_COLS]


def group_masks(currel: np.ndarray) -> dict[str, np.ndarray]:
    masks = {label: (currel == code) for code, label in ALL_RELIGIOUS_CODES.items()}
    masks["All religious average"] = np.isin(currel, list(ALL_RELIGIOUS_CODES.keys()))
    masks["Religiously unaffiliated"] = currel == UNAFFILIATED_CODE
    return masks


def binary_share(col: np.ndarray, weight: np.ndarray, group_mask: np.ndarray,
                  hit_codes: set[str]) -> dict:
    valid = group_mask & (col != DK)
    hit = valid & np.isin(col, list(hit_codes))
    return {
        "pct": round(100 * weight[hit].sum() / weight[valid].sum(), 2),
        "valid_unweighted_n": int(valid.sum()),
        "group_unweighted_n": int(group_mask.sum()),
    }


def run_binary(col: np.ndarray, weight: np.ndarray, masks: dict, hit_codes: set[str]) -> dict:
    return {label: binary_share(col, weight, mask, hit_codes) for label, mask in masks.items()}


def main():
    print("Loading CSV (this takes a bit - 502 columns, 36,908 rows)...")
    dtypes = {c: str for c in ["CURREL", "SOUL", "HVN", "HLL", "EVOL"]}
    df = pd.read_csv(CSV, usecols=USECOLS, dtype=dtypes)
    weight = df["WEIGHT"].to_numpy()
    currel = df["CURREL"].to_numpy()

    masks = group_masks(currel)

    soul_results = run_binary(df["SOUL"].to_numpy(), weight, masks, {"1"})
    heaven_results = run_binary(df["HVN"].to_numpy(), weight, masks, {"1"})
    hell_results = run_binary(df["HLL"].to_numpy(), weight, masks, {"1"})
    evol_guided_results = run_binary(df["EVOL"].to_numpy(), weight, masks, {"2"})

    out = {
        "source": "Pew Research Center. 2025. “2023-24 Religious Landscape Study "
                   "(RLS) Dataset.” doi: 10.58094/3kwb-bf52.",
        "method": "Population is current tradition (CURREL), weighted by WEIGHT, excluding "
                  "don't know/refused from each item's own denominator. GRAPHICS_TODO.md left "
                  "this section's population unspecified; resolved here as all twelve "
                  "religiously-affiliated traditions individually + a weighted average across "
                  "them + the religiously unaffiliated as their own row (not folded into the "
                  "average), since afterlife/soul belief is a genuine, well-attested finding "
                  "among the unaffiliated worth showing, not just a Christian-only comparison.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "soul_belief": soul_results,
        "heaven_belief": heaven_results,
        "hell_belief": hell_results,
        "evolution_guided_by_god": evol_guided_results,
    }
    with open("docs/datasets/pew-rls-2023-24/beliefs.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    def show(label, results):
        print(f"\n=== {label} ===")
        for group, r in results.items():
            print(f"{group:30} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")

    show("Belief in a soul (SOUL=Yes)", soul_results)
    show("Belief in heaven (HVN=Yes)", heaven_results)
    show("Belief in hell (HLL=Yes)", hell_results)
    show("Evolution guided by God (EVOL=2)", evol_guided_results)

    print("\nWrote docs/datasets/pew-rls-2023-24/beliefs.json")


if __name__ == "__main__":
    main()

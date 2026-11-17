"""
Computes the "public life and society" numbers for the Data Explorer's Pew
RLS graphics - GRAPHICS_TODO.md's "Public life and society" section, eleven
items. Population defaults to Christian (the section's own header, "Christian,
unless noted") except where an item explicitly widens it:

- HUMNTR_B: Christian + other religions, filtered to GOD=Yes believers only
  (per the RLS readme's own documented filter for this item - HUMNTR_A/B
  are only asked of God-believers).
- RELIMPACT, VOL12_CPS: all religiously affiliated traditions individually
  + an average + the religiously unaffiliated - each item's own note calls
  this "the widest population rule of any item on this list."

One design decision the backlog left open: HUMNTR_B's 5-point scale has no
cutpoint named in the request (unlike BIBIMP's explicit "extremely/very" or
RELIMP's "very/somewhat"). Resolved as top-box ("Completely" alone), same
choice as GRACE and PRAC_A elsewhere in this pipeline when a scale's
cutpoint isn't specified.

Usage: python scripts/pew-rls/public_life.py
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
USECOLS = [
    "CURREL", "OPENIDEN", "CHNG_A", "DIVRACPOP", "DIVRELPOP", "HUMNTR_B",
    "GOD", "RELIMPACT", "RELINST_F", "RELINST_G", "RELINST_E", "SCIMPACT",
    "VOL12_CPS", "WEIGHT", *REPWT_COLS,
]


def christian_masks(currel: np.ndarray) -> dict[str, np.ndarray]:
    masks = {label: (currel == code) for code, label in CHRISTIAN_CODES.items()}
    masks["Christian average"] = np.isin(currel, list(CHRISTIAN_CODES.keys()))
    return masks


def christian_plus_other_masks(currel: np.ndarray) -> dict[str, np.ndarray]:
    masks = {label: (currel == code) for code, label in CHRISTIAN_CODES.items()}
    masks["Other religions"] = np.isin(currel, list(OTHER_RELIGION_CODES.keys()))
    masks["Religiously affiliated average"] = np.isin(currel, list(ALL_RELIGIOUS_CODES.keys()))
    return masks


def widest_masks(currel: np.ndarray) -> dict[str, np.ndarray]:
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
    dtypes = {c: str for c in
               ["CURREL", "OPENIDEN", "CHNG_A", "DIVRACPOP", "DIVRELPOP", "HUMNTR_B",
                "GOD", "RELIMPACT", "RELINST_F", "RELINST_G", "RELINST_E", "SCIMPACT",
                "VOL12_CPS"]}
    df = pd.read_csv(CSV, usecols=USECOLS, dtype=dtypes)
    weight = df["WEIGHT"].to_numpy()
    currel = df["CURREL"].to_numpy()

    christian_m = christian_masks(currel)
    christian_plus_other_m = christian_plus_other_masks(currel)
    widest_m = widest_masks(currel)

    openiden_results = run_binary(df["OPENIDEN"].to_numpy(), weight, christian_m, {"1"})
    chng_a_results = run_binary(df["CHNG_A"].to_numpy(), weight, christian_m, {"1"})
    divracpop_results = run_binary(df["DIVRACPOP"].to_numpy(), weight, christian_m, {"1"})
    divrelpop_results = run_binary(df["DIVRELPOP"].to_numpy(), weight, christian_m, {"1"})

    # HUMNTR_B: Christian + other religions, filtered to GOD=Yes believers.
    god_yes = df["GOD"].to_numpy() == "1"
    humntr_col = df["HUMNTR_B"].to_numpy()
    humntr_results = {}
    for label, group_mask in christian_plus_other_m.items():
        believer_mask = group_mask & god_yes
        valid = believer_mask & (humntr_col != DK)
        hit = valid & (humntr_col == "1")
        humntr_results[label] = {
            "pct": round(100 * weight[hit].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
            "believer_unweighted_n": int(believer_mask.sum()),
        }

    relimpact_results = run_binary(df["RELIMPACT"].to_numpy(), weight, widest_m, {"2"})
    relinst_f_results = run_binary(df["RELINST_F"].to_numpy(), weight, christian_m, {"1"})
    relinst_g_results = run_binary(df["RELINST_G"].to_numpy(), weight, christian_m, {"1"})
    relinst_e_results = run_binary(df["RELINST_E"].to_numpy(), weight, christian_m, {"1"})
    scimpact_results = run_binary(df["SCIMPACT"].to_numpy(), weight, christian_m, {"1"})
    vol12_results = run_binary(df["VOL12_CPS"].to_numpy(), weight, widest_m, {"1"})

    out = {
        "source": "Pew Research Center. 2025. “2023-24 Religious Landscape Study "
                   "(RLS) Dataset.” doi: 10.58094/3kwb-bf52.",
        "method": "Population is current tradition (CURREL), weighted by WEIGHT, excluding "
                  "don't know/refused from each item's own denominator. Defaults to Christian "
                  "(six groups + a weighted average) per this section's own header, except "
                  "HUMNTR_B (Christian + other religions, filtered to GOD=Yes believers only) "
                  "and RELIMPACT/VOL12_CPS (all twelve religiously-affiliated traditions "
                  "individually + an average + the religiously unaffiliated - each item's own "
                  "note calls this the widest population rule in the section).",
        "design_decisions": {
            "HUMNTR_B": "Top box (\"Completely\" alone) - the request named no cutpoint for "
                       "this 5-point scale, so this file defaults to top-box, same as GRACE "
                       "and PRAC_A elsewhere in this pipeline.",
        },
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "openiden_openness_essential": openiden_results,
        "chng_a_immigration_better": chng_a_results,
        "divracpop_strengthens": divracpop_results,
        "divrelpop_strengthens": divrelpop_results,
        "humntr_b_completely": humntr_results,
        "relimpact_more_good": relimpact_results,
        "relinst_f_bring_together": relinst_f_results,
        "relinst_g_help_poor": relinst_g_results,
        "relinst_e_strengthen_morality": relinst_e_results,
        "scimpact_more_harm": scimpact_results,
        "vol12_volunteered": vol12_results,
    }
    with open("docs/datasets/pew-rls-2023-24/public-life.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    def show(label, results):
        print(f"\n=== {label} ===")
        for group, r in results.items():
            print(f"{group:30} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")

    show("America's openness essential (OPENIDEN=1)", openiden_results)
    show("Immigration a change for the better (CHNG_A=1)", chng_a_results)
    show("Racial diversity strengthens society (DIVRACPOP=1)", divracpop_results)
    show("Religious diversity strengthens society (DIVRELPOP=1)", divrelpop_results)
    show("God gave humans duty to protect Earth, Completely (HUMNTR_B=1, God-believers)", humntr_results)
    show("Religion does more good than harm (RELIMPACT=2)", relimpact_results)
    show("Religious orgs bring people together (RELINST_F=Agree)", relinst_f_results)
    show("Religious orgs help the poor and needy (RELINST_G=Agree)", relinst_g_results)
    show("Religious orgs protect/strengthen morality (RELINST_E=Agree)", relinst_e_results)
    show("Science does more harm than good (SCIMPACT=1)", scimpact_results)
    show("Volunteered in past 12 months (VOL12_CPS=Yes)", vol12_results)

    print("\nWrote docs/datasets/pew-rls-2023-24/public-life.json")


if __name__ == "__main__":
    main()

"""
Computes the "practice" numbers for the Data Explorer's Pew RLS graphics -
GRAPHICS_TODO.md's "Practice" section, ten items whose population varies
item to item (the section's own header warning). Three population sets are
used, all keyed on CURREL (current tradition - these ask about the
respondent's life today, not their upbringing):

- CHRISTIAN: the six Christian CURREL groups + a weighted Christian
  average (same set every other current-tradition chart on this page uses).
- CHRISTIAN_PLUS_OTHER: those six + an "Other religions" bucket (Jewish/
  Muslim/Buddhist/Hindu/other-world/other-faiths) + a religiously-affiliated
  average, excluding the unaffiliated - used where the request says
  "Christian + other religions."
- ALL_RELIGIOUS: all twelve religiously-affiliated CURREL groups
  individually (the six Christian ones plus Jewish/Muslim/Buddhist/Hindu/
  other-world/other-faiths, unlumped) + an all-religious average - used
  where the request says "all religions"/"all religious groups," which this
  file reads as *religiously affiliated*, not literally everyone (the
  unaffiliated are excluded here the same way "all religions and
  unaffiliated," used by other backlog items like RELIMPACT, is NOT the
  phrase used for any item in this section - see GRACE, MEMB, PRAY, etc.,
  all just say "all religions").

Each item excludes its own DON'T KNOW/REFUSED (99) from its own
denominator. Four items needed a design decision the backlog flagged
explicitly - resolved here, noted in each result's own `design_decision`
key so the render script's caption can quote it:

- RELIMP: top-two-box (very + somewhat important), matching the site's
  existing "somewhat + strongly agree" convention for cutpoint items.
- PRAY (7 categories): collapsed to four buckets - Daily (several times a
  day + once a day), Weekly (a few times a week + once a week), Monthly or
  less (a few times a month + seldom), Never.
- GRACE: top box (Always) alone, not Always+Often - matching this file's
  other top-box picks (RELIMP is the one top-two-box exception, chosen
  because it mirrors the site's existing agree-scale convention).
- PRAC_A: "at least once a week" alone (the scale's own top category), for
  consistency with PRAC_B/PRAC_C's identical "weekly+" framing.

Usage: python scripts/pew-rls/practice.py
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

DK = "99"

REPWT_COLS = [f"REPWT_{i:03d}" for i in range(1, 501)]
USECOLS = [
    "CURREL", "RELIMP", "BIBIMP", "ATTNDPERRLS", "ATTNDONRLS", "MEMB",
    "PRAY", "PRAC_A", "PRAC_B", "PRAC_C", "GRACE", "WEIGHT", *REPWT_COLS,
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


def all_religious_masks(currel: np.ndarray) -> dict[str, np.ndarray]:
    masks = {label: (currel == code) for code, label in ALL_RELIGIOUS_CODES.items()}
    masks["All religious average"] = np.isin(currel, list(ALL_RELIGIOUS_CODES.keys()))
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


def distribution(col: np.ndarray, weight: np.ndarray, group_mask: np.ndarray,
                  bucket_of: dict[str, str], order: list[str]) -> dict:
    """Full-distribution shares (sum to 100) among GROUP_MASK's valid
    respondents, where `bucket_of` maps each raw code to a bucket label
    (identity mapping for an unbucketed item)."""
    valid = group_mask & (col != DK)
    base_w = weight[valid].sum()
    shares = {label: 0.0 for label in order}
    for code, label in bucket_of.items():
        w = weight[valid & (col == code)].sum()
        shares[label] += w
    shares = {label: round(100 * w / base_w, 2) for label, w in shares.items()}
    return {
        "shares_pct": {label: shares[label] for label in order},
        "valid_unweighted_n": int(valid.sum()),
        "group_unweighted_n": int(group_mask.sum()),
    }


def run_binary(col: np.ndarray, weight: np.ndarray, masks: dict, hit_codes: set[str]) -> dict:
    return {label: binary_share(col, weight, mask, hit_codes) for label, mask in masks.items()}


def run_distribution(col: np.ndarray, weight: np.ndarray, masks: dict,
                      bucket_of: dict[str, str], order: list[str]) -> dict:
    return {label: distribution(col, weight, mask, bucket_of, order) for label, mask in masks.items()}


def main():
    print("Loading CSV (this takes a bit - 502 columns, 36,908 rows)...")
    dtypes = {c: str for c in
               ["CURREL", "RELIMP", "BIBIMP", "ATTNDPERRLS", "ATTNDONRLS", "MEMB",
                "PRAY", "PRAC_A", "PRAC_B", "PRAC_C", "GRACE"]}
    df = pd.read_csv(CSV, usecols=USECOLS, dtype=dtypes)
    weight = df["WEIGHT"].to_numpy()
    currel = df["CURREL"].to_numpy()

    christian_m = christian_masks(currel)
    christian_plus_other_m = christian_plus_other_masks(currel)
    all_religious_m = all_religious_masks(currel)

    # --- RELIMP: top-two-box, Christian + other religions ------------------
    relimp_results = run_binary(df["RELIMP"].to_numpy(), weight, christian_plus_other_m, {"1", "2"})

    # --- BIBIMP: top-two-box (extremely/very), Christian only --------------
    bibimp_results = run_binary(df["BIBIMP"].to_numpy(), weight, christian_m, {"1", "2"})

    # --- ATTNDPERRLS: full 6-category distribution, all religious ----------
    attend_order = ["More than once a week", "Once a week", "Once or twice a month",
                     "A few times a year", "Seldom", "Never"]
    attend_bucket = {"1": attend_order[0], "2": attend_order[1], "3": attend_order[2],
                      "4": attend_order[3], "5": attend_order[4], "6": attend_order[5]}
    attend_results = run_distribution(df["ATTNDPERRLS"].to_numpy(), weight, all_religious_m,
                                       attend_bucket, attend_order)

    # --- Derived: ATTNDPERRLS or ATTNDONRLS monthly+, all religious --------
    attnd_per = df["ATTNDPERRLS"].to_numpy()
    attnd_on = df["ATTNDONRLS"].to_numpy()
    monthly_plus = {"1", "2", "3"}
    either_monthly_plus = np.isin(attnd_per, list(monthly_plus)) | np.isin(attnd_on, list(monthly_plus))
    either_valid = (attnd_per != DK) | (attnd_on != DK)  # valid if at least one item answered
    derived_results = {}
    for label, mask in all_religious_m.items():
        valid = mask & either_valid
        hit = valid & either_monthly_plus
        derived_results[label] = {
            "pct": round(100 * weight[hit].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(mask.sum()),
        }

    # --- MEMB: member of a house of worship, all religious ------------------
    memb_results = run_binary(df["MEMB"].to_numpy(), weight, all_religious_m, {"1"})

    # --- PRAY: bucketed to 4 categories, all religious ----------------------
    pray_order = ["Daily", "Weekly", "Monthly or less", "Never"]
    pray_bucket = {
        "1": "Daily", "2": "Daily",
        "3": "Weekly", "4": "Weekly",
        "5": "Monthly or less", "6": "Monthly or less",
        "7": "Never",
    }
    pray_results = run_distribution(df["PRAY"].to_numpy(), weight, all_religious_m, pray_bucket, pray_order)

    # --- PRAC_B: read scripture outside services, weekly+, all religious ---
    pracb_results = run_binary(df["PRAC_B"].to_numpy(), weight, all_religious_m, {"1"})

    # --- PRAC_C: read other holy texts, weekly+, Christian only ------------
    pracc_results = run_binary(df["PRAC_C"].to_numpy(), weight, christian_m, {"1"})

    # --- GRACE: pray before meals, Always (top box), Christian only --------
    grace_results = run_binary(df["GRACE"].to_numpy(), weight, christian_m, {"1"})

    # --- PRAC_A: prayer/study groups, at least weekly, Christian only ------
    praca_results = run_binary(df["PRAC_A"].to_numpy(), weight, christian_m, {"1"})

    out = {
        "source": "Pew Research Center. 2025. “2023-24 Religious Landscape Study "
                   "(RLS) Dataset.” doi: 10.58094/3kwb-bf52.",
        "method": "Population is current tradition (CURREL), weighted by WEIGHT; each item "
                  "excludes its own don't know/refused (99) from its own denominator. Three "
                  "population sets, per GRAPHICS_TODO.md's own per-item notes: Christian (six "
                  "groups + a weighted Christian average), Christian + other religions (those "
                  "six plus a pooled 'Other religions' bucket and a religiously-affiliated "
                  "average), and all religious groups (all twelve traditions individually plus "
                  "an all-religious average) - the religiously unaffiliated are excluded from "
                  "every population here, since none of this section's items ask for them.",
        "design_decisions": {
            "RELIMP": "Top-two-box (very + somewhat important) - matches the site's existing "
                      "agree-scale convention.",
            "PRAY": "Collapsed from 7 categories to 4: Daily (several times a day + once a "
                   "day), Weekly (a few times a week + once a week), Monthly or less (a few "
                   "times a month + seldom), Never.",
            "GRACE": "Top box (Always) alone, not Always+Often.",
            "PRAC_A": "\"At least once a week\" alone (the scale's own top category), matching "
                     "PRAC_B/PRAC_C's identical weekly+ framing.",
        },
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "relimp_important": relimp_results,
        "bibimp_important": bibimp_results,
        "attend_distribution": attend_results,
        "attend_order": attend_order,
        "attend_monthly_plus_either": derived_results,
        "memb_member": memb_results,
        "pray_distribution": pray_results,
        "pray_order": pray_order,
        "pracb_weekly_plus": pracb_results,
        "pracc_weekly_plus": pracc_results,
        "grace_always": grace_results,
        "praca_weekly_plus": praca_results,
    }
    with open("docs/datasets/pew-rls-2023-24/practice.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    def show(label, results):
        print(f"\n=== {label} ===")
        for group, r in results.items():
            if "pct" in r:
                print(f"{group:30} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
            else:
                shares = ", ".join(f"{k} {v:.0f}%" for k, v in r["shares_pct"].items())
                print(f"{group:30} {shares}  (n={r['valid_unweighted_n']:>5})")

    show("Religion very/somewhat important (RELIMP)", relimp_results)
    show("Bible extremely/very important (BIBIMP)", bibimp_results)
    show("Attendance distribution (ATTNDPERRLS)", attend_results)
    show("Attend in-person and/or online monthly+", derived_results)
    show("Member of a house of worship (MEMB)", memb_results)
    show("Prayer frequency (PRAY, bucketed)", pray_results)
    show("Read scripture outside services, weekly+ (PRAC_B)", pracb_results)
    show("Read other holy texts, weekly+ (PRAC_C)", pracc_results)
    show("Say grace before meals, Always (GRACE)", grace_results)
    show("Prayer/study groups, weekly+ (PRAC_A)", praca_results)

    print("\nWrote docs/datasets/pew-rls-2023-24/practice.json")


if __name__ == "__main__":
    main()

"""
Computes nine heatmap-matrix graphics from
docs/datasets/ryan-burge/VOTER_PANEL_IDEAS.md (ideas 7, 8, 9, 11, 12, 14,
16, 17, 18) - reusing the same religion x target grid shape already
shipped for the feeling-thermometer and issue-importance matrices
(voter_matrices.py).

Each battery is grouped by whichever wave its own variables live in
(2016, 2017, or baseline), per that wave's own religpew_* variable - see
voter_ideas_common.py for the shared group set/thin-group exclusion.

Design notes on cell definitions (documented once here rather than
per-item, since several are cutpoint/framing decisions):

- Sexism battery (7), Muslim-distrust battery (8), issue batteries with a
  4-point agree/disagree scale: top-two-box (strongly+somewhat agree/
  strongly+somewhat support).
- Immigration battery (9): mixes scale types (a 3-point contribution item,
  a binary naturalize item, and four 1-10 sliders) - each cell is its own
  0-100 share/rescaled-mean so every row is independently interpretable;
  the immi_contribution item is an A/B question-wording experiment
  (immi_contribution_a/b_2017) - coalesced into one value per respondent
  since together the two versions cover the whole sample.
- Trade battery (11): the five free_trade_*_2016 items ask about five
  different economic effects (jobs/wages/prices/quality/quantity) where
  "increase" means something different each time (more jobs is positive,
  higher prices is negative) - each row's cell is the share holding the
  *positive*-for-consumers view (more jobs/higher wages/lower prices/
  better quality/more products), so the whole matrix reads on one
  consistent "sees free trade as good for me" scale rather than mixing
  polarities under one raw "% Increase" label.
- Trump-promise battery (12): share who support the promise regardless of
  priority (codes 1-2 of a 5-point support/oppose-by-priority scale).
- Media/orgs/volunteer batteries (14/16/17): all select-all Yes/No -
  straight share answering Yes.
- Pride battery (18): top-two-box (very + somewhat proud).

Usage: python scripts/ryan-burge/voter_ideas_matrices.py
"""
import json

import numpy as np
import pyreadstat

from voter_ideas_common import DTA, EXCLUDED_TOO_THIN, GROUP_ORDER, RELIGION_LABELS

DK_2 = {8, 9}
DK_3 = {8, 98, 99}


def group_masks(religion: np.ndarray) -> dict[str, np.ndarray]:
    return {label: (religion == code) for code, label in RELIGION_LABELS.items()}


def share_matrix(df, religion_col: str, cols_labels: dict[str, str], hit_codes: set[int],
                  dk: set[int]) -> tuple[dict, dict]:
    religion = df[religion_col].to_numpy(dtype=float)
    masks = group_masks(religion)
    matrix = {}
    for label, group_mask in masks.items():
        row = {}
        for col, target_label in cols_labels.items():
            vals = df[col].to_numpy(dtype=float)
            valid = group_mask & ~np.isin(vals, list(dk)) & ~np.isnan(vals)
            hit = valid & np.isin(vals, list(hit_codes))
            base = valid.sum()
            row[target_label] = round(100 * hit.sum() / base, 1) if base else None
        matrix[label] = row
    return matrix, {label: int(mask.sum()) for label, mask in masks.items()}


def mean_matrix_1_10(df, religion_col: str, cols_labels: dict[str, str], dk: set[int]) -> dict:
    religion = df[religion_col].to_numpy(dtype=float)
    masks = group_masks(religion)
    matrix = {}
    for label, group_mask in masks.items():
        row = {}
        for col, target_label in cols_labels.items():
            vals = df[col].to_numpy(dtype=float)
            valid = group_mask & ~np.isin(vals, list(dk)) & ~np.isnan(vals)
            if valid.sum():
                mean_raw = vals[valid].mean()
                row[target_label] = round((mean_raw - 1) / 9 * 100, 1)  # 1-10 -> 0-100
            else:
                row[target_label] = None
        matrix[label] = row
    return matrix


def dump(name: str, out: dict) -> None:
    with open(f"docs/datasets/ryan-burge/{name}.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"wrote docs/datasets/ryan-burge/{name}.json")


def common(wave_note: str) -> dict:
    return {
        "source": "Democracy Fund Voter Study Group / YouGov, VOTER Survey Panel, via Ryan "
                   "Burge (github.com/ryanburge).",
        "via": "Ryan Burge",
        "excluded_too_thin": EXCLUDED_TOO_THIN,
        "group_order": GROUP_ORDER,
        "wave_note": wave_note,
    }


def main():
    # --- Sexism (2016) ------------------------------------------------------
    sexism_cols = {
        "sexism1_2016": "Women should return to traditional roles",
        "sexism2_2016": "Equality demands are really about special favors",
        "sexism3_2016": "Women miss out on jobs due to discrimination",
        "sexism4_2016": "Harassment complaints cause more problems than they solve",
        "sexism5_2016": "Workplace harassment is no longer a real problem",
        "sexism6_2016": "Opportunities for women have improved quality of life",
    }
    df = pyreadstat.read_dta(DTA, usecols=["religpew_2016", *sexism_cols], apply_value_formats=False)[0]
    sexism_matrix, ns = share_matrix(df, "religpew_2016", sexism_cols, {1, 2}, DK_2)
    dump("voter-ideas-sexism", {
        **common("2016 wave (religpew_2016)"),
        "note": "Share who strongly or somewhat agree (top-two-box) with each statement.",
        "target_order": list(sexism_cols.values()), "matrix": sexism_matrix,
    })

    # --- Muslim distrust (2017) ---------------------------------------------
    muslim_cols = {
        "muslim_distrust_mosque_2017": "Increase mosque surveillance",
        "muslim_distrust_airpot_2017": "Target Muslims at airport screening",
        "muslim_distrust_vote_2017": "Deny Muslim citizens the right to vote",
    }
    df = pyreadstat.read_dta(DTA, usecols=["religpew_2017", "weight_2017", *muslim_cols],
                              apply_value_formats=False)[0]
    muslim_matrix, _ = share_matrix(df, "religpew_2017", muslim_cols, {1, 2}, DK_2)
    dump("voter-ideas-muslim-distrust", {
        **common("2017 wave (religpew_2017)"),
        "note": "Share who strongly or somewhat agree (top-two-box) with each Muslim "
               "surveillance/restriction proposal.",
        "target_order": list(muslim_cols.values()), "matrix": muslim_matrix,
    })

    # --- Immigration (2017) --------------------------------------------------
    df = pyreadstat.read_dta(
        DTA, usecols=["religpew_2017", "immi_contribution_a_2017", "immi_contribution_b_2017",
                      "immi_naturalize_2017", "immigrants_economy_2017", "immigrants_crime_2017",
                      "immigrants_culture_2017", "immigrants_security_2017"],
        apply_value_formats=False,
    )[0]
    a = df["immi_contribution_a_2017"].to_numpy(dtype=float)
    b = df["immi_contribution_b_2017"].to_numpy(dtype=float)
    contribution = np.where(~np.isin(a, list(DK_3)) & ~np.isnan(a), a, b)
    df["immi_contribution_2017"] = contribution
    imm_share_cols = {
        "immi_contribution_2017": "Say immigrants mostly make a contribution",
        "immi_naturalize_2017": "Favor a path to citizenship",
    }
    imm_share_matrix, _ = share_matrix(df, "religpew_2017", imm_share_cols, {1}, DK_3)
    imm_slider_cols = {
        "immigrants_economy_2017": "Improve the economy",
        "immigrants_crime_2017": "Reduce crime",
        "immigrants_culture_2017": "Enrich cultural life",
        "immigrants_security_2017": "Improve national security",
    }
    imm_slider_matrix = mean_matrix_1_10(df, "religpew_2017", imm_slider_cols, {998, 999})
    imm_matrix = {label: {**imm_share_matrix[label], **imm_slider_matrix[label]} for label in GROUP_ORDER}
    dump("voter-ideas-immigration", {
        **common("2017 wave (religpew_2017)"),
        "note": "First two rows: share holding the pro-immigrant view. Last four rows: mean "
               "0-100 (rescaled from a 1-10 slider, 100=most positive view of immigrants' "
               "effect). Not a single scale, but every row is independently a 0-100 share of "
               "'positive' sentiment.",
        "target_order": list(imm_share_cols.values()) + list(imm_slider_cols.values()),
        "matrix": imm_matrix,
    })

    # --- Trade (2016) ---------------------------------------------------------
    df = pyreadstat.read_dta(
        DTA, usecols=["religpew_2016", "tradepolicy_2016", "free_trade_1_2016",
                      "free_trade_2_2016", "free_trade_3_2016", "free_trade_4_2016",
                      "free_trade_5_2016"],
        apply_value_formats=False,
    )[0]
    trade_cols_hits = {
        "tradepolicy_2016": ("Favor increasing trade generally", {1}, DK_3),
        "free_trade_1_2016": ("Free trade agreements mean more jobs", {1}, DK_2),
        "free_trade_2_2016": ("Free trade agreements mean higher wages", {1}, DK_2),
        "free_trade_3_2016": ("Free trade agreements mean lower prices", {2}, DK_2),
        "free_trade_4_2016": ("Free trade agreements mean better product quality", {1}, DK_2),
        "free_trade_5_2016": ("Free trade agreements mean more products available", {1}, DK_2),
    }
    religion = df["religpew_2016"].to_numpy(dtype=float)
    masks = group_masks(religion)
    trade_matrix = {label: {} for label in GROUP_ORDER}
    for col, (target_label, hit_codes, dk) in trade_cols_hits.items():
        vals = df[col].to_numpy(dtype=float)
        for label, group_mask in masks.items():
            valid = group_mask & ~np.isin(vals, list(dk)) & ~np.isnan(vals)
            hit = valid & np.isin(vals, list(hit_codes))
            base = valid.sum()
            trade_matrix[label][target_label] = round(100 * hit.sum() / base, 1) if base else None
    dump("voter-ideas-trade", {
        **common("2016 wave (religpew_2016)"),
        "note": "Each row is the share holding the positive-for-consumers view of that "
               "specific economic effect (more jobs/higher wages/lower prices/better "
               "quality/more products) - not a single 'favor trade' scale, since the five "
               "source items ask about five different effects.",
        "target_order": [v[0] for v in trade_cols_hits.values()], "matrix": trade_matrix,
    })

    # --- Trump promises (2017) -----------------------------------------------
    promise_cols = {
        "promise_wall_2017": "Building a border wall",
        "promise_repeal_aca_2017": "Repealing the ACA (Obamacare)",
        "promise_tpp_2017": "Withdrawing from the TPP trade deal",
        "promise_corruption_2017": "Reducing corruption in government",
    }
    df = pyreadstat.read_dta(DTA, usecols=["religpew_2017", *promise_cols], apply_value_formats=False)[0]
    promise_matrix, _ = share_matrix(df, "religpew_2017", promise_cols, {1, 2}, DK_2)
    dump("voter-ideas-promises", {
        **common("2017 wave (religpew_2017)"),
        "note": "Share who support this Trump promise (regardless of how high a priority "
               "they said it was).",
        "target_order": list(promise_cols.values()), "matrix": promise_matrix,
    })

    # --- Media diet (baseline) ------------------------------------------------
    media_cols = {
        "enews_show_1_baseline": "ABC World News",
        "enews_show_2_baseline": "CBS Evening News",
        "enews_show_3_baseline": "NBC Nightly News",
        "enews_show_4_baseline": "Fox Special Report",
        "enews_show_5_baseline": "PBS NewsHour",
        "enews_show_6_baseline": "CNN",
        "enews_show_7_baseline": "MSNBC",
    }
    df = pyreadstat.read_dta(DTA, usecols=["religpew_baseline", *media_cols], apply_value_formats=False)[0]
    media_matrix, _ = share_matrix(df, "religpew_baseline", media_cols, {1}, DK_2)
    dump("voter-ideas-media", {
        **common("baseline wave (~2011, religpew_baseline)"),
        "note": "Share who watch this evening news program.",
        "target_order": list(media_cols.values()), "matrix": media_matrix,
    })

    # --- Organization membership (baseline) -----------------------------------
    org_labels = {
        1: "Aircraft Owners and Pilots Assoc.", 2: "Alcoholics Anonymous", 3: "AAA",
        4: "American Legion", 5: "ASPCA", 6: "Family Research Council", 7: "Humane Society",
        8: "Lions Clubs", 9: "Mature Outlook", 10: "MADD", 11: "Nat'l Assoc. of Investors",
        12: "National Organization for Women", 13: "NRA", 14: "National Wildlife Federation",
        15: "Nature Conservancy", 16: "PETA", 17: "Rotary International", 18: "Sierra Club",
        19: "United Seniors", 20: "YMCA",
    }
    org_cols = {f"org_membership_{i}_baseline": label for i, label in org_labels.items()}
    df = pyreadstat.read_dta(DTA, usecols=["religpew_baseline", *org_cols], apply_value_formats=False)[0]
    org_matrix, _ = share_matrix(df, "religpew_baseline", org_cols, {1}, DK_2)
    dump("voter-ideas-orgs", {
        **common("baseline wave (~2011, religpew_baseline)"),
        "note": "Share who are a member of this organization.",
        "target_order": list(org_labels.values()), "matrix": org_matrix,
    })

    # --- Volunteering by cause (baseline) --------------------------------------
    vol_labels = {
        1: "Religious organization", 2: "Children's ed./sports/rec.", 3: "Other education",
        4: "Social/community service", 5: "Civic organization", 6: "Cultural or arts",
        7: "Environmental/animal care", 8: "Health research/education",
        9: "Hospital/clinic/healthcare", 10: "Immigrant/refugee assistance",
        11: "International organization", 12: "Labor/business/professional",
        13: "Political party/advocacy", 14: "Public safety", 15: "Sports or hobby group",
        16: "Youth services", 17: "Some other organization",
    }
    vol_cols = {f"volunteerorg2_{i}_baseline": label for i, label in vol_labels.items()}
    df = pyreadstat.read_dta(DTA, usecols=["religpew_baseline", *vol_cols], apply_value_formats=False)[0]
    vol_matrix, _ = share_matrix(df, "religpew_baseline", vol_cols, {1}, DK_2)
    dump("voter-ideas-volunteering", {
        **common("baseline wave (~2011, religpew_baseline)"),
        "note": "Share who volunteered for this type of organization in the past 12 months.",
        "target_order": list(vol_labels.values()), "matrix": vol_matrix,
    })

    # --- National pride (2016) -------------------------------------------------
    pride_cols = {
        "prouddem_2016": "The way democracy works",
        "proudgrp_2016": "Fair and equal treatment of all groups",
        "proudhis_2016": "Its history",
    }
    df = pyreadstat.read_dta(DTA, usecols=["religpew_2016", *pride_cols], apply_value_formats=False)[0]
    pride_matrix, _ = share_matrix(df, "religpew_2016", pride_cols, {1, 2}, DK_3)
    dump("voter-ideas-pride", {
        **common("2016 wave (religpew_2016)"),
        "note": "Share who are very or somewhat proud (top-two-box) of America on this dimension.",
        "target_order": list(pride_cols.values()), "matrix": pride_matrix,
    })

    print("\nAll nine VOTER idea matrices written.")


if __name__ == "__main__":
    main()

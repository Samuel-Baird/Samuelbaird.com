"""
Computes six longitudinal/panel graphics from
docs/datasets/ryan-burge/VOTER_PANEL_IDEAS.md (ideas 1, 2, 3, 5, 20) - the
ideas that lean into what makes this panel genuinely different from every
other dataset this project has used: it's the same respondents,
re-interviewed, not a fresh cross-section each wave.

**Methodology, used consistently across all six**: every respondent's
group is fixed at their `religpew_baseline` (~2011) identity - a "baseline
cohort" - and tracked forward through 2016/2017 regardless of whether they
still identify with that religion later. This is deliberate: it's what a
panel can do that a repeated cross-section (Pew RLS, CCES) can't - show
what happened to the *same* people, not just how the population compares
wave to wave. (Idea 1, religious retention, is the one exception - it
measures the very thing this cohort-fixing would hide, so it instead
computes what share of the baseline cohort *still* identifies with that
religion at each later wave.)

**Wave scope correction**: the actual file only contains baseline (~2011),
2012, 2016, and 2017 - not the 2018-2020 waves idea 3 originally cited
(see voter_ideas_common.py's docstring). Idea 3 is scoped to 2012 -> 2016
here, not 2012 -> 2020.

No survey weight is used for any of these six - `weight_2017` is specific
to the 2017 cross-section and isn't the right weight for a fixed baseline
cohort tracked forward; unweighted shares are shape/direction only, same
caveat this project already carries for the CCES 2016 extract.

Usage: python scripts/ryan-burge/voter_ideas_longitudinal.py
"""
import json

import numpy as np
import pyreadstat

from voter_ideas_common import DTA, EXCLUDED_TOO_THIN, GROUP_ORDER, RELIGION_LABELS

DK_2 = {8, 9}
DK_3 = {8, 98, 99}
WAVE_YEARS = [2011, 2016, 2017]  # baseline fielded 2011; used only as x-axis positions


def cohort_masks(religion_baseline: np.ndarray) -> dict[str, np.ndarray]:
    return {label: (religion_baseline == code) for code, label in RELIGION_LABELS.items()}


def share_over_waves(cohorts: dict, cols: list, hit_codes: set[int], dk: set[int]) -> dict:
    """For each cohort, the share of valid respondents hitting hit_codes at
    each wave in `cols` (aligned to WAVE_YEARS)."""
    out = {}
    for label, mask in cohorts.items():
        series = []
        ns = []
        for col in cols:
            valid = mask & ~np.isin(col, list(dk)) & ~np.isnan(col)
            hit = valid & np.isin(col, list(hit_codes))
            base = valid.sum()
            series.append(round(100 * hit.sum() / base, 2) if base else None)
            ns.append(int(base))
        out[label] = {"values": series, "n": ns}
    return out


def main():
    cols = [
        "religpew_baseline", "religpew_2016", "religpew_2017",
        "pew_religimp_baseline", "pew_religimp_2016", "pew_religimp_2017",
        "pew_prayer_baseline", "pew_prayer_2016", "pew_prayer_2017",
        "trustgovt_baseline", "trustgovt_2016", "trustgovt_2017",
        "post_presvote12_2012", "presvote16post_2016",
        "gaymar2_baseline", "gaymar_2016",
    ]
    df, _ = pyreadstat.read_dta(DTA, usecols=cols, apply_value_formats=False)
    religion_baseline = df["religpew_baseline"].to_numpy(dtype=float)
    cohorts = cohort_masks(religion_baseline)

    def col(name):
        return df[name].to_numpy(dtype=float)

    # --- Idea 1: religious retention -----------------------------------------
    retention = {}
    for code, label in RELIGION_LABELS.items():
        mask = cohorts[label]
        r2016 = col("religpew_2016")
        r2017 = col("religpew_2017")
        valid16 = mask & ~np.isnan(r2016)
        valid17 = mask & ~np.isnan(r2017)
        pct16 = round(100 * (valid16 & (r2016 == code)).sum() / valid16.sum(), 2) if valid16.sum() else None
        pct17 = round(100 * (valid17 & (r2017 == code)).sum() / valid17.sum(), 2) if valid17.sum() else None
        retention[label] = {
            "values": [100.0, pct16, pct17],
            "n": [int(mask.sum()), int(valid16.sum()), int(valid17.sum())],
        }

    # --- Idea 2: religiosity trajectory (baseline cohort tracked forward) ---
    religimp = share_over_waves(
        cohorts, [col("pew_religimp_baseline"), col("pew_religimp_2016"), col("pew_religimp_2017")],
        {1}, DK_2,
    )
    prayer_daily = share_over_waves(
        cohorts, [col("pew_prayer_baseline"), col("pew_prayer_2016"), col("pew_prayer_2017")],
        {1, 2}, DK_3,
    )

    # --- Idea 5: trust in government (baseline cohort tracked forward) ------
    trustgovt = share_over_waves(
        cohorts, [col("trustgovt_baseline"), col("trustgovt_2016"), col("trustgovt_2017")],
        {1, 2}, DK_2,
    )

    # --- Idea 3: Republican presidential vote share, 2012 vs. 2016 ----------
    v2012, v2016 = col("post_presvote12_2012"), col("presvote16post_2016")
    vote_r_share = {}
    for label, mask in cohorts.items():
        valid12 = mask & np.isin(v2012, [1, 2, 3])  # major/minor candidates, excludes non-voters/DK
        valid16 = mask & np.isin(v2016, [1, 2, 3, 4, 5, 6])
        r12 = round(100 * (valid12 & (v2012 == 2)).sum() / valid12.sum(), 2) if valid12.sum() else None
        r16 = round(100 * (valid16 & (v2016 == 2)).sum() / valid16.sum(), 2) if valid16.sum() else None
        vote_r_share[label] = {
            "2012": r12, "2016": r16,
            "n_2012": int(valid12.sum()), "n_2016": int(valid16.sum()),
        }

    # --- Idea 20: gay marriage favor, baseline vs. 2016 ----------------------
    g_base, g_2016 = col("gaymar2_baseline"), col("gaymar_2016")
    gaymar_shift = {}
    for label, mask in cohorts.items():
        valid_b = mask & np.isin(g_base, [1, 2, 3])
        valid_16 = mask & np.isin(g_2016, [1, 2])
        fb = round(100 * (valid_b & (g_base == 1)).sum() / valid_b.sum(), 2) if valid_b.sum() else None
        f16 = round(100 * (valid_16 & (g_2016 == 1)).sum() / valid_16.sum(), 2) if valid_16.sum() else None
        gaymar_shift[label] = {
            "baseline": fb, "2016": f16,
            "n_baseline": int(valid_b.sum()), "n_2016": int(valid_16.sum()),
        }

    out = {
        "source": "Democracy Fund Voter Study Group / YouGov, VOTER Survey Panel, via Ryan "
                   "Burge (github.com/ryanburge).",
        "via": "Ryan Burge",
        "method": "Every respondent's group is fixed at their religpew_baseline (~2011) "
                  "identity - a 'baseline cohort' - tracked forward through 2016/2017 "
                  "regardless of later religious identification, except retention (idea 1), "
                  "which measures identity persistence itself. Unweighted. Excludes the same "
                  "too-thin categories as every other VOTER graphic.",
        "excluded_too_thin": EXCLUDED_TOO_THIN,
        "group_order": GROUP_ORDER,
        "wave_years": WAVE_YEARS,
        "retention": retention,
        "religimp_very_important": religimp,
        "prayer_daily": prayer_daily,
        "trustgovt_top_two": trustgovt,
        "vote_r_share_2012_2016": vote_r_share,
        "gaymar_favor_baseline_2016": gaymar_shift,
    }
    with open("docs/datasets/ryan-burge/voter-ideas-longitudinal.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    def show(label, results, keys=None):
        print(f"\n=== {label} ===")
        for group in GROUP_ORDER:
            r = results[group]
            if keys:
                print(f"{group:24} " + ", ".join(f"{k}={r[k]}" for k in keys))
            else:
                print(f"{group:24} {r['values']}  n={r['n']}")

    show("Religious retention (baseline/2016/2017)", retention)
    show("Very important religion (baseline/2016/2017)", religimp)
    show("Pray daily (baseline/2016/2017)", prayer_daily)
    show("Trust govt most/always (baseline/2016/2017)", trustgovt)
    show("R vote share, 2012 vs 2016", vote_r_share, keys=["2012", "2016"])
    show("Favor gay marriage, baseline vs 2016", gaymar_shift, keys=["baseline", "2016"])

    print("\nWrote docs/datasets/ryan-burge/voter-ideas-longitudinal.json")


if __name__ == "__main__":
    main()

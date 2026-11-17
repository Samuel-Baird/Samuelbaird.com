"""
Computes eight single-value "magnitude bar" graphics from
docs/datasets/ryan-burge/VOTER_PANEL_IDEAS.md, all cross-sectional within
the 2016 wave (grouped by `religpew_2016`, N=133 LDS) since every source
variable here is itself a `_2016`-suffixed item:

- Idea 4: 2016 vote regret - `wished_voted_2016`, `vote_regrets_2016`.
- Idea 6: authoritarian child-rearing values - `SOCIAL_CONFORMITY_3_2016`
  (the classic "obedience vs. self-reliance" proxy), share picking
  self-reliance.
- Idea 10: racial attitudes - `race_slave_2016`, `reverse_discrimination_2016`,
  top-two-box (strongly agree + agree).
- Idea 13: generalized social trust - `trust_people_2016`, share "most
  people can be trusted."
- Idea 15: military household - `milstat_1_2016`-`milstat_4_2016`
  (self/family currently/previously served), a derived "any" flag rather
  than a straight variable read, since it's a select-all battery.
- Idea 19: populist elite-distrust - `RIGGED_SYSTEM_6_2016`, top-two-box.

Same population/exclusion convention as voter_stranger.py and
voter_matrices.py - see voter_ideas_common.py.

Usage: python scripts/ryan-burge/voter_ideas_bars.py
"""
import json

import numpy as np
import pyreadstat

from voter_ideas_common import DTA, EXCLUDED_TOO_THIN, GROUP_ORDER, RELIGION_LABELS

DK_2 = {8, 9}
DK_3 = {8, 98, 99}


def group_masks(religion: np.ndarray) -> dict[str, np.ndarray]:
    return {label: (religion == code) for code, label in RELIGION_LABELS.items()}


def binary_share(col: np.ndarray, group_mask: np.ndarray, hit_codes: set[int], dk: set[int]) -> dict:
    valid = group_mask & ~np.isin(col, list(dk)) & ~np.isnan(col)
    hit = valid & np.isin(col, list(hit_codes))
    base = valid.sum()
    return {
        "pct": round(100 * hit.sum() / base, 2) if base else None,
        "valid_n": int(base),
        "group_n": int(group_mask.sum()),
    }


def run(col: np.ndarray, masks: dict, hit_codes: set[int], dk: set[int]) -> dict:
    return {label: binary_share(col, mask, hit_codes, dk) for label, mask in masks.items()}


def main():
    cols = [
        "religpew_2016", "wished_voted_2016", "vote_regrets_2016",
        "SOCIAL_CONFORMITY_3_2016", "race_slave_2016", "reverse_discrimination_2016",
        "trust_people_2016", "RIGGED_SYSTEM_6_2016",
        "milstat_1_2016", "milstat_2_2016", "milstat_3_2016", "milstat_4_2016",
    ]
    df, _ = pyreadstat.read_dta(DTA, usecols=cols, apply_value_formats=False)
    religion = df["religpew_2016"].to_numpy(dtype=float)
    masks = group_masks(religion)

    def col(name):
        return df[name].to_numpy(dtype=float)

    wished_voted = run(col("wished_voted_2016"), masks, {1}, DK_2)
    vote_regrets = run(col("vote_regrets_2016"), masks, {1}, DK_2)
    self_reliance = run(col("SOCIAL_CONFORMITY_3_2016"), masks, {2}, DK_2)
    race_slave = run(col("race_slave_2016"), masks, {1, 2}, DK_3)
    reverse_discrim = run(col("reverse_discrimination_2016"), masks, {1, 2}, DK_3)
    trust_people = run(col("trust_people_2016"), masks, {2}, {8, 98, 99})
    rigged_elites = run(col("RIGGED_SYSTEM_6_2016"), masks, {1, 2}, DK_2)

    # Military household: derived "any" flag - Yes on any of the four
    # currently/previously-serving items, among respondents who answered
    # at least one of the four (not a straight variable read).
    m1, m2, m3, m4 = col("milstat_1_2016"), col("milstat_2_2016"), col("milstat_3_2016"), col("milstat_4_2016")
    any_answered = (~np.isin(m1, list(DK_2))) | (~np.isin(m2, list(DK_2))) | \
                   (~np.isin(m3, list(DK_2))) | (~np.isin(m4, list(DK_2)))
    any_military = (m1 == 1) | (m2 == 1) | (m3 == 1) | (m4 == 1)
    milstat_results = {}
    for label, group_mask in masks.items():
        valid = group_mask & any_answered
        hit = valid & any_military
        base = valid.sum()
        milstat_results[label] = {
            "pct": round(100 * hit.sum() / base, 2) if base else None,
            "valid_n": int(valid.sum()),
            "group_n": int(group_mask.sum()),
        }

    out = {
        "source": "Democracy Fund Voter Study Group / YouGov, VOTER Survey Panel, 2016 wave, "
                   "via Ryan Burge (github.com/ryanburge).",
        "via": "Ryan Burge",
        "method": "Population: religpew_2016, unweighted (this project's other VOTER graphics "
                  "use weight_2017; the 2016 wave's own case weight was not selected into this "
                  "extract, so these eight are raw shares - good for shape/direction). Excludes "
                  "the same too-thin categories as every other VOTER graphic.",
        "excluded_too_thin": EXCLUDED_TOO_THIN,
        "group_order": GROUP_ORDER,
        "wished_voted": wished_voted,
        "vote_regrets": vote_regrets,
        "self_reliance": self_reliance,
        "race_slave_agree": race_slave,
        "reverse_discrimination_agree": reverse_discrim,
        "trust_people": trust_people,
        "rigged_elites_agree": rigged_elites,
        "military_household": milstat_results,
    }
    with open("docs/datasets/ryan-burge/voter-ideas-bars.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    def show(label, results):
        print(f"\n=== {label} ===")
        for group in GROUP_ORDER:
            r = results[group]
            print(f"{group:24} {r['pct']}%  (n={r['valid_n']})" if r["pct"] is not None
                  else f"{group:24} n/a")

    show("Wished voted 2016", wished_voted)
    show("Regrets 2016 vote", vote_regrets)
    show("Self-reliance (vs. obedience)", self_reliance)
    show("Race/slavery structural-inequality agree", race_slave)
    show("Reverse discrimination agree", reverse_discrim)
    show("Most people can be trusted", trust_people)
    show("Elites don't understand people like me", rigged_elites)
    show("Any military household connection", milstat_results)

    print("\nWrote docs/datasets/ryan-burge/voter-ideas-bars.json")


if __name__ == "__main__":
    main()

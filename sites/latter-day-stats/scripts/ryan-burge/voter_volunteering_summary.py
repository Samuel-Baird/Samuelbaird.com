"""
Computes two summary graphics from the same baseline-wave (~2011)
`volunteerorg2_*_baseline` battery as voter-ideas-volunteering.json's
heatmap (scripts/ryan-burge/voter_ideas_matrices.py) - VOTER Survey Panel:

- Average number of NON-religious causes volunteered for per person: for
  each respondent, the count of "Yes" answers across the 16 non-religious
  categories (volunteerorg2_2 through _17), averaged across everyone in
  the group. A per-person count, not a percentage - so unlike every other
  chart in this pipeline, its value isn't 0-100.
- Share who volunteered for a religious organization specifically
  (volunteerorg2_1_baseline) - the one category the average above
  excludes.

Population/grouping: religpew_baseline, unweighted (this dataset extract
has no baseline-wave weight - see voter_ideas_common.py's docstring and
render_voter_ideas_longitudinal.py's precedent for treating baseline-only
items as unweighted). Narrower group set than voter_ideas_common.py's own
GROUP_ORDER: Agnostic, Nothing in particular, and Something else dropped
per this chart's own request (not this project's usual population - most
VOTER Panel charts keep all three), on top of the standing
Orthodox/Muslim/Hindu too-thin exclusion every other chart in this family
already applies.

All 17 volunteerorg2_*_baseline items are clean Yes(1)/No(2) with no
missing/skip/not-asked codes for any of the 8,000 baseline respondents
(verified directly against the .dta) - so there's no denominator-exclusion
step needed here, unlike most other items in this pipeline.

Usage: python scripts/ryan-burge/voter_volunteering_summary.py
"""
import json

import numpy as np
import pyreadstat

from voter_ideas_common import DTA, EXCLUDED_TOO_THIN, RELIGION_LABELS

GROUP_ORDER = ["Mormon", "Protestant", "Catholic", "Jewish", "Buddhist", "Atheist"]

RELIGIOUS_ORG_COL = "volunteerorg2_1_baseline"
NONRELIGIOUS_COLS = [f"volunteerorg2_{i}_baseline" for i in range(2, 18)]


def main():
    cols = ["religpew_baseline", RELIGIOUS_ORG_COL, *NONRELIGIOUS_COLS]
    df, _ = pyreadstat.read_dta(DTA, usecols=cols, apply_value_formats=False)
    religion = df["religpew_baseline"].to_numpy(dtype=float)

    religious_org = df[RELIGIOUS_ORG_COL].to_numpy(dtype=float)
    nonreligious = df[NONRELIGIOUS_COLS].to_numpy(dtype=float)  # shape (n, 16)
    nonreligious_count = (nonreligious == 1).sum(axis=1)  # per-respondent count, 0-16

    religious_org_pct = {}
    nonreligious_avg = {}
    for code, label in RELIGION_LABELS.items():
        if label not in GROUP_ORDER:
            continue
        group_mask = religion == code
        n = int(group_mask.sum())

        yes = (religious_org == 1) & group_mask
        religious_org_pct[label] = {
            "pct": round(100 * yes.sum() / n, 2) if n else None,
            "valid_n": n,
            "group_n": n,
        }

        nonreligious_avg[label] = {
            "avg_causes": round(float(nonreligious_count[group_mask].mean()), 2) if n else None,
            "valid_n": n,
            "group_n": n,
        }

    out = {
        "source": "Democracy Fund Voter Study Group / YouGov, VOTER Survey Panel, baseline "
                   "wave (~2011), via Ryan Burge (github.com/ryanburge).",
        "via": "Ryan Burge",
        "wave_note": "baseline wave (~2011, religpew_baseline). Unweighted.",
        "excluded_groups": "Agnostic, Nothing in particular, and Something else dropped per "
                            "this chart's own request; Orthodox/Muslim/Hindu dropped as too "
                            "thin, matching every other chart in this family.",
        "excluded_too_thin": EXCLUDED_TOO_THIN,
        "group_order": GROUP_ORDER,
        "religious_org_pct": religious_org_pct,
        "nonreligious_causes_avg": nonreligious_avg,
    }
    with open("docs/datasets/ryan-burge/voter-volunteering-summary.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print("Religious organization, % volunteering:")
    for label in GROUP_ORDER:
        r = religious_org_pct[label]
        print(f"  {label:12} {r['pct']:5.1f}%  (n={r['valid_n']})")
    print("\nAverage non-religious causes volunteered for, per person:")
    for label in GROUP_ORDER:
        r = nonreligious_avg[label]
        print(f"  {label:12} {r['avg_causes']:5.2f}  (n={r['valid_n']})")
    print("\nWrote docs/datasets/ryan-burge/voter-volunteering-summary.json")


if __name__ == "__main__":
    main()

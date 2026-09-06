"""
Single-item pull-out from voter_matrices.py's political/social feeling-
thermometer matrix: how warmly do Americans feel toward gays and
lesbians, by religion (ft_gays_2017, VOTER Survey Panel 2017 wave)? Same
population/weighting/sentinel-exclusion convention as voter_matrices.py's
ft_matrix (see that file's own docstring) - this is the same underlying
number already live inside the "Feeling thermometers: political and
social groups, by religion" heatmap, pulled into its own single-target
magnitude bar rather than recomputed with a different method.

Usage: python scripts/ryan-burge/ft_gays_lesbians.py
"""
import json

import numpy as np
import pyreadstat

DTA = "data/ryan-burge/tier1-strong/voter_survey_panel.dta"

RELIGION_LABELS = {
    1: "Protestant", 2: "Catholic", 3: "Mormon", 5: "Jewish",
    7: "Buddhist", 9: "Atheist", 10: "Agnostic",
    11: "Nothing in particular", 12: "Something else",
}
FT_SENTINELS = {997, 998, 999}  # Don't know / Skipped / Not asked


def main():
    df, _ = pyreadstat.read_dta(
        DTA, usecols=["religpew_2017", "weight_2017", "ft_gays_2017"], apply_value_formats=False,
    )
    religion = df["religpew_2017"].to_numpy(dtype=float)
    weight = df["weight_2017"].to_numpy(dtype=float)
    ft = df["ft_gays_2017"].to_numpy(dtype=float)

    results = {}
    for code, label in RELIGION_LABELS.items():
        group_mask = religion == code
        valid = group_mask & ~np.isin(ft, list(FT_SENTINELS)) & ~np.isnan(ft)
        base_w = weight[valid].sum()
        results[label] = {
            "mean": round(float((ft[valid] * weight[valid]).sum() / base_w), 1) if base_w else None,
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = ~np.isin(ft, list(FT_SENTINELS)) & ~np.isnan(ft) & np.isin(religion, list(RELIGION_LABELS.keys()))
    results["All respondents"] = {
        "mean": round(float((ft[valid_all] * weight[valid_all]).sum() / weight[valid_all].sum()), 1),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(valid_all.sum()),
    }

    out = {
        "source": "Democracy Fund Voter Study Group / YouGov, VOTER Survey Panel, 2017 wave, "
                  "via Ryan Burge (github.com/ryanburge).",
        "via": "Ryan Burge",
        "method": "Population: religpew_2017, weighted by weight_2017. Feeling-thermometer "
                  "mean toward gays and lesbians (0=coldest/most unfavorable, 100=warmest/most "
                  "favorable); sentinel codes (don't know/skipped/not asked) excluded before "
                  "averaging. Orthodox (n=18), Muslim (n=13), and Hindu (n=3) excluded as too "
                  "thin, matching voter_matrices.py's convention.",
        "total_unweighted_n": int(len(df)),
        "group_order": list(RELIGION_LABELS.values()) + ["All respondents"],
        "ft_gays_lesbians": results,
    }
    with open("docs/datasets/ryan-burge/ft-gays-lesbians.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in out["group_order"]:
        r = results[label]
        mean = r["mean"]
        print(f"{label:24} {mean:5.1f}  (n={r['valid_unweighted_n']:>4})" if mean is not None else f"{label:24}   n/a")
    print("\nWrote docs/datasets/ryan-burge/ft-gays-lesbians.json")


if __name__ == "__main__":
    main()

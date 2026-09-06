"""
Single-item pull-out from voter_matrices.py's issue-importance matrix:
how important is gender equality as an issue, by religion (imiss_y_2017,
VOTER Survey Panel 2017 wave)? Same population/weighting/top-two-box
convention as voter_matrices.py's imiss_matrix (see that file's own
docstring) - this is the same underlying number already live inside the
"Issue importance, by religion" heatmap, pulled into its own single-issue
magnitude bar rather than recomputed with a different method.

Usage: python scripts/ryan-burge/gender_equality_importance.py
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
DK = {8, 9}  # Skipped, Not Asked - matches voter_matrices.py's IMISS_INVALID
IMPORTANT = {1, 2}  # very + somewhat important (top-two-box)


def main():
    df, _ = pyreadstat.read_dta(
        DTA, usecols=["religpew_2017", "weight_2017", "imiss_y_2017"], apply_value_formats=False,
    )
    religion = df["religpew_2017"].to_numpy(dtype=float)
    weight = df["weight_2017"].to_numpy(dtype=float)
    gender_equality = df["imiss_y_2017"].to_numpy(dtype=float)

    results = {}
    for code, label in RELIGION_LABELS.items():
        group_mask = religion == code
        valid = group_mask & ~np.isin(gender_equality, list(DK)) & ~np.isnan(gender_equality)
        important = valid & np.isin(gender_equality, list(IMPORTANT))
        base_w = weight[valid].sum()
        results[label] = {
            "pct": round(100 * weight[important].sum() / base_w, 2) if base_w else None,
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = ~np.isin(gender_equality, list(DK)) & ~np.isnan(gender_equality) & np.isin(religion, list(RELIGION_LABELS.keys()))
    important_all = valid_all & np.isin(gender_equality, list(IMPORTANT))
    results["All respondents"] = {
        "pct": round(100 * weight[important_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(valid_all.sum()),
    }

    out = {
        "source": "Ryan Burge (github.com/ryanburge), Democracy Fund VOTER Survey Panel, 2017 wave.",
        "via": "Ryan Burge",
        "method": "Population: religpew_2017, weighted by weight_2017. Share saying gender "
                  "equality is a very or somewhat important issue (top-two-box); don't know/"
                  "skipped excluded. Orthodox (n=18), Muslim (n=13), and Hindu (n=3) excluded "
                  "as too thin, matching voter_matrices.py's convention.",
        "total_unweighted_n": int(len(df)),
        "group_order": list(RELIGION_LABELS.values()) + ["All respondents"],
        "gender_equality_important": results,
    }
    with open("docs/datasets/ryan-burge/gender-equality-importance.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in out["group_order"]:
        r = results[label]
        print(f"{label:24} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>4})")
    print("\nWrote docs/datasets/ryan-burge/gender-equality-importance.json")


if __name__ == "__main__":
    main()

"""
Computes the three VOTER Survey Panel "matrix" graphics for the Data
Explorer's Ryan Burge pages - feeling thermometers (racial/religious and
political/social) and issue importance, all by religion (2017 wave), per
docs/datasets/ryan-burge/GRAPHICS_TODO.md's "VOTER Survey Panel" section.

Population/grouping: `religpew_2017`, weighted by `weight_2017` - same
choice and same excluded-too-thin groups (Orthodox n=18, Muslim n=13,
Hindu n=3) as voter_stranger.py; see that script's own docstring for why.

Feeling thermometers (`ft_*_2017`, 0-100 continuous): sentinel codes
997/998/999 (Don't know/Skipped/Not Asked) excluded before averaging, per
the backlog item's own instruction. Reports the weighted mean per
group x target cell.

Issue importance (`imiss_*_2017`, 4-point: Very/Somewhat/Not very/
Unimportant): **design decision** - top-two-box ("very" + "somewhat"
important), matching this project's existing convention for cutpoint
items without an explicit request for top-box alone (RELIMP in the Pew RLS
Practice section made the same call, for the same reason: it mirrors the
site's "somewhat + strongly agree" convention).

Usage: python scripts/ryan-burge/voter_matrices.py
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
EXCLUDED_TOO_THIN = {4: "Orthodox (n=18)", 6: "Muslim (n=13)", 8: "Hindu (n=3)"}
GROUP_ORDER = ["Mormon", "Protestant", "Catholic", "Jewish", "Buddhist",
               "Atheist", "Agnostic", "Nothing in particular", "Something else"]

FT_SENTINELS = {997, 998, 999}

FT_RACIAL_RELIGIOUS = {
    "ft_black_2017": "Blacks", "ft_white_2017": "Whites", "ft_hisp_2017": "Hispanics",
    "ft_asian_2017": "Asians", "ft_muslim_2017": "Muslims", "ft_jew_2017": "Jews",
    "ft_christ_2017": "Christians",
}
FT_POLITICAL_SOCIAL = {
    "ft_fem_2017": "Feminists", "ft_immig_2017": "Immigrants", "ft_gays_2017": "Gays and lesbians",
    "ft_unions_2017": "Labor unions", "ft_police_2017": "Police officers",
    "ft_altright_2017": "The alt-right movement", "ft_evang_2017": "Evangelical Christians",
    "ft_dem_2017": "Democrats", "ft_rep_2017": "Republicans",
}
IMISS_ITEMS = {
    "imiss_a_2017": "Crime", "imiss_b_2017": "The economy", "imiss_c_2017": "Immigration",
    "imiss_d_2017": "The environment", "imiss_e_2017": "Religious liberty",
    "imiss_f_2017": "Terrorism", "imiss_g_2017": "Gay rights", "imiss_h_2017": "Education",
    "imiss_i_2017": "Family and medical leave", "imiss_j_2017": "Health care",
    "imiss_k_2017": "Money in politics", "imiss_l_2017": "Climate change",
    "imiss_m_2017": "Social Security", "imiss_n_2017": "Infrastructure investment",
    "imiss_o_2017": "Jobs", "imiss_p_2017": "The budget deficit", "imiss_q_2017": "Poverty",
    "imiss_r_2017": "Taxes", "imiss_s_2017": "Medicare", "imiss_t_2017": "Abortion",
    "imiss_u_2017": "The size of government", "imiss_x_2017": "Racial equality",
    "imiss_y_2017": "Gender equality",
}
IMISS_TOP_TWO = {1, 2}  # Very Important, Somewhat Important
IMISS_INVALID = {8, 9}  # Skipped, Not Asked


def load(cols: list[str]):
    df, _ = pyreadstat.read_dta(
        DTA, usecols=["religpew_2017", "weight_2017", *cols], apply_value_formats=False,
    )
    religion = df["religpew_2017"].to_numpy(dtype=float)
    weight = df["weight_2017"].to_numpy(dtype=float)
    return df, religion, weight


def ft_matrix(targets: dict[str, str]) -> dict:
    df, religion, weight = load(list(targets.keys()))
    matrix = {}
    for group_code, group_label in RELIGION_LABELS.items():
        group_mask = religion == group_code
        row = {}
        for col, target_label in targets.items():
            vals = df[col].to_numpy(dtype=float)
            valid = group_mask & ~np.isin(vals, list(FT_SENTINELS)) & ~np.isnan(vals)
            base_w = weight[valid].sum()
            row[target_label] = round(float((vals[valid] * weight[valid]).sum() / base_w), 1) if base_w else None
        matrix[group_label] = row
    return matrix


def imiss_matrix(targets: dict[str, str]) -> dict:
    df, religion, weight = load(list(targets.keys()))
    matrix = {}
    for group_code, group_label in RELIGION_LABELS.items():
        group_mask = religion == group_code
        row = {}
        for col, target_label in targets.items():
            vals = df[col].to_numpy(dtype=float)
            valid = group_mask & ~np.isin(vals, list(IMISS_INVALID)) & ~np.isnan(vals)
            hit = valid & np.isin(vals, list(IMISS_TOP_TWO))
            base_w = weight[valid].sum()
            row[target_label] = round(100 * weight[hit].sum() / base_w, 1) if base_w else None
        matrix[group_label] = row
    return matrix


def main():
    racial_matrix = ft_matrix(FT_RACIAL_RELIGIOUS)
    political_matrix = ft_matrix(FT_POLITICAL_SOCIAL)
    imiss_mat = imiss_matrix(IMISS_ITEMS)

    common = {
        "source": "Democracy Fund Voter Study Group / YouGov, VOTER Survey Panel, 2017 wave, "
                   "via Ryan Burge (github.com/ryanburge).",
        "via": "Ryan Burge",
        "method": "Population: religpew_2017, weighted by weight_2017. Excludes three "
                  "categories too thin to show individually - see excluded_too_thin below.",
        "excluded_too_thin": EXCLUDED_TOO_THIN,
        "group_order": GROUP_ORDER,
    }

    racial_out = {
        **common,
        "note": "Feeling thermometer (0=coldest/most unfavorable, 100=warmest/most favorable). "
                "Sentinel codes (don't know/skipped/not asked) excluded before averaging.",
        "target_order": list(FT_RACIAL_RELIGIOUS.values()),
        "matrix": racial_matrix,
    }
    political_out = {
        **common,
        "note": "Feeling thermometer (0=coldest/most unfavorable, 100=warmest/most favorable). "
                "Sentinel codes (don't know/skipped/not asked) excluded before averaging.",
        "target_order": list(FT_POLITICAL_SOCIAL.values()),
        "matrix": political_matrix,
    }
    imiss_out = {
        **common,
        "note": "Share saying this issue is very or somewhat important (top-two-box) - see "
                "this script's own docstring for the design decision.",
        "target_order": list(IMISS_ITEMS.values()),
        "matrix": imiss_mat,
    }

    with open("docs/datasets/ryan-burge/voter-ft-racial-religious.json", "w", encoding="utf-8") as f:
        json.dump(racial_out, f, indent=2, ensure_ascii=False)
        f.write("\n")
    with open("docs/datasets/ryan-burge/voter-ft-political-social.json", "w", encoding="utf-8") as f:
        json.dump(political_out, f, indent=2, ensure_ascii=False)
        f.write("\n")
    with open("docs/datasets/ryan-burge/voter-issue-importance.json", "w", encoding="utf-8") as f:
        json.dump(imiss_out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    def show(label, matrix, targets):
        print(f"\n=== {label} ===")
        header = "religion".ljust(24) + "".join(t[:8].rjust(9) for t in targets)
        print(header)
        for group in GROUP_ORDER:
            row = matrix[group]
            print(group.ljust(24) + "".join(
                (f"{row[t]:.0f}".rjust(9) if row[t] is not None else "n/a".rjust(9)) for t in targets
            ))

    show("Feeling thermometers - racial/religious", racial_matrix, list(FT_RACIAL_RELIGIOUS.values()))
    show("Feeling thermometers - political/social", political_matrix, list(FT_POLITICAL_SOCIAL.values()))
    show("Issue importance (top-two-box %)", imiss_mat, list(IMISS_ITEMS.values()))

    print("\nWrote voter-ft-racial-religious.json, voter-ft-political-social.json, "
          "voter-issue-importance.json")


if __name__ == "__main__":
    main()

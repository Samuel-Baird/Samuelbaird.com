"""
ANES 2016 Time Series (American National Election Studies), redistributed by
Ryan Burge (github.com/ryanburge): the post-election moral-traditionalism and
gender-role battery, broken out by religious tradition.

Group variable: V161265x ("Major group religion summary": Mainline
Protestant, Evangelical Protestant, Black Protestant, Roman Catholic,
Undifferentiated Christian, Jewish, Other religion, Not religious) with
Latter-day Saints pulled out of "Other religion" via V161264x == 301
("Mormons; Latter Day Saints; Community of Christ"), 52 pre-election
respondents, 43 with a post-election interview. Black Protestant (31
pre-election, fewer post) is below the 30-valid floor for these
post-election items and is dropped, not shown. "Undifferentiated Christian"
is ANES's own label for respondents who said "Christian" without naming a
denomination; it is labeled "Christian (no denomination given)" here.

Weighted by V160102 (post-election weight, full sample: face-to-face + web).
All four items are post-election (V162xxx); respondents without a post
interview (-6/-7), refusals (-9), don't-knows (-8), and programming errors
(-4) are excluded from every base.

Items:
  V162230x  "It is much better for everyone involved if the man is the
            achiever outside the home and the woman takes care of the home
            and family" - 7-point summary; share saying much/somewhat/
            slightly better (1-3) vs. makes no difference or worse.
  V162229x  "Is it easier or harder for a working mother to bond with her
            child?" - 7-point summary; share saying slightly/somewhat/a
            great deal harder (5-7).
  V162210   "This country would have many fewer problems if there were more
            emphasis on traditional family ties" - share agreeing strongly or
            somewhat (1-2).
  V162208   "The newer lifestyles are contributing to the breakdown of our
            society" - share agreeing strongly or somewhat (1-2).

Usage: python scripts/ryan-burge/anes_2016_family_values.py
"""
import json

import numpy as np
import pyreadstat

DTA = "data/ryan-burge/tier2-small-n/anes_2016.dta"
OUT_DIR = "docs/datasets/ryan-burge"

LDS_CODE = 301  # V161264x
MAJOR_LABELS = {  # V161265x, excluding 3 (Black Protestant, n<30 post-election)
    2: "Evangelical Protestant",
    1: "Mainline Protestant",
    4: "Catholic",
    5: "Christian (no denomination given)",
    6: "Jewish",
    8: "Religiously unaffiliated",
    7: "Other religion",
}
LDS_LABEL = "Latter-day Saint"
ALL_LABEL = "All U.S. adults"

SOURCE = ("American National Election Studies, 2016 Time Series Study, "
          "via Ryan Burge (github.com/ryanburge).")

ITEMS = [
    {
        "var": "V162230x", "key": "man_works_woman_home_better",
        "stem": "anes-2016-man-works-woman-home",
        "valid": [1, 2, 3, 4, 5, 6, 7], "yes": [1, 2, 3],
        "method": "Share saying it is much, somewhat, or slightly better if the man is the "
                  "achiever outside the home and the woman takes care of the home and family "
                  "(vs. makes no difference or worse), V162230x.",
    },
    {
        "var": "V162229x", "key": "working_mother_bond_harder",
        "stem": "anes-2016-working-mother-bond",
        "valid": [1, 2, 3, 4, 5, 6, 7], "yes": [5, 6, 7],
        "method": "Share saying it is slightly, somewhat, or a great deal harder for a working "
                  "mother to bond with her child (vs. neither or easier), V162229x.",
    },
    {
        "var": "V162210", "key": "traditional_family_ties_agree",
        "stem": "anes-2016-traditional-family-ties",
        "valid": [1, 2, 3, 4, 5], "yes": [1, 2],
        "method": "Share agreeing strongly or somewhat that this country would have many fewer "
                  "problems if there were more emphasis on traditional family ties, V162210.",
    },
    {
        "var": "V162208", "key": "newer_lifestyles_breakdown_agree",
        "stem": "anes-2016-newer-lifestyles",
        "valid": [1, 2, 3, 4, 5], "yes": [1, 2],
        "method": "Share agreeing strongly or somewhat that the newer lifestyles are "
                  "contributing to the breakdown of our society, V162208.",
    },
]


def main():
    cols = ["V160102", "V161264x", "V161265x"] + [it["var"] for it in ITEMS]
    df, _ = pyreadstat.read_dta(DTA, usecols=cols, apply_value_formats=False)
    weight = df["V160102"].to_numpy(dtype=float)
    full = df["V161264x"].to_numpy(dtype=float)
    major = df["V161265x"].to_numpy(dtype=float)
    has_post = weight > 0

    is_lds = full == LDS_CODE
    groups = [(LDS_LABEL, is_lds)]
    for code, label in MAJOR_LABELS.items():
        groups.append((label, (major == code) & ~is_lds))

    for it in ITEMS:
        x = df[it["var"]].to_numpy(dtype=float)
        valid_item = np.isin(x, it["valid"]) & has_post
        results = {}
        for label, mask in groups:
            valid = mask & valid_item
            yes = valid & np.isin(x, it["yes"])
            base_w = weight[valid].sum()
            results[label] = {
                "pct": round(100 * weight[yes].sum() / base_w, 2) if base_w else None,
                "valid_unweighted_n": int(valid.sum()),
                "group_unweighted_n": int((mask & has_post).sum()),
            }
        valid_all = valid_item & (major >= 1)  # any coded religion group, incl. Black Protestant
        yes_all = valid_all & np.isin(x, it["yes"])
        results[ALL_LABEL] = {
            "pct": round(100 * weight[yes_all].sum() / weight[valid_all].sum(), 2),
            "valid_unweighted_n": int(valid_all.sum()),
            "group_unweighted_n": int((has_post & (major >= 1)).sum()),
        }
        out = {
            "source": SOURCE,
            "via": "Ryan Burge",
            "method": "Population: respondents with a post-election interview, weighted by "
                      "V160102 (post-election full-sample weight). Groups from V161265x "
                      "(major religion summary) with Latter-day Saints pulled out of 'Other "
                      "religion' via V161264x == 301; Black Protestant dropped (fewer than 30 "
                      "post-election respondents). " + it["method"] + " Refused/don't know/no "
                      "post interview excluded from the base. Latter-day Saint n=43 with a "
                      "post-election interview. 'All U.S. adults' includes Black Protestants.",
            "total_unweighted_n": int(has_post.sum()),
            "group_order": [label for label, _ in groups] + [ALL_LABEL],
            it["key"]: results,
        }
        path = f"{OUT_DIR}/{it['stem']}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"\n== {it['var']} -> {path}")
        for label in out["group_order"]:
            r = results[label]
            print(f"{label:36} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>4})")


if __name__ == "__main__":
    main()

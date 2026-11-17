"""
Faith Matters Survey 2006 (Robert Putnam & David Campbell, the "American
Grace" survey), redistributed by Ryan Burge (github.com/ryanburge): four
full-sample religious-practice/attitude items broken out by the survey's own
RELTRAD-style `reltrad` variable (which, unlike the standard 7-category
RELTRAD, carries Mormon as its own category, code 6, n=53 unweighted).

Every item here was asked of the full sample (~3,100), so the Latter-day
Saint cell clears the pipeline's 30-valid-respondent floor (42-53 valid,
depending on item). The survey's split-sample items (grace before meals,
religious abstinence from food/drink/tobacco, morality of homosexuality,
feeling God's love) were asked of only ~1,550 and leave Latter-day Saint at
n=21-25 - checked and deliberately NOT charted.

Items (all weighted by `weight`; don't know/refused excluded from the base):
  CONV_OK  12-13 "Okay for religious people to try to convert others" (1)
           vs "Everyone should leave everyone else alone" (0)
  giverel  14-2  Money given to religious causes in the past 12 months;
           share giving $1,000 or more (codes 5-6 of a 6-band scale)
  wedinrel 9-8   Importance that your children marry someone of your own
           faith; share saying "Very important" (3). Asked only of
           respondents with children (687 skipped).
  talkrel  11-4  How often you talk about religion with family and friends;
           share saying "Roughly daily" (5)

Group labels: the survey's `reltrad` labels are mapped to this site's
canonical spellings (chart_style.GROUP_COLORS). Its "Evangelical
Protestant/Other Protestant" category is labeled "Evangelical Protestant"
here; "None" is "Religiously unaffiliated"; "Black Protestant" is
"Historically Black Protestant"; "Mormon" is "Latter-day Saint".

Usage: python scripts/ryan-burge/faith_matters_2006.py
"""
import json

import numpy as np
import pyreadstat

DTA = "data/ryan-burge/tier2-small-n/faith_matters_2006.DTA"
OUT_DIR = "docs/datasets/ryan-burge"

RELTRAD_LABELS = {
    6: "Latter-day Saint",
    3: "Evangelical Protestant",
    4: "Historically Black Protestant",
    2: "Mainline Protestant",
    1: "Catholic",
    5: "Jewish",
    0: "Religiously unaffiliated",
    7: "Other non-Christian",
}
ALL_LABEL = "All U.S. adults"

SOURCE = ("Faith Matters Survey 2006 (Robert D. Putnam and David E. Campbell), "
          "via Ryan Burge (github.com/ryanburge).")

ITEMS = [
    {
        "var": "CONV_OK", "key": "convert_ok", "stem": "faith-matters-convert-ok",
        "valid": [0, 1], "yes": [1],
        "method": "Share saying it is okay for religious people to try to convert others "
                  "(vs. 'everyone should leave everyone else alone'), Q12-13.",
    },
    {
        "var": "giverel", "key": "gave_1000_plus_religious", "stem": "faith-matters-religious-giving",
        "valid": [1, 2, 3, 4, 5, 6], "yes": [5, 6],
        "method": "Share whose household gave $1,000 or more to religious causes in the past "
                  "12 months (top two bands of a six-band scale: $1,000-$4,999 and $5,000+), Q14-2.",
    },
    {
        "var": "wedinrel", "key": "marry_within_faith_very_important", "stem": "faith-matters-marry-within-faith",
        "valid": [0, 1, 2, 3], "yes": [3],
        "method": "Share saying it is 'very important' that their children marry someone of "
                  "their own faith, Q9-8. Asked of respondents with children.",
    },
    {
        "var": "talkrel", "key": "talk_religion_daily", "stem": "faith-matters-talk-religion",
        "valid": [1, 2, 3, 4, 5], "yes": [5],
        "method": "Share saying they talk about religion with family and friends 'roughly "
                  "daily' (top of a five-point never-to-daily scale), Q11-4.",
    },
]


def main():
    cols = ["reltrad", "weight"] + [it["var"] for it in ITEMS]
    df, _ = pyreadstat.read_dta(DTA, usecols=cols, apply_value_formats=False)
    reltrad = df["reltrad"].to_numpy(dtype=float)
    weight = df["weight"].to_numpy(dtype=float)

    for it in ITEMS:
        x = df[it["var"]].to_numpy(dtype=float)
        valid_all = np.isin(x, it["valid"]) & ~np.isnan(reltrad)
        results = {}
        for code, label in RELTRAD_LABELS.items():
            group = reltrad == code
            valid = group & valid_all
            yes = valid & np.isin(x, it["yes"])
            base_w = weight[valid].sum()
            results[label] = {
                "pct": round(100 * weight[yes].sum() / base_w, 2) if base_w else None,
                "valid_unweighted_n": int(valid.sum()),
                "group_unweighted_n": int(group.sum()),
            }
        yes_all = valid_all & np.isin(x, it["yes"])
        results[ALL_LABEL] = {
            "pct": round(100 * weight[yes_all].sum() / weight[valid_all].sum(), 2),
            "valid_unweighted_n": int(valid_all.sum()),
            "group_unweighted_n": int((~np.isnan(reltrad)).sum()),
        }
        out = {
            "source": SOURCE,
            "via": "Ryan Burge",
            "method": "Population: all respondents with a coded religious tradition (reltrad), "
                      "weighted by `weight`. " + it["method"] + " Don't know/refused excluded "
                      "from the base. Latter-day Saint = reltrad 6 (Mormon), 53 unweighted "
                      "respondents in the full sample.",
            "total_unweighted_n": int(len(df)),
            "group_order": list(RELTRAD_LABELS.values()) + [ALL_LABEL],
            it["key"]: results,
        }
        path = f"{OUT_DIR}/{it['stem']}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"\n== {it['var']} -> {path}")
        for label in out["group_order"]:
            r = results[label]
            print(f"{label:32} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>4})")


if __name__ == "__main__":
    main()

"""
Faith Matters Survey 2011 (Robert Putnam & David Campbell's second American
Grace wave), redistributed by Ryan Burge (github.com/ryanburge): four items
that were NEW in 2011 (not asked in 2006), broken out by the survey's own
RELTRAD-style `RELTRA11` variable, which keeps Mormon as its own category
(code 6, n=49 unweighted among the 2,305 respondents with a coded tradition).

The .dta carries 4,069 rows, but only 2,322 are 2011 interviews (1,361
recontacted 2006 panelists + 751 fresh adult sample + 210 youth sample, per
SAMPLE11); the remaining 1,747 rows are 2006 panel dropouts with no 2011
data and are excluded automatically by requiring a 2011 weight. Weighted by
`WGTTOT11` ("Weight for all respondents"). Because most of the 2011 sample
are re-interviewed 2006 respondents, this wave is NOT poolable with
faith_matters_2006.py's output without double-counting panelists.

Items (don't know/refused are already missing in this file):
  WRLDEN11 12-1  "Do you believe the world is soon coming to an end, or not?"
           share saying yes (1). Full 2011 sample; LDS n=48.
  FTHDEE11 12-6  Path to salvation: through actions/deeds (1), a mixture
           (volunteered), or beliefs/faith. Share choosing actions or deeds
           (code 1). Only code 1 is charted: this file's value labels put
           "Mixture (Volunteered)" on code 2 and "beliefs or faith" on code 3,
           the reverse of the 2006 file, and the marginals (Evangelical
           Protestant 71% on code 2, 6% on code 3) make it clear code 2 is
           really "faith" - so the two minor codes are labeled unreliably and
           are left out of the chart. Full 2011 sample; LDS n=48.
  BLDMUS11 13-4  "Suppose some Muslims wanted to build a large mosque in your
           community, would that bother you a lot / a little / not bother
           you / be something you welcome?" Share saying it would not bother
           them or they would welcome it (3, 4). Split-sample item (~1,500
           asked); LDS n=34 - above the 30-valid floor, but thin.
  RELINF11 1-1   "Do you think organized religion has too much influence on
           American politics, too little, or about the right amount?" Share
           saying too little (0). Full 2011 sample; LDS n=48.

Group labels: the survey's `RELTRA11` labels are mapped to this site's
canonical spellings (chart_style.GROUP_COLORS): "None" -> "Religiously
unaffiliated", "Black Protestant" -> "Historically Black Protestant",
"Mormon" -> "Latter-day Saint". 2011 also splits an "Other
Protestant/Christian" catch-all (code 8) out of 2006's combined
Evangelical/Other Protestant category; it is kept as its own (gray,
sink-to-bottom) row.

Usage: python scripts/ryan-burge/faith_matters_2011.py
"""
import json

import numpy as np
import pyreadstat

DTA = "data/ryan-burge/tier2-small-n/faith_matters_2011.DTA"
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
    8: "Other Protestant/Christian",
}
ALL_LABEL = "All U.S. adults"

SOURCE = ("Faith Matters Survey 2011 (Robert D. Putnam and David E. Campbell), "
          "via Ryan Burge (github.com/ryanburge).")

ITEMS = [
    {
        "var": "WRLDEN11", "key": "world_ending_soon", "stem": "faith-matters-2011-world-ending",
        "valid": [0, 1], "yes": [1],
        "method": "Share saying yes to 'Do you believe the world is soon coming to an end, "
                  "or not?', Q12-1.",
    },
    {
        "var": "FTHDEE11", "key": "salvation_through_deeds", "stem": "faith-matters-2011-salvation-deeds",
        "valid": [1, 2, 3], "yes": [1],
        "method": "Share saying 'the path to salvation comes through our actions or deeds' "
                  "rather than 'lies in our beliefs or faith' (or a volunteered mixture of "
                  "the two), Q12-6. Respondents who don't believe in salvation excluded from "
                  "the base.",
    },
    {
        "var": "BLDMUS11", "key": "mosque_not_bothered_or_welcome", "stem": "faith-matters-2011-mosque",
        "valid": [1, 2, 3, 4], "yes": [3, 4],
        "method": "Share saying a large mosque built in their community would 'not bother' "
                  "them or would 'be something you welcome' (vs. bother them a lot or a "
                  "little), Q13-4. Split-sample item; Latter-day Saint n=34.",
    },
    {
        "var": "RELINF11", "key": "religion_too_little_influence", "stem": "faith-matters-2011-religion-influence",
        "valid": [0, 1, 2], "yes": [0],
        "method": "Share saying organized religion has 'too little influence' on American "
                  "politics (vs. about the right amount or too much), Q1-1.",
    },
]


def main():
    cols = ["RELTRA11", "WGTTOT11"] + [it["var"] for it in ITEMS]
    df, _ = pyreadstat.read_dta(DTA, usecols=cols, apply_value_formats=False)
    reltrad = df["RELTRA11"].to_numpy(dtype=float)
    weight = df["WGTTOT11"].to_numpy(dtype=float)
    in_2011 = ~np.isnan(weight)
    weight = np.where(in_2011, weight, 0.0)

    for it in ITEMS:
        x = df[it["var"]].to_numpy(dtype=float)
        valid_all = np.isin(x, it["valid"]) & ~np.isnan(reltrad) & in_2011
        results = {}
        for code, label in RELTRAD_LABELS.items():
            group = (reltrad == code) & in_2011
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
            "group_unweighted_n": int((~np.isnan(reltrad) & in_2011).sum()),
        }
        out = {
            "source": SOURCE,
            "via": "Ryan Burge",
            "method": "Population: 2011 respondents with a coded religious tradition (RELTRA11), "
                      "weighted by WGTTOT11. " + it["method"] + " Don't know/refused excluded "
                      "from the base. Latter-day Saint = RELTRA11 6 (Mormon), 49 unweighted "
                      "respondents in the 2011 sample.",
            "total_unweighted_n": int(in_2011.sum()),
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

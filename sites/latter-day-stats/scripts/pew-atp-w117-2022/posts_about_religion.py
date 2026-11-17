"""
ATP Wave 117 (November 2022): among social media users, who posts or shares
things about their religion (or their thoughts on religion) on social media?
SNSPOST3_W117 was asked of respondents who use social media, broken out by
F_RELTRAD (option 3, "I generally do not post or share anything on social
media," is excluded from the denominator so this reads as a share of social
media users who post about religion specifically, not social media use in
general). Latter-day Saints report the highest rate of any tradition (57%),
narrowly ahead of Evangelical Protestants (56%) and Historically Black
Protestants (55%) - a companion to this wave's already-shipped
`follows-own-leaders.json` (following rather than posting) that rounds out
the wave's picture of Latter-day Saints as unusually active religious
participants on social media. Groups under 30 valid respondents are dropped.

Usage: python scripts/pew-atp-w117-2022/posts_about_religion.py
"""
import json

import numpy as np
import pyreadstat

SAV = "data/pew-atp-w117-2022/ATP W117.sav"

RELTRAD_CODES = {
    1100.0: "Evangelical Protestant",
    1200.0: "Mainline Protestant",
    1300.0: "Historically Black Protestant",
    10000.0: "Catholic",
    20000.0: "Mormon",
    30000.0: "Orthodox Christian",
    50000.0: "Jewish",
    100000.0: "Unaffiliated",
}
YES = 1.0
VALID_CODES = {1.0, 2.0}
MIN_VALID_N = 30


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["F_RELTRAD", "SNSPOST3_W117", "WEIGHT_W117"])
    weight = df["WEIGHT_W117"].to_numpy()
    reltrad = df["F_RELTRAD"].to_numpy()
    posts = df["SNSPOST3_W117"].to_numpy()

    results = {}
    for code, label in RELTRAD_CODES.items():
        group_mask = reltrad == code
        valid = group_mask & np.isin(posts, list(VALID_CODES))
        if valid.sum() < MIN_VALID_N:
            continue
        yes = valid & (posts == YES)
        results[label] = {
            "pct": round(100 * weight[yes].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = np.isin(posts, list(VALID_CODES))
    yes_all = valid_all & (posts == YES)
    results["All U.S. adults"] = {
        "pct": round(100 * weight[yes_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }

    order = sorted(results, key=lambda label: -results[label]["pct"])
    order.remove("All U.S. adults")
    order.append("All U.S. adults")

    out = {
        "source": "Pew Research Center. American Trends Panel Wave 117, fielded November 16-27, 2022.",
        "method": "Population is respondent's religious tradition (F_RELTRAD), among "
                  "social media users. Share answering \"yes, I do this\" to "
                  "SNSPOST3_W117 (\"Do you ever post or share things about your "
                  "religion/your thoughts on religion on social media?\"); respondents "
                  "who generally do not post or share anything on social media, and "
                  "refused, are excluded from each row's denominator. Groups under 30 "
                  "valid respondents omitted. Weighted by the dataset's own "
                  "WEIGHT_W117 variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "group_order": order,
        "posts_about_religion": results,
    }
    with open("docs/datasets/pew-atp-w117-2022/posts-about-religion.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:26} {r['pct']:5.1f}%  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-atp-w117-2022/posts-about-religion.json")


if __name__ == "__main__":
    main()

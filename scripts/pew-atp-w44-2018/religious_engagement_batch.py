"""
Three religious-engagement items from ATP Wave 44, broken out by F_RELTRAD -
same by-group construction, Protestant-collapse, and MIN_VALID_N floor as
scripts/pew-atp-w44-2018/knowledge_batch.py.

- READREL1: "How often do you do things to help you learn about your own
  religion (e.g. reading scripture, visiting websites, listening to
  podcasts, reading books/magazines, watching TV)?" Collapsed to "at least
  weekly" (More than once a week + Once a week). Ties to LDS emphasis on
  daily/weekly personal and family scripture study.
- REL4c: "Do you, personally, happen to know anyone who is Mormon?" Asked
  of the full sample regardless of the respondent's own tradition - this
  measures how visible/socially proximate Latter-day Saints are to each
  other tradition, not LDS respondents' own answers about themselves.
- RELSCHL2: "How many years, if any, did you attend Sunday school, CCD, or
  some other form of religious education?" Collapsed to "4+ years" (4-6
  years + 7 years or more). Ties to the Church's youth Primary/Sunday
  School programs.

Usage: python scripts/pew-atp-w44-2018/religious_engagement_batch.py
"""
import json

import numpy as np
import pyreadstat

SAV = "data/pew-atp-w44-2018/ATP W44.sav"

RELTRAD_CODES = {
    (1100.0, 1200.0, 1300.0): "Protestant",
    (10000.0,): "Catholic",
    (20000.0,): "Latter-day Saint",
    (30000.0,): "Orthodox Christian",
    (40001.0,): "Jehovah's Witness",
    (40002.0,): "Other Christian",
    (50000.0,): "Jewish",
    (60000.0,): "Muslim",
    (70000.0,): "Buddhist",
    (80000.0,): "Hindu",
    (90001.0,): "Other world religions",
    (90002.0,): "Other faiths",
    (100000.0,): "Religiously unaffiliated",
}
MIN_VALID_N = 30


def share_by_group(col, weight, reltrad, hit_codes, valid_codes):
    results = {}
    for codes, label in RELTRAD_CODES.items():
        group_mask = np.isin(reltrad, codes)
        valid = group_mask & np.isin(col, list(valid_codes))
        if valid.sum() < MIN_VALID_N:
            continue
        hit = valid & np.isin(col, list(hit_codes))
        results[label] = {
            "pct": round(100 * weight[hit].sum() / weight[valid].sum(), 2),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }
    valid_all = np.isin(col, list(valid_codes))
    hit_all = valid_all & np.isin(col, list(hit_codes))
    results["U.S. adults"] = {
        "pct": round(100 * weight[hit_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(col)),
    }
    return results


def main():
    cols = ["F_RELTRAD", "READREL1_W44", "REL4c_W44", "RELSCHL2_W44", "WEIGHT_W44"]
    df, _ = pyreadstat.read_sav(SAV, usecols=cols)
    weight = df["WEIGHT_W44"].to_numpy()
    reltrad = df["F_RELTRAD"].to_numpy()

    readrel1 = share_by_group(
        df["READREL1_W44"].to_numpy(), weight, reltrad,
        hit_codes={1.0, 2.0}, valid_codes={1.0, 2.0, 3.0, 4.0, 5.0, 6.0},
    )
    rel4c = share_by_group(
        df["REL4c_W44"].to_numpy(), weight, reltrad,
        hit_codes={1.0}, valid_codes={1.0, 2.0},
    )
    relschl2 = share_by_group(
        df["RELSCHL2_W44"].to_numpy(), weight, reltrad,
        hit_codes={3.0, 4.0}, valid_codes={1.0, 2.0, 3.0, 4.0},
    )

    out = {
        "source": "Pew Research Center. American Trends Panel Wave 44, fielded Feb. 4-19, 2019.",
        "method": "Population is all respondents, grouped by religious tradition (F_RELTRAD). "
                  "Each item's own refused excluded from its own denominator. Groups under 30 "
                  "valid respondents omitted. Weighted by WEIGHT_W44.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "learns_about_own_religion_weekly_plus": readrel1,
        "personally_knows_a_mormon": rel4c,
        "religious_ed_4plus_years": relschl2,
    }
    with open("docs/datasets/pew-atp-w44-2018/religious-engagement-batch.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("Wrote docs/datasets/pew-atp-w44-2018/religious-engagement-batch.json")


if __name__ == "__main__":
    main()

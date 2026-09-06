"""
Computes 2007 -> 2023-24 share-of-U.S.-adults change for EVERY religious
tradition in Pew's RELTRAD taxonomy - not just the Christian denominations
(compare scripts/pew-rls/switching_generalized.py and this site's Deseret
News op-ed set, both of which stop at Christian traditions). RELTRAD's codes
are identical across all three Religious Landscape Study waves (verified
against each wave's own value-label table), so no recoding is needed.

This is a "mixed data" entry (see src/lib/data-explorer.ts's Dataset.category
doc): it reads two separate raw files - the 2007 continental-US .sav and the
2023-24 public-use CSV - the same way us-membership-growth-2000-2025 and
ten-largest-us-churches-2035 stitch together multiple sources, rather than
one survey's own microdata.

Every group's own unweighted n is carried through so a reader can judge
which changes are precise (Evangelical, Catholic, Unaffiliated - thousands
of respondents) and which are noisy (Hindu, Buddhist, Jehovah's Witness -
a few hundred).

Usage (from the repo root): python scripts/religious-tradition-shifts/compute_shifts.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pyreadstat

ROOT = Path(__file__).resolve().parent.parent.parent
SAV_2007 = ROOT / "data/pew-rls-2007/Religious Landscape Survey Data - Continental US.sav"
CSV_2324 = ROOT / "data/pew-rls-2023-24/2023-24 RLS Public Use File Feb 19.csv"
OUT = ROOT / "docs/datasets/religious-tradition-shifts/shifts-2007-2023.json"

# RELTRAD codes are identical across all three RLS waves (2007, 2014,
# 2023-24) - confirmed directly against each wave's own value-label table.
# Canonical display names follow chart_style.py's GROUP_COLORS/GROUP_ALIASES
# so every row gets this site's locked identity color automatically.
RELTRAD = {
    "1100": "Evangelical Protestant",
    "1200": "Mainline Protestant",
    "1300": "Historically Black Protestant",
    "10000": "Catholic",
    "20000": "Latter-day Saint",
    "30000": "Orthodox Christian",
    "40001": "Jehovah's Witness",
    "40002": "Other Christian",
    "50000": "Jewish",
    "60000": "Muslim",
    "70000": "Buddhist",
    "80000": "Hindu",
    "90001": "Other World Religions",
    "90002": "Other Faiths",
    "100000": "Religiously unaffiliated",
}
DK = "900000"


def codes_as_str(series) -> np.ndarray:
    return np.array([str(int(v)) if v == v else "nan" for v in series.to_numpy()])


def shares(reltrad: np.ndarray, weight: np.ndarray) -> dict:
    total = weight.sum()
    out = {}
    for code, name in RELTRAD.items():
        mask = reltrad == code
        out[name] = {
            "pct": round(float(100 * weight[mask].sum() / total), 3),
            "unweighted_n": int(mask.sum()),
        }
    return out


def main() -> None:
    print("2007 ...")
    df07, _ = pyreadstat.read_sav(str(SAV_2007), usecols=["reltrad", "weight"])
    shares_07 = shares(codes_as_str(df07["reltrad"]), df07["weight"].to_numpy())

    print("2023-24 ...")
    import pandas as pd
    df23 = pd.read_csv(CSV_2324, usecols=["RELTRAD", "WEIGHT"], dtype={"RELTRAD": str})
    shares_23 = shares(df23["RELTRAD"].to_numpy(), df23["WEIGHT"].to_numpy())

    groups = []
    for name in RELTRAD.values():
        old, new = shares_07[name]["pct"], shares_23[name]["pct"]
        groups.append({
            "name": name,
            "pct_2007": old,
            "pct_2023_24": new,
            "unweighted_n_2007": shares_07[name]["unweighted_n"],
            "unweighted_n_2023_24": shares_23[name]["unweighted_n"],
            "absolute_change_pct_points": round(new - old, 3),
            "relative_change_pct": round(100 * (new - old) / old, 1),
        })
    groups.sort(key=lambda g: -g["pct_2023_24"])

    out = {
        "source_2007": 'Pew Research Center. 2008. "U.S. Religious Landscape Survey." '
                       "Continental-US file, N=35,556.",
        "source_2023_24": 'Pew Research Center. 2025. "2023-24 Religious Landscape Study '
                          '(RLS) Dataset." doi: 10.58094/3kwb-bf52. Public-use file, N=36,908.',
        "method": "Share of ALL U.S. adults identifying with each RELTRAD tradition (Pew's "
                  "own religious-tradition classification, identical coding across every RLS "
                  "wave), weighted by each wave's own weight variable, don't-know/refused kept "
                  "in the denominator. 2007 is the continental-U.S. main survey only. Not every "
                  "small group's change is statistically meaningful - see each row's "
                  "unweighted n; groups under a few hundred respondents (Jehovah's Witness, "
                  "Buddhist, Hindu, Orthodox Christian) carry wide margins of error in both "
                  "waves. The 2023-24 wave also changed data collection mode from telephone "
                  "(2007) to mostly online/mail, which Pew flags as a caveat for any "
                  "cross-wave comparison.",
        "group_order": [g["name"] for g in groups],
        "groups": groups,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"\n{'Group':30} {'2007':>7} {'2023-24':>8} {'abs pt':>8} {'rel %':>8}  n07/n23")
    for g in groups:
        print(f"{g['name']:30} {g['pct_2007']:7.2f} {g['pct_2023_24']:8.2f} "
              f"{g['absolute_change_pct_points']:8.2f} {g['relative_change_pct']:8.1f}  "
              f"{g['unweighted_n_2007']}/{g['unweighted_n_2023_24']}")
    print(f"\nWrote {OUT}")


if __name__ == "__main__":
    main()

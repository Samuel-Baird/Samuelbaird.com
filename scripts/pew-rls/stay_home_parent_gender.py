"""
Second-order follow-up to holiday_batch.py's PAR2CHILD item: of those who
say it's generally better if a parent stays home to focus on the family,
should that parent specifically be the mother? PAR2CHILDA asks "mother,
father, or doesn't matter" - "father" is a negligible share in every
tradition (well under 5%), so the substantive split is "mother" vs.
"doesn't matter which parent." Population is conditioned on PAR2CHILD == 1
(believes a parent should stay home) - not the full CURREL population
every other RLS holiday-batch chart uses, since PAR2CHILDA was only asked
of that subset. Own don't know/refused (99) excluded.

Hook: Family Proclamation anniversary, Sep 23 2026 - a second, genuinely
new LDS-specific stat alongside the already-shipped PAR2CHILD chart
("Is a stay-at-home parent better for kids?").

Usage: python scripts/pew-rls/stay_home_parent_gender.py
"""
import json

import numpy as np
import pandas as pd

from practice import ALL_RELIGIOUS_CODES

CSV = "data/pew-rls-2023-24/2023-24 RLS Public Use File Feb 19.csv"

GROUP_CODES = {**ALL_RELIGIOUS_CODES, "100000": "Religiously unaffiliated"}
USECOLS = ["CURREL", "PAR2CHILD", "PAR2CHILDA", "WEIGHT"]
MOTHER = "1"
VALID = {"1", "2", "3"}


def main():
    print("Loading RLS CSV subset...")
    dtypes = {c: str for c in ["CURREL", "PAR2CHILD", "PAR2CHILDA"]}
    df = pd.read_csv(CSV, usecols=USECOLS, dtype=dtypes)
    weight = df["WEIGHT"].to_numpy()
    currel = df["CURREL"].to_numpy()
    stay_home_believer = df["PAR2CHILD"].to_numpy() == "1"
    answer = df["PAR2CHILDA"].to_numpy()

    results = {}
    for code, label in GROUP_CODES.items():
        group_mask = (currel == code) & stay_home_believer
        valid = group_mask & np.isin(answer, list(VALID))
        mother = valid & (answer == MOTHER)
        results[label] = {
            "pct": round(100 * weight[mother].sum() / weight[valid].sum(), 2) if valid.sum() else None,
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }
    valid_all = stay_home_believer & np.isin(answer, list(VALID))
    mother_all = valid_all & (answer == MOTHER)
    results["All groups average"] = {
        "pct": round(100 * weight[mother_all].sum() / weight[valid_all].sum(), 2),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(stay_home_believer.sum()),
    }

    out = {
        "group_order": list(GROUP_CODES.values()) + ["All groups average"],
        "total_n": int(len(df)),
        "should_be_mother": results,
    }
    out_path = "docs/datasets/pew-rls-2023-24/stay-home-parent-gender.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"wrote {out_path}")

    for label, r in sorted(results.items(), key=lambda kv: -(kv[1]["pct"] or 0)):
        print(f"{label:32} {r['pct']}%  (n={r['valid_unweighted_n']:>4})" if r["pct"] is not None
              else f"{label:32} n/a (n={r['valid_unweighted_n']:>4})")


if __name__ == "__main__":
    main()

"""
How warmly do Americans feel toward Mormons? (REL3c_W44) - a 0-100
feeling-thermometer mean, by the respondent's own religious tradition
(F_RELTRAD). Unlike every other chart in this pipeline, the value plotted
is a mean rating, not a percentage - genuinely out-of-scale values (>100,
used as this wave's own refused/skip code) are dropped before averaging.
Same Protestant-collapse and MIN_VALID_N floor as knowledge_batch.py in
this folder.

General content - no single holiday hook, unlike this wave's knowledge
items.

Usage: python scripts/pew-atp-w44-2018/warmth_toward_mormons.py
"""
import json

import numpy as np
import pyreadstat

from knowledge_batch import RELTRAD_CODES, MIN_VALID_N

SAV = "data/pew-atp-w44-2018/ATP W44.sav"


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["F_RELTRAD", "REL3c_W44", "WEIGHT_W44"])
    weight = df["WEIGHT_W44"].to_numpy()
    reltrad = df["F_RELTRAD"].to_numpy()
    therm = df["REL3c_W44"].to_numpy()

    results = {}
    for codes, label in RELTRAD_CODES.items():
        group_mask = np.isin(reltrad, codes)
        valid = group_mask & (therm >= 0) & (therm <= 100)
        if valid.sum() < MIN_VALID_N:
            continue
        results[label] = {
            "mean": round(float(np.average(therm[valid], weights=weight[valid])), 1),
            "valid_unweighted_n": int(valid.sum()),
            "group_unweighted_n": int(group_mask.sum()),
        }

    valid_all = (therm >= 0) & (therm <= 100)
    results["U.S. adults"] = {
        "mean": round(float(np.average(therm[valid_all], weights=weight[valid_all])), 1),
        "valid_unweighted_n": int(valid_all.sum()),
        "group_unweighted_n": int(len(df)),
    }

    out = {
        "source": "Pew Research Center. American Trends Panel Wave 44, fielded Feb. 4-19, 2019.",
        "method": "Population is all respondents, grouped by religious tradition (F_RELTRAD; "
                  "Protestant sub-traditions collapsed, see knowledge_batch.py's own note). "
                  "REL3c is a 0-100 feeling thermometer toward Mormons (0=coldest, "
                  "100=warmest); out-of-range codes (refused) excluded. Groups under 30 valid "
                  "respondents omitted. Weighted mean by WEIGHT_W44.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "warmth_toward_mormons": results,
    }
    with open("docs/datasets/pew-atp-w44-2018/warmth-toward-mormons.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label, r in sorted(results.items(), key=lambda kv: -kv[1]["mean"]):
        print(f"{label:32} {r['mean']:5.1f}  (n={r['valid_unweighted_n']:>5})")
    print("\nWrote docs/datasets/pew-atp-w44-2018/warmth-toward-mormons.json")


if __name__ == "__main__":
    main()

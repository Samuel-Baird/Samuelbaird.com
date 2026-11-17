"""
Fifth flagship chart for the 2007 U.S. Religious Landscape Survey: of
U.S. Mormons, what share live in each Census region? Population is
respondents whose current tradition (RELTRAD) is Mormon, continental-US
main survey only, broken out by cregion. Framed as "share of Mormons by
region" rather than "Mormon share of each region's population" - the
latter rounds three of four regions to 0% at this site's whole-percent
display convention (0.4-0.6% in the Northeast/Midwest/South vs. this
framing's meaningfully distinct 4-77%), so this framing is the one that
actually reads.

Usage: python scripts/pew-rls-2007/lds_share_by_region.py
"""
import json

import numpy as np
import pyreadstat

SAV = "data/pew-rls-2007/Religious Landscape Survey Data - Continental US.sav"

REGION_CODES = {1.0: "Northeast", 2.0: "Midwest", 3.0: "South", 4.0: "West"}
MORMON = 20000.0


def main():
    df, _ = pyreadstat.read_sav(SAV, usecols=["cregion", "reltrad", "weight"])
    weight = df["weight"].to_numpy()
    region = df["cregion"].to_numpy()
    reltrad = df["reltrad"].to_numpy()

    mormon = reltrad == MORMON
    mormon_w = weight[mormon].sum()
    mormon_n = int(mormon.sum())

    results = {}
    for code, label in REGION_CODES.items():
        mask = mormon & (region == code)
        results[label] = {
            "pct": round(100 * weight[mask].sum() / mormon_w, 2),
            "unweighted_n": int(mask.sum()),
        }

    order = sorted(results, key=lambda label: -results[label]["pct"])

    out = {
        "source": 'Pew Research Center. 2008. "U.S. Religious Landscape Survey."',
        "method": "Population is respondents whose current tradition (RELTRAD) is Mormon, "
                  "continental-US main survey only (the Alaska/Hawaii supplement is a "
                  "separate file and isn't combined here), broken out by Census region "
                  "(cregion). Weighted by the dataset's own `weight` variable.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "mormon_unweighted_n": mormon_n,
        "region_order": order,
        "share_of_mormons": results,
    }
    with open("docs/datasets/pew-rls-2007/lds-share-by-region.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for label in order:
        r = results[label]
        print(f"{label:12} {r['pct']:5.1f}%  (n={r['unweighted_n']:>4})")
    print("\nWrote docs/datasets/pew-rls-2007/lds-share-by-region.json")


if __name__ == "__main__":
    main()

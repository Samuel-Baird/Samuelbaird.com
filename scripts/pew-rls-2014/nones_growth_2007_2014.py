"""
Fifth flagship chart for the 2014 Religious Landscape Study: how much did
the religiously unaffiliated ("nones") share of the U.S. population grow
between the 2007 and 2014 Religious Landscape Study waves? Reads BOTH
waves' microdata (unusual for this site's per-dataset scripts, which
normally read only their own folder's .sav - justified here because the
whole point is the two-wave comparison, and both files use the same
RELTRAD coding for "Unaffiliated"). Filed under pew-rls-2014 since it's
this wave's own headline finding ("nones" overtaking many single
traditions), with the 2007 wave as its baseline.

Usage: python scripts/pew-rls-2014/nones_growth_2007_2014.py
"""
import json

import numpy as np
import pyreadstat

SAV_2007 = "data/pew-rls-2007/Religious Landscape Survey Data - Continental US.sav"
SAV_2014 = ("data/pew-rls-2014/"
            "Dataset - Pew Research Center 2014 Religious Landscape Study National "
            "Telephone Survey - Version 1.1 - December 1 2016.sav")
UNAFFILIATED = 100000.0


def main():
    df07, _ = pyreadstat.read_sav(SAV_2007, usecols=["reltrad", "weight"])
    w07 = df07["weight"].to_numpy()
    unaff07 = df07["reltrad"].to_numpy() == UNAFFILIATED
    pct07 = round(100 * w07[unaff07].sum() / w07.sum(), 2)

    df14, _ = pyreadstat.read_sav(SAV_2014, usecols=["RELTRAD", "WEIGHT"])
    w14 = df14["WEIGHT"].to_numpy()
    unaff14 = df14["RELTRAD"].to_numpy() == UNAFFILIATED
    pct14 = round(100 * w14[unaff14].sum() / w14.sum(), 2)

    results = {
        "2007": {"pct": pct07, "unweighted_n": int(unaff07.sum()), "total_unweighted_n": int(len(df07))},
        "2014": {"pct": pct14, "unweighted_n": int(unaff14.sum()), "total_unweighted_n": int(len(df14))},
    }

    out = {
        "source": 'Pew Research Center. 2008. "U.S. Religious Landscape Survey"; Pew '
                  'Research Center. 2015. "2014 Religious Landscape Study."',
        "method": "Unaffiliated (\"nones\") share of the total population in each wave's "
                  "own RELTRAD variable (code 100000). 2007 is continental-US main survey "
                  "only. Each wave weighted by its own weight variable.",
        "wave_order": ["2007", "2014"],
        "unaffiliated_pct": results,
    }
    with open("docs/datasets/pew-rls-2014/nones-growth-2007-2014.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for wave in out["wave_order"]:
        r = results[wave]
        print(f"{wave}  {r['pct']:5.1f}%  (n={r['unweighted_n']:>6} of {r['total_unweighted_n']:>6})")
    print("\nWrote docs/datasets/pew-rls-2014/nones-growth-2007-2014.json")


if __name__ == "__main__":
    main()

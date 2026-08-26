"""
Computes "raised in X" vs "currently X" net-change rates from the 2023-24
RLS microdata, for the Data Explorer's LDS-vs-other-traditions graphic.

Method mirrors Pew's own published Religious Landscape Study tables:
- % raised/current is FRMREL/CURREL as share of ALL respondents (weighted
  by WEIGHT), the same base Pew uses in its own report tables.
- Standard errors come from Pew's own bootstrap replicate weights
  (REPWT_001-REPWT_500), per the survey design note in the methodology
  report: `svyset [pweight=weight], bsrweight(repwt_001-repwt_500)
  vce(bootstrap)`. A naive weighted-proportion SE would understate
  uncertainty under this complex design; the replicate weights give the
  real one. Net-change SE is computed per-replicate (not via the delta
  method), which captures the correlation between "raised" and "current"
  estimates from the same 36,908 respondents.

FRMREL only codes "Protestant" as one bucket in the public-use file (the
Evangelical/Mainline/Historically Black split needs FRMREL2, restricted-use
only). So Protestant traditions are reported as one combined group here;
RELTRAD (current-only, public) supplies the three-way split as a separate
current-composition table, clearly not a switching rate.

Usage: python scripts/pew-rls/switching_rates.py
"""
import json

import numpy as np
import pandas as pd

CSV = "data/pew-rls-2023-24/2023-24 RLS Public Use File Feb 19.csv"

# FRMREL / CURREL codes -> group label. Matches both variables' shared
# coding (Pew designed CURREL to align with FRMREL for exactly this).
GROUPS = {
    "1000": "Protestant",
    "10000": "Catholic",
    "20000": "Latter-day Saint",
    "30000": "Orthodox Christian",
    "40001": "Jehovah's Witness",
    "40002": "Other Christian",
}

REPWT_COLS = [f"REPWT_{i:03d}" for i in range(1, 501)]
USECOLS = ["FRMREL", "CURREL", "RELTRAD", "WEIGHT", *REPWT_COLS]


def weighted_share(code_col: pd.Series, weight: np.ndarray, code: str) -> float:
    """% of the weighted population coded `code`, as Pew's own tables report it."""
    return 100 * weight[code_col.values == code].sum() / weight.sum()


def main():
    print("Loading CSV (this takes a bit - 502 columns, 36,908 rows)...")
    df = pd.read_csv(CSV, usecols=USECOLS, dtype={"FRMREL": str, "CURREL": str, "RELTRAD": str})
    weight = df["WEIGHT"].to_numpy()
    rep_weights = df[REPWT_COLS].to_numpy()  # shape (36908, 500)

    results = {}
    for code, label in GROUPS.items():
        raised_pt = weighted_share(df["FRMREL"], weight, code)
        current_pt = weighted_share(df["CURREL"], weight, code)
        net_change_pt = 100 * (current_pt - raised_pt) / raised_pt

        # Bootstrap: same point-estimate formula, once per replicate weight.
        # Vectorized over all 500 replicates at once rather than looped.
        raised_mask = (df["FRMREL"].values == code).astype(float)
        current_mask = (df["CURREL"].values == code).astype(float)
        rep_totals = rep_weights.sum(axis=0)  # (500,)
        raised_rep = 100 * (rep_weights * raised_mask[:, None]).sum(axis=0) / rep_totals
        current_rep = 100 * (rep_weights * current_mask[:, None]).sum(axis=0) / rep_totals
        net_change_rep = 100 * (current_rep - raised_rep) / raised_rep

        results[label] = {
            "raised_pct": round(raised_pt, 3),
            "raised_se": round(float(raised_rep.std(ddof=1)), 3),
            "current_pct": round(current_pt, 3),
            "current_se": round(float(current_rep.std(ddof=1)), 3),
            "net_change_pct": round(net_change_pt, 2),
            "net_change_se": round(float(net_change_rep.std(ddof=1)), 2),
            "raised_unweighted_n": int((df["FRMREL"] == code).sum()),
            "current_unweighted_n": int((df["CURREL"] == code).sum()),
        }

    # Current-only composition of the three Protestant subtraditions
    # (RELTRAD, public) - a snapshot, not a switching rate; FRMREL can't
    # split "raised Protestant" this finely in the public file.
    reltrad_codes = {"1100": "Evangelical Protestant", "1200": "Mainline Protestant",
                      "1300": "Historically Black Protestant"}
    protestant_composition = {}
    for code, label in reltrad_codes.items():
        pt = weighted_share(df["RELTRAD"], weight, code)
        mask = (df["RELTRAD"].values == code).astype(float)
        rep_totals = rep_weights.sum(axis=0)
        rep = 100 * (rep_weights * mask[:, None]).sum(axis=0) / rep_totals
        protestant_composition[label] = {
            "current_pct": round(pt, 3),
            "current_se": round(float(rep.std(ddof=1)), 3),
            "current_unweighted_n": int((df["RELTRAD"] == code).sum()),
        }

    out = {
        "source": "Pew Research Center. 2025. “2023-24 Religious Landscape Study "
                   "(RLS) Dataset.” doi: 10.58094/3kwb-bf52.",
        "method": "raised = FRMREL share, current = CURREL share, both weighted by WEIGHT; "
                  "net_change_pct = 100*(current-raised)/raised; standard errors from 500 "
                  "bootstrap replicate weights (REPWT_001-500) per Pew's survey design.",
        "total_weighted_n": float(weight.sum()),
        "total_unweighted_n": int(len(df)),
        "switching": results,
        "protestant_current_composition": protestant_composition,
    }
    with open("docs/datasets/pew-rls-2023-24/switching-rates.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print("\n=== Raised vs. current, net change (bootstrap SE) ===")
    for label, r in results.items():
        print(f"{label:22} raised {r['raised_pct']:5.2f}% (n={r['raised_unweighted_n']:>5})  "
              f"-> current {r['current_pct']:5.2f}% (n={r['current_unweighted_n']:>5})  "
              f"net {r['net_change_pct']:+7.2f}%  ±{1.96*r['net_change_se']:.1f} (95% CI)")

    print("\n=== Current Protestant composition (RELTRAD, snapshot only) ===")
    for label, r in protestant_composition.items():
        print(f"{label:30} {r['current_pct']:5.2f}%  (n={r['current_unweighted_n']})")

    print("\nWrote docs/datasets/pew-rls-2023-24/switching-rates.json")


if __name__ == "__main__":
    main()

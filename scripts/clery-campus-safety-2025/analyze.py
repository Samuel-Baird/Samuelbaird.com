#!/usr/bin/env python3
"""Institution-level on-campus reported rape analysis from the U.S. Dept. of
Education Campus Safety and Security (Clery Act) 2025 release, years 2022-24.

Source file: Oncampuscrime222324.xls (from Crime2025EXCEL.zip, downloaded from
https://ope.ed.gov/campussafety/#/datafile/list). One row per campus/branch.

Method
- Institution = UNITID_P minus its 3-digit branch suffix.
- Rapes: summed across an institution's campuses. "On-campus" in the file
  already includes residence halls (the residence-hall file is a subset), so
  the residence-hall file is NOT added.
- Enrollment ("Total"): the same institution-wide figure is repeated on every
  branch row, so it is taken once per institution (max), never summed.
- Four-year = Sector_desc "... 4-year or above" (public, private nonprofit,
  private for-profit).
- Rate per 10,000 = rapes / enrollment x 10,000. The file carries one
  enrollment figure per institution, applied to all three years.
- A year counts only if at least one of the institution's rows has
  FILTER<yy> == 1 (branches opened later carry 0 and blank counts) and the
  summed count is not blank.

Usage: python scripts/clery-campus-safety-2025/analyze.py [--src DIR]
Writes docs/datasets/clery-campus-safety-2025/*.json
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "datasets" / "clery-campus-safety-2025"
DEFAULT_SRC = Path.home() / "Downloads" / "Crime2025EXCEL"
BYU = "230038"
MIN_ENR_BROAD, MIN_ENR_LARGE = 1000, 5000


def load(src: Path) -> pd.DataFrame:
    df = pd.read_excel(src / "Oncampuscrime222324.xls")
    df = df[df["Sector_desc"].str.contains("4-year or above")].copy()
    df["inst"] = df["UNITID_P"].astype(str).str[:-3]
    for y in ("22", "23", "24"):
        df[f"RAPE{y}"] = pd.to_numeric(df[f"RAPE{y}"], errors="coerce")
    g = df.groupby("inst")
    out = pd.DataFrame({
        "name": g["INSTNM"].first(),
        "state": g["State"].first(),
        "sector": g["Sector_desc"].first(),
        "enrollment": g["Total"].max(),
        "n_campuses": g.size(),
    })
    for y in ("22", "23", "24"):
        out[f"rape{y}"] = g[f"RAPE{y}"].sum(min_count=1)
        out[f"ok{y}"] = g[f"FILTER{y}"].max() == 1
    return out.dropna(subset=["enrollment"])


def pct_below(values: np.ndarray, x: float) -> float:
    """Percent of institutions with a lower rate than x (ties count half)."""
    return float(((values < x).sum() + 0.5 * (values == x).sum()) / len(values) * 100)


def clean(v):
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (float, np.floating)):
        return None if pd.isna(v) else round(float(v), 4)
    return v


def rec(i, r, cols):
    return {"unitid": i, "name": r["name"], "state": r["state"], **{c: clean(r[c]) for c in cols}}


def table(df, cols):
    return [rec(i, r, cols) for i, r in df.iterrows()]


def dump(name, obj, indent=2):
    (OUT / name).write_text(json.dumps(obj, indent=indent) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", type=Path, default=DEFAULT_SRC)
    args = ap.parse_args()
    d = load(args.src)

    # ---- 2024 ----
    y24 = d[d.ok24 & d.rape24.notna()].copy()
    y24["rate24"] = y24.rape24 / y24.enrollment * 1e4
    y24["rank_raw"] = y24.rape24.rank(ascending=False, method="min").astype(int)
    broad = y24[y24.enrollment >= MIN_ENR_BROAD].copy()
    large = y24[y24.enrollment >= MIN_ENR_LARGE].copy()
    broad["rank_rate"] = broad.rate24.rank(ascending=False, method="min").astype(int)
    large["rank_rate"] = large.rate24.rank(ascending=False, method="min").astype(int)

    # ---- 2022-24 ----
    m_all = d[d.ok22 & d.ok23 & d.ok24 & d[["rape22", "rape23", "rape24"]].notna().all(axis=1)].copy()
    m_all["avg_rapes"] = m_all[["rape22", "rape23", "rape24"]].mean(axis=1)
    m_all["rate3"] = m_all.avg_rapes / m_all.enrollment * 1e4
    m = m_all[m_all.enrollment >= MIN_ENR_LARGE].copy()
    m["rank3"] = m.rate3.rank(ascending=False, method="min").astype(int)

    # ---- trend model (>=1,000): expected = pooled national rate x enrollment ----
    pooled = broad.rape24.sum() / broad.enrollment.sum()
    broad["expected"] = pooled * broad.enrollment
    broad["resid_z"] = (broad.rape24 - broad.expected) / np.sqrt(broad.expected)

    b = y24.loc[BYU]
    stats = {
        "source": "U.S. Dept. of Education, Campus Safety and Security (Clery Act) data, 2025 release (years 2022-2024), Oncampuscrime222324.xls",
        "byu_unitid": BYU,
        "n_four_year_institutions_with_2024_data": int(len(y24)),
        "n_ge_1000": int(len(broad)), "n_ge_5000": int(len(large)), "n_three_year_ge_5000": int(len(m)),
        "pooled_rate_per_10k_ge_1000": round(pooled * 1e4, 4),
        "byu": {
            "rapes_2024": int(b.rape24), "enrollment": int(b.enrollment), "rate_2024": round(float(b.rate24), 4),
            "rank_raw_2024": int(b.rank_raw), "of_raw": int(len(y24)),
            "rank_rate_ge_1000": int(broad.loc[BYU, "rank_rate"]), "of_ge_1000": int(len(broad)),
            "percentile_ge_1000": round(pct_below(broad.rate24.values, b.rate24), 1),
            "rank_rate_ge_5000": int(large.loc[BYU, "rank_rate"]), "of_ge_5000": int(len(large)),
            "percentile_ge_5000": round(pct_below(large.rate24.values, b.rate24), 1),
            "rapes_2022_24": [int(b.rape22), int(b.rape23), int(b.rape24)],
            "rate_3yr": round(float(m.loc[BYU, "rate3"]), 4), "rank_3yr": int(m.loc[BYU, "rank3"]),
            "of_3yr": int(len(m)),
            "percentile_3yr": round(pct_below(m.rate3.values, m.loc[BYU, "rate3"]), 1),
        },
        "distribution_ge_5000_2024": {
            "median": round(float(large.rate24.median()), 4), "mean": round(float(large.rate24.mean()), 4),
            "p90": round(float(large.rate24.quantile(.9)), 4), "max": round(float(large.rate24.max()), 4),
            "share_zero": round(float((large.rate24 == 0).mean() * 100), 1),
        },
        "distribution_3yr_ge_5000": {"median": round(float(m.rate3.median()), 4), "mean": round(float(m.rate3.mean()), 4)},
    }

    OUT.mkdir(parents=True, exist_ok=True)
    dump("stats.json", stats)
    cols_raw = ["rape24", "enrollment", "rate24", "rank_raw"]
    dump("raw-rapes-2024-top30.json", {
        "n": int(len(y24)),
        "rows": table(y24.sort_values(["rape24", "enrollment"], ascending=[False, False]).head(30), cols_raw),
        "byu": rec(BYU, b, cols_raw)})
    cols_rate = ["rape24", "enrollment", "rate24", "rank_rate"]
    dump("rate-2024-top30.json", {
        "min_enrollment": MIN_ENR_BROAD, "n": int(len(broad)), "median": round(float(broad.rate24.median()), 4),
        "rows": table(broad.sort_values("rate24", ascending=False).head(30), cols_rate),
        "byu": rec(BYU, broad.loc[BYU], cols_rate)})
    cols_m = ["rape22", "rape23", "rape24", "avg_rapes", "enrollment", "rate3", "rank3"]
    dump("rate-2022-24-top30.json", {
        "min_enrollment": MIN_ENR_LARGE, "n": int(len(m)), "median": stats["distribution_3yr_ge_5000"]["median"],
        "rows": table(m.sort_values("rate3", ascending=False).head(30), cols_m),
        "byu": rec(BYU, m.loc[BYU], cols_m)})
    dump("scatter-2024.json", {
        "min_enrollment": MIN_ENR_BROAD, "pooled_rate_per_10k": stats["pooled_rate_per_10k_ge_1000"],
        "points": table(broad, ["rape24", "enrollment", "expected", "resid_z"])}, indent=1)
    dump("histogram-2024.json", {
        "min_enrollment": MIN_ENR_LARGE,
        "rates": [round(float(x), 4) for x in large.rate24.sort_values()],
        "byu_rate": stats["byu"]["rate_2024"]}, indent=None)

    # ---- Utah only (all Utah four-year institutions with 1,000+ students) ----
    ut = y24[(y24.state == "UT") & (y24.enrollment >= MIN_ENR_BROAD)].copy()
    ut["rate24"] = ut.rape24 / ut.enrollment * 1e4
    ut["rank_raw"] = ut.rape24.rank(ascending=False, method="min").astype(int)
    ut["rank_rate"] = ut.rate24.rank(ascending=False, method="min").astype(int)
    ut3 = m_all[(m_all.state == "UT") & (m_all.enrollment >= MIN_ENR_BROAD)].copy()
    ut3["rank3"] = ut3.rate3.rank(ascending=False, method="min").astype(int)
    pooled_ut = ut.rape24.sum() / ut.enrollment.sum()
    ut["expected"] = pooled_ut * ut.enrollment
    ut_stats = {
        "min_enrollment": MIN_ENR_BROAD, "n": int(len(ut)), "n_3yr": int(len(ut3)),
        "median_rate_2024": round(float(ut.rate24.median()), 4), "median_rate_3yr": round(float(ut3.rate3.median()), 4),
        "pooled_rate_per_10k": round(pooled_ut * 1e4, 4),
        "byu": {"rank_raw": int(ut.loc[BYU, "rank_raw"]), "rank_rate": int(ut.loc[BYU, "rank_rate"]),
                "rank_3yr": int(ut3.loc[BYU, "rank3"]), "rate_2024": round(float(ut.loc[BYU, "rate24"]), 4),
                "rate_3yr": round(float(ut3.loc[BYU, "rate3"]), 4)},
    }
    dump("utah-stats.json", ut_stats)
    cu = ["rape24", "enrollment", "rate24", "rank_raw", "rank_rate", "expected"]
    dump("utah-2024.json", {**ut_stats, "rows": table(ut.sort_values(["rape24", "enrollment"], ascending=False), cu)})
    c3 = ["rape22", "rape23", "rape24", "avg_rapes", "enrollment", "rate3", "rank3"]
    dump("utah-2022-24.json", {**ut_stats, "rows": table(ut3.sort_values("rate3", ascending=False), c3)})

    print(json.dumps(stats, indent=2))
    print(json.dumps(ut_stats, indent=2))
    for t, df, c in (
        ("RAW top 30", y24.sort_values("rape24", ascending=False).head(30), ["name", "rape24", "enrollment", "rate24"]),
        ("RATE 2024 >=1000 top 30", broad.sort_values("rate24", ascending=False).head(30), ["name", "rape24", "enrollment", "rate24"]),
        ("3yr >=5000 top 30", m.sort_values("rate3", ascending=False).head(30), ["name", "rape22", "rape23", "rape24", "enrollment", "rate3"]),
        ("scatter outliers", broad.reindex(broad.resid_z.abs().sort_values(ascending=False).index).head(15), ["name", "rape24", "enrollment", "expected", "resid_z"]),
    ):
        print("\n==", t)
        print(df[c].round(2).to_string())


if __name__ == "__main__":
    main()

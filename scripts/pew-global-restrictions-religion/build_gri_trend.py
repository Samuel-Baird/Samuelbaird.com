"""
Builds the global-median Government Restrictions Index (GRI) time series,
2007-2022, from Pew Research Center's "Global Restrictions on Religion"
cumulative country-year dataset
(data/pew-global-restrictions-religion/PublicDataset_ReligiousRestrictions_2007to2022.csv,
gitignored, not committed).

This dataset is country/year-level - each row is one country-year (e.g.
"Afghanistan, 2007") rated 0-10 on the GRI (government restrictions) and
SHI (social hostilities) indexes. It carries no per-respondent religion
variable, so unlike the site's other Pew datasets there is no LDS-specific
breakout possible here. The codebook's GRI_Q_11_* columns (which religious
groups were harassed) break out only by broad tradition (e.g.
"Christianity"), not by denomination, so no Latter-day-Saint-specific
figure exists in this public release either.

The defensible flagship chart is therefore a worldwide trend, not a group
comparison: the global median GRI score, year by year, computed here
directly from the country-level rows (Pew's own reports use the median,
not the mean, as the headline global figure, since the country-level
distribution is right-skewed - a handful of severe outliers would pull a
mean up). Every year is a real Pew-published country-year rating, not an
interpolation, so every point is marked "reported".

Usage: python scripts/pew-global-restrictions-religion/build_gri_trend.py
"""
import json
from pathlib import Path

import pandas as pd

CSV_PATH = (
    Path(__file__).parent / ".." / ".." / "data" / "pew-global-restrictions-religion"
    / "PublicDataset_ReligiousRestrictions_2007to2022.csv"
).resolve()

OUT_PATH = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-global-restrictions-religion"
    / "gri-trend.json"
)


def main():
    df = pd.read_csv(CSV_PATH)

    by_year = df.groupby("Question_Year").agg(
        median_gri=("GRI", "median"),
        median_shi=("SHI", "median"),
        n_countries=("GRI", "count"),
    )

    years_sorted = sorted(int(y) for y in by_year.index)
    series = {}
    for y in years_sorted:
        row = by_year.loc[y]
        series[y] = {
            "median_gri": round(float(row["median_gri"]), 2),
            "median_shi": round(float(row["median_shi"]), 2),
            "n_countries": int(row["n_countries"]),
            "status": "reported",
        }

    out = {
        "sources_summary": [
            "Pew Research Center, \"Global Restrictions on Religion\" cumulative dataset, "
            "2007-2022 (PublicDataset_ReligiousRestrictions_2007to2022.csv), 198 countries "
            "and territories rated annually.",
            "https://www.pewresearch.org/religion/2024/12/18/government-restrictions-on-religion-stayed-at-peak-levels-globally-in-2022/",
        ],
        "method": "Each row in the raw dataset is one country-year, rated 0-10 on the "
                  "Government Restrictions Index (GRI). This series is the global median "
                  "GRI score across all 197-198 rated countries/territories for each year, "
                  "computed directly from the country-level rows (median, not mean, since "
                  "the distribution across countries is right-skewed - matching how Pew's "
                  "own published reports summarize the global trend). Every year is a real "
                  "Pew-coded rating; none are interpolated.",
        "year_order": years_sorted,
        "series": {str(y): series[y] for y in years_sorted},
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for y in years_sorted:
        r = series[y]
        print(f"{y}  GRI={r['median_gri']:.2f}  SHI={r['median_shi']:.2f}  n={r['n_countries']}")
    print(f"\nWrote {OUT_PATH}")


if __name__ == "__main__":
    main()

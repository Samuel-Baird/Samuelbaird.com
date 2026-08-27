"""
Builds a linear-trend projection of U.S. Church membership through 2050,
extending the companion "compiled timeline" chart (build_data.py). Method:

1. Fit an ordinary-least-squares line to the 14 Church-reported annual
   figures 2012-2025 (the longest run of fully solid, non-interpolated,
   non-rounded data in membership-by-year.json - see that file's own
   `status` field). This is a *reported-only* trend, not one contaminated
   by the earlier interpolated/rounded years.
2. Anchor the projection at the actual 2025 figure (not the fitted value
   at 2025, which differs slightly from actual - recent growth has been
   flatter than the 2012-2025 average) and extend forward at the fitted
   slope through 2050. This avoids a visible jump at the join.

This is a linear extrapolation of a 14-year average, not a demographic
forecast - it assumes the 2012-2025 average annual increase (~45,000/year)
continues unchanged. Actual U.S. membership growth has been decelerating
(2024 to 2025 was essentially flat), so 2050 could plausibly land lower
than this projection; the chart's own caption says so explicitly.

Usage: python scripts/us-membership-growth-2000-2025/build_projection.py
"""
import json

import numpy as np

HISTORY_JSON = "docs/datasets/us-membership-growth-2000-2025/membership-by-year.json"
TREND_FIT_YEARS = range(2012, 2026)  # the reported-only stretch used to fit the slope
PROJECT_THROUGH = 2050


def main():
    with open(HISTORY_JSON, encoding="utf-8") as f:
        history = json.load(f)

    series = history["series"]
    fit_years = list(TREND_FIT_YEARS)
    fit_values = [series[str(y)]["members"] for y in fit_years]
    slope, intercept = np.polyfit(fit_years, fit_values, 1)

    anchor_year = fit_years[-1]
    anchor_value = fit_values[-1]

    full_years = history["year_order"]
    out_series = {
        y: {"members": series[str(y)]["members"], "status": "reported"}
        for y in full_years
    }
    for y in range(anchor_year + 1, PROJECT_THROUGH + 1):
        projected = round(anchor_value + slope * (y - anchor_year))
        out_series[y] = {"members": projected, "status": "projected"}

    year_order = sorted(out_series)
    out = {
        "method": f"Ordinary-least-squares linear fit to the {len(fit_years)} Church-reported "
                  f"annual figures {fit_years[0]}-{fit_years[-1]} (slope ~{round(slope):,}/year), "
                  f"anchored at the actual {anchor_year} figure and extended to {PROJECT_THROUGH} "
                  "at that same slope. A linear extrapolation of a 14-year average, not a "
                  "demographic forecast - actual growth has been decelerating (2024 to 2025 was "
                  "essentially flat), so this likely overstates 2050 membership if that slowdown "
                  "continues.",
        "trend_fit_years": [fit_years[0], fit_years[-1]],
        "trend_slope_per_year": round(slope),
        "anchor_year": anchor_year,
        "anchor_value": anchor_value,
        "year_order": year_order,
        "series": {str(y): out_series[y] for y in year_order},
    }
    with open("docs/datasets/us-membership-growth-2000-2025/membership-projection-2050.json",
              "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for y in (2025, 2030, 2035, 2040, 2045, 2050):
        print(f"{y}  {out_series[y]['members']:>10,}  [{out_series[y]['status']}]")
    print("\nWrote docs/datasets/us-membership-growth-2000-2025/membership-projection-2050.json")


if __name__ == "__main__":
    main()

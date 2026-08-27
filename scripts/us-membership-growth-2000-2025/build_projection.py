"""
Builds a 2050 projection RANGE (not a single line) for U.S. Church
membership, extending the companion "compiled timeline" chart
(build_data.py). A single trend line turned out not to be defensible this
far out - see the two bounds below - so this produces a low/high band
instead, per the user's own call after reviewing both alternatives.

Two bounds, both anchored at the actual 2025 figure:

- HIGH: ordinary-least-squares linear fit to the 14 Church-reported
  annual figures 2012-2025 (slope ~45,000/year), extended unchanged to
  2050. This is what "the 2012-2025 average trend continues" implies.
- LOW: the year-over-year growth RATE (%) fit as a declining linear trend
  over the same 2012-2025 window, then compounded forward and floored at
  0% (never assumes outright membership decline, since nothing in the
  data supports that). This is what "the recent deceleration continues"
  implies - it hits its 0% floor around 2032 and stays flat after.

Neither bound is "the forecast" - a quadratic fit to the same 14 points
scores a better R² than either (0.99 vs the linear bound's 0.98), but
extrapolated 25 years out its negative curvature makes membership PEAK
around 2034 and then decline below today's level by 2050, a classic
polynomial-extrapolation artifact (a curve that fits the observed window
well can still do something absurd once extended far past it). The
declining-growth-rate bound avoids that reversal but is itself a weak fit
on the noisy year-over-year rate (R² ~0.41 on the rate series, pulled
around by the COVID-era dip and partial rebound). Given that, a range
between the two most defensible SIMPLE bounds communicates the real
uncertainty better than any single curve would.

Usage: python scripts/us-membership-growth-2000-2025/build_projection.py
"""
import json

import numpy as np

HISTORY_JSON = "docs/datasets/us-membership-growth-2000-2025/membership-by-year.json"
TREND_FIT_YEARS = range(2012, 2026)  # the reported-only stretch used to fit both bounds
PROJECT_THROUGH = 2050


def main():
    with open(HISTORY_JSON, encoding="utf-8") as f:
        history = json.load(f)

    series = history["series"]
    fit_years = np.array(list(TREND_FIT_YEARS), dtype=float)
    fit_values = np.array([series[str(int(y))]["members"] for y in fit_years], dtype=float)

    anchor_year = int(fit_years[-1])
    anchor_value = fit_values[-1]

    # HIGH bound: linear level fit, extended unchanged.
    high_slope, _ = np.polyfit(fit_years, fit_values, 1)

    # LOW bound: linear fit to the YoY growth RATE, compounded forward,
    # floored at 0% once the declining rate would otherwise go negative.
    pct = np.diff(fit_values) / fit_values[:-1]
    rate_years = fit_years[1:]
    rate_slope, rate_intercept = np.polyfit(rate_years, pct, 1)

    high_series = {anchor_year: anchor_value}
    low_series = {anchor_year: anchor_value}
    high_val = anchor_value
    low_val = anchor_value
    for y in range(anchor_year + 1, PROJECT_THROUGH + 1):
        high_val = anchor_value + high_slope * (y - anchor_year)
        high_series[y] = round(high_val)
        rate = max(rate_slope * y + rate_intercept, 0.0)
        low_val = low_val * (1 + rate)
        low_series[y] = round(low_val)

    history_years = history["year_order"]
    history_series = {
        y: {"members": series[str(y)]["members"], "status": "reported"} for y in history_years
    }

    range_years = list(range(anchor_year, PROJECT_THROUGH + 1))
    out = {
        "method": "Two bounds, not one line - see build_projection.py's own docstring for "
                  "why a single trend (linear or otherwise) wasn't defensible 25 years out. "
                  f"HIGH: linear fit to the 14 Church-reported figures {int(fit_years[0])}-"
                  f"{anchor_year} (slope ~{round(high_slope):,}/year), extended unchanged. "
                  "LOW: that same window's year-over-year growth rate, fit as a declining "
                  "linear trend and compounded forward, floored at 0% (reaches the floor "
                  f"around {round(-rate_intercept / rate_slope)}). Both anchored at the "
                  f"actual {anchor_year} figure.",
        "trend_fit_years": [int(fit_years[0]), anchor_year],
        "high_slope_per_year": round(high_slope),
        "low_rate_slope_per_year": rate_slope,
        "low_rate_intercept": rate_intercept,
        "low_rate_floor_year": round(-rate_intercept / rate_slope),
        "anchor_year": anchor_year,
        "anchor_value": anchor_value,
        "history_year_order": history_years,
        "history_series": history_series,
        "range_year_order": range_years,
        "range_series": {
            str(y): {"low": low_series[y], "high": high_series[y]} for y in range_years
        },
    }
    with open("docs/datasets/us-membership-growth-2000-2025/membership-projection-2050.json",
              "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for y in (2025, 2030, 2035, 2040, 2045, 2050):
        print(f"{y}  low={low_series[y]:>10,}  high={high_series[y]:>10,}")
    print("\nWrote docs/datasets/us-membership-growth-2000-2025/membership-projection-2050.json")


if __name__ == "__main__":
    main()

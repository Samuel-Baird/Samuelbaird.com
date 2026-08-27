"""
Builds the year-by-year U.S. Church membership series for the site's first
"mixed data" Data Explorer entry - a compiled timeline, not a single
survey's microdata. Every point below is a real reported (or Church-
published round-estimate) figure with its own citation; years with no
findable U.S.-only total anywhere (2001, 2003, 2005, 2007, 2011 - the
Church's annual General Conference statistical report only gives worldwide
totals for that era, and the print-only Deseret News Church Almanac isn't
text-searchable online) are linearly interpolated between their nearest
real neighbors and marked "interpolated" so the chart can render them
visibly differently and the alt text can say so explicitly - never present
an invented number as if it were reported.

Usage: python scripts/us-membership-growth-2000-2025/build_data.py
"""
import json

# Real points: (year, members, status, source, note). status is "reported"
# (an exact Church-published figure) or "rounded" (a real reported figure
# known only to the nearest 10,000, from a secondary compilation).
REPORTED = [
    (2000, 5_208_827, "reported",
     "2000 U.S. Religion Census (Association of Statisticians of American Religious "
     "Bodies), LDS Church self-report.", None),
    (2002, 5_410_000, "rounded",
     "Deseret News Church Almanac figure, as compiled by cumorah.com's LDS Church "
     "growth archive; known only to the nearest 10,000.", None),
    (2004, 5_600_000, "rounded",
     "Deseret News Church Almanac figure, as compiled by cumorah.com; known only to "
     "the nearest 10,000.", None),
    (2006, 5_780_000, "rounded",
     "Deseret News Church Almanac figure, as compiled by cumorah.com; known only to "
     "the nearest 10,000.", None),
    (2008, 5_970_000, "rounded",
     "Deseret News Church Almanac figure, as compiled by cumorah.com; known only to "
     "the nearest 10,000.", None),
    (2009, 6_058_907, "reported",
     "Deseret News 2011 Church Almanac, as compiled by rickety.us.", None),
    (2010, 6_144_582, "reported",
     "2010 U.S. Religion Census (Association of Statisticians of American Religious "
     "Bodies), LDS Church self-report.", None),
    (2012, 6_321_416, "reported", "Church newsroom country page.", None),
    (2013, 6_398_889, "reported", "Church newsroom country page.", None),
    (2014, 6_466_267, "reported", "Church newsroom country page.", None),
    (2015, 6_531_656, "reported", "Church newsroom country page.", None),
    (2016, 6_592_195, "reported", "Church newsroom country page.", None),
    (2017, 6_641_886, "reported", "Church newsroom country page.", None),
    (2018, 6_681_829, "reported", "Church newsroom country page.", None),
    (2019, 6_721_032, "reported", "Church newsroom country page.", None),
    (2020, 6_742_000, "reported", "Church newsroom country page.",
     "Published as a round number; the Church did not release an exact 2020 total."),
    (2021, 6_763_019, "reported", "Church newsroom country page.", None),
    (2022, 6_804_028, "reported", "Church newsroom country page.", None),
    (2023, 6_868_793, "reported", "Church newsroom country page.", None),
    (2024, 6_929_956, "reported", "Church newsroom country page.", None),
    (2025, 6_929_770, "reported", "Church newsroom country page.", "As of Oct. 13, 2025."),
]

FIRST_YEAR, LAST_YEAR = 2000, 2025


def main():
    known = {year: members for year, members, *_ in REPORTED}
    meta = {year: {"status": status, "source": source, "note": note}
            for year, members, status, source, note in REPORTED}

    known_years = sorted(known)
    series = {}
    for year in range(FIRST_YEAR, LAST_YEAR + 1):
        if year in known:
            series[year] = {"members": known[year], **meta[year]}
            continue
        lower = max(y for y in known_years if y < year)
        upper = min(y for y in known_years if y > year)
        frac = (year - lower) / (upper - lower)
        interpolated = round(known[lower] + frac * (known[upper] - known[lower]))
        series[year] = {
            "members": interpolated,
            "status": "interpolated",
            "source": f"Linearly interpolated between the {lower} and {upper} figures - "
                      f"no U.S.-only total for {year} was found in any available source.",
            "note": None,
        }

    years_sorted = sorted(series)
    out = {
        "sources_summary": [
            "Pew/ARDA 2000 and 2010 U.S. Religion Census (Church self-report).",
            "Deseret News Church Almanac figures (2002-2009), via cumorah.com's LDS "
            "Church growth archive and rickety.us.",
            "Church newsroom country page (2012-2025), via Wikipedia's \"United States "
            "membership statistics (LDS Church)\" compiled table: "
            "https://en.wikipedia.org/wiki/United_States_membership_statistics_(LDS_Church)",
            "https://newsroom.churchofjesuschrist.org/facts-and-statistics/country/united-states",
        ],
        "method": "This is a compiled timeline, not one survey's microdata - each point is a "
                  "separately cited Church-reported (or Church-published round estimate) "
                  "figure. 2001, 2003, 2005, 2007, and 2011 have no findable U.S.-only total "
                  "in any source checked and are linearly interpolated between their nearest "
                  "real neighbors; every other year is a real reported figure. See each "
                  "year's own `status` (reported/rounded/interpolated) and `source`.",
        "year_order": years_sorted,
        "series": {str(y): series[y] for y in years_sorted},
    }
    with open("docs/datasets/us-membership-growth-2000-2025/membership-by-year.json",
              "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for y in years_sorted:
        r = series[y]
        flag = "" if r["status"] == "reported" else f"  [{r['status']}]"
        print(f"{y}  {r['members']:>10,}{flag}")
    print("\nWrote docs/datasets/us-membership-growth-2000-2025/membership-by-year.json")


if __name__ == "__main__":
    main()

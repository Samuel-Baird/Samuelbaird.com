"""
Builds the Brazil year-by-year Church membership series - a compiled
historical timeline, not one survey's microdata, following the exact
pattern of scripts/us-membership-growth-2000-2025/build_data.py.

Unlike that U.S. series (a fixed annual 2000-2025 grid with only a handful
of interpolated gap years), this one is a much sparser historical
timeline: real reported/rounded figures exist as far back as 1940, but
the 2010-2024 stretch has only two more findable points (2010, 2019)
beyond the endpoints. Additional WebSearch/WebFetch attempts (Church
newsroom country page via Wayback Machine - blocked in this environment;
Wikipedia's "Membership statistics of the Church of Jesus Christ of
Latter-day Saints" full table; ldschurchgrowth.blogspot.com's annual
"Country-by-Country Membership Statistics" posts for 2019/2021/2022/2024,
which report Brazil's net numerical INCREASE for those years but not a
running total) did not turn up further exact annual totals for Brazil in
1940-1970, 1980-1988, 1990-1998, 2001-2008, 2011-2018, or 2020-2024. Per
this dataset's own sourcing rule, no interpolated or invented point is
added for those gaps - every point below is a real reported or
Church-published rounded figure with its own citation, and the chart
renders with genuinely irregular spacing rather than a fabricated-even
grid. See docs/datasets/lds-brazil-2022/README.md for the full citation
list.

Usage: python scripts/lds-brazil-2022/build_membership_by_year.py
"""
import json
from pathlib import Path

# (year, members, status, source). status is "reported" (an exact
# Church-published figure) or "rounded" (a real reported figure known
# only to the nearest thousand/ten-thousand, from a secondary compilation).
REPORTED = [
    (1940, 233, "reported",
     "Wikipedia, \"The Church of Jesus Christ of Latter-day Saints in Brazil,\" "
     "compiled historical timeline."),
    (1950, 648, "reported",
     "Wikipedia, \"The Church of Jesus Christ of Latter-day Saints in Brazil,\" "
     "compiled historical timeline."),
    (1960, 2_644, "reported",
     "Wikipedia, \"The Church of Jesus Christ of Latter-day Saints in Brazil,\" "
     "compiled historical timeline."),
    (1970, 33_104, "reported",
     "Wikipedia, \"The Church of Jesus Christ of Latter-day Saints in Brazil,\" "
     "compiled historical timeline."),
    (1979, 71_510, "reported",
     "Wikipedia, \"The Church of Jesus Christ of Latter-day Saints in Brazil,\" "
     "compiled historical timeline."),
    (1989, 302_000, "rounded",
     "Wikipedia, \"The Church of Jesus Christ of Latter-day Saints in Brazil\" - "
     "published as a rounded number."),
    (1999, 743_182, "reported",
     "Wikipedia, \"The Church of Jesus Christ of Latter-day Saints in Brazil,\" "
     "compiled historical timeline."),
    (2000, 775_822, "reported",
     "cumorah.com LDS Growth Case Studies (Matt Martinich), \"Expanding LDS "
     "Outreach in Brazil.\""),
    (2009, 1_102_674, "reported",
     "Wikipedia, \"The Church of Jesus Christ of Latter-day Saints in Brazil,\" "
     "compiled historical timeline."),
    (2010, 1_138_740, "reported",
     "cumorah.com LDS Growth Case Studies (Matt Martinich), \"Expanding LDS "
     "Outreach in Brazil.\""),
    (2019, 1_429_935, "reported",
     "Wikipedia, \"The Church of Jesus Christ of Latter-day Saints in Brazil,\" "
     "compiled historical timeline."),
    (2025, 1_573_360, "reported",
     "Church official facts-and-statistics page, as of Dec. 31, 2025: "
     "https://www.churchofjesuschrist.org/learn/facts-statistics/brazil?lang=eng"),
]


def main():
    year_order = [y for y, *_ in REPORTED]
    series = {
        year: {"members": members, "status": status, "source": source}
        for year, members, status, source in REPORTED
    }

    out = {
        "sources_summary": [
            "Wikipedia, \"The Church of Jesus Christ of Latter-day Saints in Brazil,\" "
            "compiled historical timeline (1940-1979, 1989, 1999, 2009, 2019): "
            "https://en.wikipedia.org/wiki/The_Church_of_Jesus_Christ_of_Latter-day_Saints_in_Brazil",
            "cumorah.com LDS Growth Case Studies (Matt Martinich), \"Expanding LDS "
            "Outreach in Brazil\" (2000, 2010): https://www.cumorah.com/articles/"
            "ldsGrowthCaseStudies/487?get_pdf=true",
            "Church official facts-and-statistics page (2025): "
            "https://www.churchofjesuschrist.org/learn/facts-statistics/brazil?lang=eng",
        ],
        "method": "A compiled historical timeline, not one survey's microdata - each "
                  "point is a separately cited Church-reported (or Church-published "
                  "rounded) figure, spaced irregularly across 1940-2025 rather than on "
                  "a fixed annual grid. No point is interpolated or estimated: years "
                  "with no findable real figure (most of 1940-2024 outside the points "
                  "listed here) are simply omitted rather than filled in. See each "
                  "year's own `source`.",
            "milestones": [
            {"year": 1966, "label": "First Brazilian stake organized (Sao Paulo)"},
            {"year": 1978, "label": "First temple in Brazil and South America dedicated (Sao Paulo)"},
            {"year": 1985, "label": "End of Brazil's military dictatorship"},
            {"year": 1993, "label": "Brazil becomes the 3rd country to reach 100 stakes"},
            {"year": 2025, "label": "Brazil overtakes Mexico in total membership"},
        ],
        "year_order": year_order,
        "series": {str(y): series[y] for y in year_order},
    }

    out_path = (
        Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "lds-brazil-2022"
        / "membership-by-year.json"
    ).resolve()
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for y in year_order:
        r = series[y]
        flag = "" if r["status"] == "reported" else f"  [{r['status']}]"
        print(f"{y}  {r['members']:>10,}{flag}")
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()

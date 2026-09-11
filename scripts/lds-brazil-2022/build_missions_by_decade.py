"""
Builds the Brazil LDS-mission-count series, 1950-2025 - real decade-by-decade
mission counts quoted verbatim from cumorah.com's "Reaching the Nations"
Brazil country report (Matt Martinich), plus the current 2025 figure from
the Church's official facts-and-statistics page. Same "sparse real points,
no interpolation" pattern as membership-by-year.json in this dataset -
see that build script's own docstring for the general approach.

Usage: python scripts/lds-brazil-2022/build_missions_by_decade.py
"""
import json
from pathlib import Path

# (year, missions, status, source)
REPORTED = [
    (1950, 1, "reported",
     "cumorah.com \"Reaching the Nations\" Brazil country report (Matt Martinich): "
     "\"The number of missions increased from one in 1950...\""),
    (1960, 2, "reported",
     "cumorah.com \"Reaching the Nations\" Brazil country report (Matt Martinich): "
     "\"...to two in 1960...\""),
    (1970, 3, "reported",
     "cumorah.com \"Reaching the Nations\" Brazil country report (Matt Martinich): "
     "\"...three in 1970...\""),
    (1980, 6, "reported",
     "cumorah.com \"Reaching the Nations\" Brazil country report (Matt Martinich): "
     "\"...six in 1980...\""),
    (1990, 12, "reported",
     "cumorah.com \"Reaching the Nations\" Brazil country report (Matt Martinich): "
     "\"...12 in 1990...\""),
    (2000, 26, "reported",
     "cumorah.com \"Reaching the Nations\" Brazil country report (Matt Martinich): "
     "\"...26 in 2000...\""),
    (2010, 27, "reported",
     "cumorah.com \"Reaching the Nations\" Brazil country report (Matt Martinich): "
     "\"...and 27 in 2010.\""),
    (2025, 37, "reported",
     "Church official facts-and-statistics page, as of Dec. 31, 2025: "
     "https://www.churchofjesuschrist.org/learn/facts-statistics/brazil?lang=eng"),
]


def main():
    year_order = [y for y, *_ in REPORTED]
    series = {
        year: {"missions": missions, "status": status, "source": source}
        for year, missions, status, source in REPORTED
    }

    out = {
        "sources_summary": [
            "cumorah.com \"Reaching the Nations\" Brazil country report (Matt Martinich), "
            "1950-2010: https://cumorah.com/countries/viewReports/191/Brazil",
            "Church official facts-and-statistics page (2025): "
            "https://www.churchofjesuschrist.org/learn/facts-statistics/brazil?lang=eng",
        ],
        "method": "8 real data points spanning 75 years, quoted directly from cumorah.com's "
                  "decade-by-decade sentence (1950-2010) plus the Church's own current figure "
                  "(2025). No point between these is interpolated or estimated - years with no "
                  "findable real figure are simply omitted, following the same rule as "
                  "membership-by-year.json in this dataset.",
        "year_order": year_order,
        "series": {str(y): series[y] for y in year_order},
    }

    out_path = (
        Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "lds-brazil-2022"
        / "missions-by-decade.json"
    ).resolve()
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for y in year_order:
        print(f"{y}  {series[y]['missions']:>3}")
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()

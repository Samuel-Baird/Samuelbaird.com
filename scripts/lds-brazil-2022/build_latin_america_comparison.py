"""
Builds the Brazil-vs-other-Latin-American-countries 2025 comparison
dataset: total Church membership as of Dec. 31, 2025, for the five
countries with the largest Latter-day Saint populations in Latin
America. All figures come straight from the Church's own official
facts-and-statistics pages (one per country) - a single-source snapshot,
not a compiled timeline like membership-by-year.json.

The headline: Brazil overtook Mexico in total membership in 2025 (by
1,073 members) to become the country with the most Latter-day Saints of
any nation outside the United States - noted by ldschurchgrowth.blogspot.com
as well as the Church's own per-country pages.

Usage: python scripts/lds-brazil-2022/build_latin_america_comparison.py
"""
import json
from pathlib import Path

# country -> (members, congregations, wards, branches, missions, temples, source_url)
COUNTRIES = {
    "Brazil": (1_573_360, 2_008, 1_650, 358, 37, 11,
               "https://www.churchofjesuschrist.org/learn/facts-statistics/brazil?lang=eng"),
    "Mexico": (1_572_287, 1_875, 1_401, 474, 34, 14,
               "https://www.churchofjesuschrist.org/learn/facts-statistics/mexico?lang=eng"),
    "Peru": (667_836, 809, 684, 125, 15, 4,
             "https://www.churchofjesuschrist.org/learn/facts-statistics/peru?lang=eng"),
    "Chile": (624_203, 578, 456, 122, 11, 3,
              "https://www.churchofjesuschrist.org/learn/facts-statistics/chile?lang=eng"),
    "Argentina": (505_819, 742, 506, 236, 14, 5,
                  "https://www.churchofjesuschrist.org/learn/facts-statistics/argentina?lang=eng"),
}

COUNTRY_ORDER = ["Brazil", "Mexico", "Peru", "Chile", "Argentina"]


def main():
    countries = {}
    for name in COUNTRY_ORDER:
        members, congregations, wards, branches, missions, temples, url = COUNTRIES[name]
        countries[name] = {
            "members": members,
            "congregations": congregations,
            "wards": wards,
            "branches": branches,
            "missions": missions,
            "operating_temples": temples,
            "source_url": url,
        }

    out = {
        "as_of": "December 31, 2025",
        "sources_summary": [
            "Church official facts-and-statistics pages, one per country, as of Dec. 31, "
            "2025 (churchofjesuschrist.org/learn/facts-statistics/<country>).",
            "http://ldschurchgrowth.blogspot.com/2026/04/country-by-country-membership.html "
            "(secondary source noting Brazil's overtake of Mexico).",
        ],
        "method": "Total Church membership, congregations (wards + branches), missions, "
                  "and operating temples for the five Latin American countries with the "
                  "largest Latter-day Saint populations, each pulled directly from that "
                  "country's own official Church facts-and-statistics page as of Dec. 31, "
                  "2025 - a single-source snapshot, not a compiled timeline.",
        "headline": "Brazil surpassed Mexico in total membership in 2025 (by 1,073 "
                    "members) to become the country with the most Latter-day Saints of "
                    "any nation outside the United States.",
        "country_order": COUNTRY_ORDER,
        "countries": countries,
    }

    out_path = (
        Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "lds-brazil-2022"
        / "latin-america-comparison-2025.json"
    ).resolve()
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for name in COUNTRY_ORDER:
        print(f"{name:>10}  {countries[name]['members']:>10,}")
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()

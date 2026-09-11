"""
Builds the Brazil temple-dedication series: a CUMULATIVE count of
dedicated Brazil temples by dedication year, 1978-2026. All 12 temples
currently dedicated in Brazil, cross-verified against the Church's
official chronology page and its temple list, plus a direct search
confirming the most recent dedication (Belo Horizonte, Aug 16, 2026).

Two calendar years each saw two dedications in the same year (Recife and
Porto Alegre, both Dec 2000; Rio de Janeiro and Belem, both 2022) - those
are collapsed into a single `year_order` entry each, carrying the
cumulative count *after* both that year's dedications, rather than two
separate points a day/months apart that would crowd the x-axis for no
real signal (the story here is dedication YEARS, not day-level spacing).
The `temples` list below keeps every individual temple's own date for
the dataset's README/alt-text, independent of the collapsed year series
used to plot the line itself.

Usage: python scripts/lds-brazil-2022/build_temples_dedicated_by_year.py
"""
import json
from pathlib import Path

# (name, dedicated date string, dedicated year) - in dedication order.
# Source: Church official chronology page
# (https://www.churchofjesuschrist.org/study/history/global-histories/brazil/br-chronology?lang=eng)
# and temple list (https://www.churchofjesuschrist.org/temples/list?lang=eng);
# #12 (Belo Horizonte) confirmed via Church Newsroom, "President Oaks
# Dedicates the Belo Horizonte Brazil Temple" - explicitly stated there as
# "the Church's 12th dedicated temple in Brazil."
TEMPLES = [
    ("Sao Paulo Brazil", "Oct 30, 1978", 1978),
    ("Recife Brazil", "Dec 15, 2000", 2000),
    ("Porto Alegre Brazil", "Dec 17, 2000", 2000),
    ("Campinas Brazil", "May 17, 2002", 2002),
    ("Curitiba Brazil", "Jun 1, 2008", 2008),
    ("Manaus Brazil", "Jun 10, 2012", 2012),
    ("Fortaleza Brazil", "Jun 2, 2019", 2019),
    ("Rio de Janeiro Brazil", "May 8, 2022", 2022),
    ("Belem Brazil", "Nov 20, 2022", 2022),
    ("Brasilia Brazil", "Sep 17, 2023", 2023),
    ("Salvador Brazil", "Oct 20, 2024", 2024),
    ("Belo Horizonte Brazil", "Aug 16, 2026", 2026),
]

SOURCE = (
    "Church official chronology page (Brazil) and temple list, "
    "churchofjesuschrist.org; #12 confirmed via Church Newsroom, "
    "\"President Oaks Dedicates the Belo Horizonte Brazil Temple.\""
)


def main():
    # Collapse same-year dedications into one point, carrying the running
    # cumulative total after all of that year's dedications.
    year_order: list[int] = []
    cumulative_by_year: dict[int, int] = {}
    running = 0
    for _name, _date, year in TEMPLES:
        running += 1
        if year not in cumulative_by_year:
            year_order.append(year)
        cumulative_by_year[year] = running

    series = {
        str(y): {"count": cumulative_by_year[y], "status": "reported", "source": SOURCE}
        for y in year_order
    }

    # Sanity-check the "5 of 12 dedicated in the last 4 years" claim
    # (2022-2026 inclusive) directly from TEMPLES rather than trusting any
    # prior prose count.
    recent = [name for name, _date, year in TEMPLES if 2022 <= year <= 2026]
    assert len(recent) == 5, f"expected 5 temples dedicated 2022-2026, got {len(recent)}: {recent}"

    out = {
        "sources_summary": [
            "Church official chronology page (Brazil): "
            "https://www.churchofjesuschrist.org/study/history/global-histories/brazil/br-chronology?lang=eng",
            "Church official temple list: "
            "https://www.churchofjesuschrist.org/temples/list?lang=eng",
            "Church Newsroom, \"President Oaks Dedicates the Belo Horizonte Brazil Temple\": "
            "https://newsroom.churchofjesuschrist.org/article/president-oaks-dedicates-belo-horizonte-brazil-temple",
        ],
        "method": "Every currently-dedicated Brazil temple (12 as of this writing), each with its "
                  "own exact dedication date, cross-verified against the Church's own chronology "
                  "and temple-list pages. This is a real, complete count of DEDICATED temples only "
                  "- temples under construction or merely announced are not counted here (see "
                  "`under_construction_or_announced` below). No point is interpolated or "
                  "estimated. Two calendar years (2000, 2022) saw two dedications each, collapsed "
                  "into one plotted point carrying that year's ending cumulative total - see "
                  "`temples` for each individual dedication.",
        "temples": [
            {"name": name, "dedicated": date, "year": year}
            for name, date, year in TEMPLES
        ],
        "under_construction_or_announced": {
            "under_construction": ["Natal", "Teresina", "Santos", "Joao Pessoa",
                                    "Ribeirao Preto", "Londrina"],
            "announced": ["Maceio", "Campo Grande", "Florianopolis", "Sao Paulo East",
                          "Goiania", "Vitoria"],
            "note": "Not counted in the chart itself - only dedicated temples are plotted as "
                    "completed milestones.",
        },
        "year_order": year_order,
        "series": series,
    }

    out_path = (
        Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "lds-brazil-2022"
        / "temples-dedicated-by-year.json"
    ).resolve()
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for y in year_order:
        print(f"{y}  cumulative={cumulative_by_year[y]}")
    print(f"\n2022-2026 dedications: {len(recent)} ({', '.join(recent)})")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Party ID (pid7) over time, by religious tradition — the pending item at
docs/datasets/ryan-burge/GRAPHICS_TODO.md's "CES stacked — party ID over
time" section.

Reads the CES stacked 2006-2018 extract (5 columns: trad, pid7, race,
gender, year; no weight column) and writes mean pid7 per year for a
hand-picked group set, per the backlog's NEEDS DESIGN DECISION resolution:
generic RELTRAD collapsing would erase LDS entirely, so this hand-picks
named groups the way the Pew switching-rates chart does.

Group set (design decision, noted here and in the shipped chart's caption):
Mormon (LDS), Catholic, Southern Baptist, United Methodist, Nothing in
Particular, Atheist, and Jewish — the last aggregated across the file's five
Jewish denominational rows (Conservative/Orthodox/Other/Reconstructionist/
Reformed Jew), since the raw `trad` column has no single unified "Jewish"
category.

Usage: python scripts/ryan-burge/pid_over_time.py
Writes: docs/datasets/ryan-burge/pid-over-time.json
"""

import csv
import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "data" / "ryan-burge" / "tier1-strong" / "ces_stacked_2006-2018_css_small.csv"
OUT = ROOT / "docs" / "datasets" / "ryan-burge" / "pid-over-time.json"

# 7-point party ID, Strong Democrat=-3 .. Strong Republican=+3. "NA" rows are
# excluded entirely rather than treated as a midpoint - a skipped question is
# not the same claim as "exactly independent".
PID7_SCORE = {
    "Strong Democrat": -3,
    "Not Very Strong Dem.": -2,
    "Lean Democrat": -1,
    "Independent": 0,
    "Lean Republican": 1,
    "Not Very Strong Rep.": 2,
    "Strong Republican": 3,
}

# Display label -> set of raw `trad` values it aggregates.
GROUPS = {
    "Latter-day Saint": {"Mormon"},
    "Catholic": {"Catholic"},
    "Southern Baptist": {"Southern Baptist"},
    "United Methodist": {"United Methodist"},
    "Nothing in Particular": {"Nothing in Particular"},
    "Atheist": {"Atheist"},
    "Jewish": {
        "Conservative Jew",
        "Orthodox Jew",
        "Other Jew",
        "Reconstructionist Jew",
        "Reformed Jew",
    },
}

TRAD_TO_GROUP = {trad: label for label, trads in GROUPS.items() for trad in trads}


def main() -> None:
    if not SRC.exists():
        raise SystemExit(
            f"Source CSV not found: {SRC}\n"
            "This file is gitignored and lives only on machines with the "
            "data/ryan-burge/ extract checked out locally."
        )

    # values[label][year] -> list of pid7 scores
    values: dict[str, dict[int, list[int]]] = {label: {} for label in GROUPS}
    years: set[int] = set()

    with SRC.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            label = TRAD_TO_GROUP.get(row["trad"])
            if label is None:
                continue
            pid_raw = row["pid7"].replace("\n", " ").strip()
            score = PID7_SCORE.get(pid_raw)
            if score is None:
                continue  # "NA" or unrecognized
            year = int(row["year"])
            years.add(year)
            values[label].setdefault(year, []).append(score)

    waves = sorted(years)
    series = {}
    for label in GROUPS:
        by_year = values[label]
        series[label] = {
            "values": [
                round(statistics.mean(by_year[y]), 3) if by_year.get(y) else None
                for y in waves
            ],
            "n": [len(by_year.get(y, [])) for y in waves],
        }

    out = {
        "source": "Cooperative Election Studies (CCES/CES common content), 2006-2018",
        "via": "Ryan Burge (github.com/ryanburge/pets)",
        "method": (
            "Mean 7-point party ID (Strong Democrat=-3 .. Strong Republican=+3, "
            "Independent=0) per year, within a hand-picked group set. This "
            "extract carries no survey weight column, so every number here is "
            "unweighted -- read it for shape and direction, not a number that "
            "needs to be exact. \"Jewish\" aggregates five denominational rows "
            "in the source (Conservative/Orthodox/Other/Reconstructionist/"
            "Reformed Jew); every other group is a single raw `trad` value."
        ),
        "group_set_note": (
            "Standard RELTRAD would collapse everything outside Protestant/"
            "Catholic into \"other faith\", erasing LDS entirely, so this "
            "chart hand-picks named groups instead, the way the Pew "
            "switching-rates chart does."
        ),
        "waves": waves,
        "series": series,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} ({len(waves)} waves, {len(GROUPS)} groups)")


if __name__ == "__main__":
    main()

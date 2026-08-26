#!/usr/bin/env python3
"""Renders the nine VOTER Panel "heatmap matrix" idea graphics
(docs/datasets/ryan-burge/VOTER_PANEL_IDEAS.md, ideas 7/8/9/11/12/14/16/17/18).

Reads the nine docs/datasets/ryan-burge/voter-ideas-*.json files produced
by scripts/ryan-burge/voter_ideas_matrices.py - no number here is
hand-typed. Reuses render_heatmap() from render_voter_matrices.py (the
already-shipped feeling-thermometer/issue-importance matrices) rather than
redefining the same chart shape a second time.

Usage: python render_voter_ideas_matrices.py --out-dir ../../public/data-explorer/voter-survey-panel
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from render_voter_matrices import DEFAULT_FONTS_DIR, load_fonts, render_heatmap

DEFAULT_DATA_DIR = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "ryan-burge"
).resolve()

# (json stem, output filename, title, subtitle, value_min, value_max, unit)
CHARTS = [
    ("voter-ideas-sexism", "idea-sexism.png",
     "Gender-role attitudes, by religion",
     "Share who strongly or somewhat agree with each statement (2016 wave).", 0, 100, "%"),
    ("voter-ideas-muslim-distrust", "idea-muslim-distrust.png",
     "Muslim surveillance proposals, by religion",
     "Share who strongly or somewhat agree with each proposal (2017 wave).", 0, 100, "%"),
    ("voter-ideas-immigration", "idea-immigration.png",
     "Views of immigrants, by religion",
     "Share holding the pro-immigrant view on each measure (2017 wave).", 0, 100, "%"),
    ("voter-ideas-trade", "idea-trade.png",
     "Free trade attitudes, by religion",
     "Share holding the positive-for-consumers view on each effect (2016 wave).", 0, 100, "%"),
    ("voter-ideas-promises", "idea-promises.png",
     "Support for Trump's specific promises, by religion",
     "Share who support each promise (2017 wave).", 0, 100, "%"),
    ("voter-ideas-media", "idea-media.png",
     "Evening news viewership, by religion",
     "Share who watch each program (baseline wave, ~2011).", 0, 100, "%"),
    ("voter-ideas-orgs", "idea-orgs.png",
     "Organization membership, by religion",
     "Share who are a member of each organization (baseline wave, ~2011).", 0, 100, "%"),
    ("voter-ideas-volunteering", "idea-volunteering.png",
     "Volunteering by cause, by religion",
     "Share who volunteered for each type of cause in the past 12 months (baseline wave).",
     0, 100, "%"),
    ("voter-ideas-pride", "idea-pride.png",
     "National pride, by religion",
     "Share very or somewhat proud of America on each dimension (2016 wave).", 0, 100, "%"),
]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    ap.add_argument("--fonts-dir", type=Path, default=DEFAULT_FONTS_DIR)
    args = ap.parse_args()
    fonts = load_fonts(args.fonts_dir)

    for stem, filename, title, subtitle, vmin, vmax, unit in CHARTS:
        with open(args.data_dir / f"{stem}.json", encoding="utf-8") as f:
            data = json.load(f)
        excluded_note = "Too thin to show individually: " + ", ".join(data["excluded_too_thin"].values()) + "."
        note = f"Population: {data['wave_note']}. {excluded_note} {data['note']}"
        render_heatmap(
            data["matrix"], data["target_order"], data["group_order"], vmin, vmax, unit,
            title=title, subtitle=subtitle, note=note,
            out_path=args.out_dir / filename, fonts=fonts,
        )


if __name__ == "__main__":
    main()

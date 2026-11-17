#!/usr/bin/env python3
"""Renders the four "CCES 2016 by religion" PNGs added after the original
eight: 2016 presidential vote choice (a four-segment distribution stack:
Trump / Clinton / McMullin / Other candidate) and three gun-regulation
support items (magnitude bars). Reads only
docs/datasets/ryan-burge/cces2016-vote-guns.json (produced by
scripts/ryan-burge/cces2016_vote_guns.py) - no number here is hand-typed.

Reuses render_cces2016_by_religion_charts.py's own shapes rather than
re-implementing them: `render_magnitude_bar` as-is, and
`render_distribution_stack` with explicit nominal segment colors, since
vote choice is not an ordered scale and the default ordinal blue ramp
would falsely read as light-to-dark "more". Segment colors follow
render_pid_by_gender_chart.py's documented party convention (`--accent`
for the Democratic candidate, `--honey` for the Republican, the bar-safe
muted gray for everyone else - not literal red/blue), plus
chart_style.DIV_POS_GREEN for McMullin so the one segment that is the
story (14% of Latter-day Saint voters, under 1% of every other group)
reads as its own thing rather than blending into "Other candidate".

Usage:
  python scripts/ryan-burge/render_cces2016_vote_guns_charts.py \
    --out-dir public/data-explorer/cces-2016
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_cces2016_by_religion_charts import (  # noqa: E402
    DEFAULT_FONTS_DIR, load_fonts, render_distribution_stack, render_magnitude_bar,
)
from render_pid_by_gender_chart import DEM_COLOR, IND_COLOR, REP_COLOR, TEXT_ON_FILL  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from chart_style import DIV_POS_GREEN, INK  # noqa: E402

DEFAULT_DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "ryan-burge" / "cces2016-vote-guns.json"
).resolve()

VOTE_COLORS = {
    "Trump": REP_COLOR,
    "Clinton": DEM_COLOR,
    "McMullin": DIV_POS_GREEN,
    "Other candidate": IND_COLOR,
}
VOTE_TEXT_COLORS = {
    "Trump": TEXT_ON_FILL,
    "Clinton": TEXT_ON_FILL,
    "McMullin": TEXT_ON_FILL,
    "Other candidate": INK,
}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DEFAULT_DATA_JSON)
    ap.add_argument("--fonts-dir", type=Path, default=DEFAULT_FONTS_DIR)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)
    fonts = load_fonts(args.fonts_dir)
    total_n = data["total_n"]
    note = "Population: all 12 religpew categories, shown individually (not collapsed)."
    order = data["vote16_order"]

    render_distribution_stack(
        data["vote16_distribution"], order,
        title="2016 presidential vote, by religion",
        subtitle="Among respondents who named a candidate they voted for.\nJohnson, Stein, and other write-ins combined as “Other candidate.”",
        note=note, total_n=total_n, out_path=args.out_dir / "vote-2016.png", fonts=fonts,
        seg_colors=[VOTE_COLORS[s] for s in order],
        seg_text_colors=[VOTE_TEXT_COLORS[s] for s in order],
    )
    render_magnitude_bar(
        data["background_support"],
        title="Background checks for all gun sales",
        subtitle="Share who support background checks for all sales, including\nat gun shows and over the Internet.",
        note=note, total_n=total_n, out_path=args.out_dir / "gun-background-checks.png", fonts=fonts,
    )
    render_magnitude_bar(
        data["assaultban_support"],
        title="Ban assault rifles",
        subtitle="Share who support banning assault rifles.",
        note=note, total_n=total_n, out_path=args.out_dir / "gun-assault-ban.png", fonts=fonts,
    )
    render_magnitude_bar(
        data["conceal_support"],
        title="Make concealed-carry permits easier to get",
        subtitle="Share who support making it easier for people to obtain a\nconcealed-carry permit.",
        note=note, total_n=total_n, out_path=args.out_dir / "gun-concealed-carry.png", fonts=fonts,
    )


if __name__ == "__main__":
    main()

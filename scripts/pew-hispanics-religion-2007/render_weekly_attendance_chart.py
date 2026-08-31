#!/usr/bin/env python3
"""Renders the "Weekly attendance" PNG for the 2007 Pew Hispanic Center/Pew
Forum "Changing Faiths" survey. Reads only
docs/datasets/pew-hispanics-religion-2007/weekly-attendance.json (produced
by weekly_attendance.py in this folder). Uses the shared magnitude-bar
shape in scripts/flagship-charts/.

Usage:
  python scripts/pew-hispanics-religion-2007/render_weekly_attendance_chart.py \
    --out public/data-explorer/pew-hispanics-religion-2007/weekly-attendance.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-hispanics-religion-2007"
    / "weekly-attendance.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["group_order"]
    values = {r: data["weekly_or_more"][r]["pct"] for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        group_identity=True,
        title="Who's in the pews every week",
        subtitle="Share of U.S. Latino adults attending religious services at\nleast once a week, by religious group, 2006.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew Hispanic/Pew Forum Latino Religion Survey (2007)",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()

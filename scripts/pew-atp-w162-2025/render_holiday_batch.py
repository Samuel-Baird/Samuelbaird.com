#!/usr/bin/env python3
"""Renders the two holiday-batch PNGs for ATP Wave 162 from
docs/datasets/pew-atp-w162-2025/holiday-batch.json (produced by
holiday_batch.py). Same shared magnitude-bar shape / row-order rule as
scripts/pew-atp-w143-2024/render_holiday_batch.py.

Usage: python scripts/pew-atp-w162-2025/render_holiday_batch.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from chart_style import sort_groups  # noqa: E402

DATA = Path("docs/datasets/pew-atp-w162-2025/holiday-batch.json")
OUT_DIR = Path("public/data-explorer/pew-atp-w162-2025")

CHARTS = [
    dict(
        key="religion_culture_conflict", out="religion-culture-conflict.png",
        title="Do your beliefs conflict with mainstream culture?",
        subtitle="Share saying there is a great deal or some conflict between\ntheir own religious beliefs and mainstream American culture,\nby religion, February 2025.",
    ),
    dict(
        key="devotion_to_saints_weekly_plus", out="devotion-to-saints.png",
        title="Who practices devotion to saints?",
        subtitle="Share practicing devotion to the Virgin Mary or a favorite\nsaint at least weekly, by religion, February 2025.",
    ),
]


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    fonts = load_fonts()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for spec in CHARTS:
        results = data[spec["key"]]
        values = {r: results[r]["pct"] for r in results}
        rows = sort_groups(list(results.keys()), lambda r: values[r])
        render_magnitude_bar(
            rows=rows,
            values=values,
            highlight_rows=None,
            group_identity=True,
            title=spec["title"],
            subtitle=spec["subtitle"],
            caption_paragraphs=[],
            handle="@ithinkisam | data: Pew ATP Wave 162 (2025)",
            out_path=OUT_DIR / spec["out"],
            fonts=fonts,
        )


if __name__ == "__main__":
    main()

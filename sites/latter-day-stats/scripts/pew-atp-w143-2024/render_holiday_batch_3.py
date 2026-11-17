#!/usr/bin/env python3
"""Renders the two third-batch holiday PNGs for ATP Wave 143 from
docs/datasets/pew-atp-w143-2024/holiday-batch-3.json (produced by
holiday_batch_3.py). Same shared magnitude-bar shape / row-order rule as
render_holiday_batch.py in this folder.

Usage: python scripts/pew-atp-w143-2024/render_holiday_batch_3.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from chart_style import sort_groups  # noqa: E402

DATA = Path("docs/datasets/pew-atp-w143-2024/holiday-batch-3.json")
OUT_DIR = Path("public/data-explorer/pew-atp-w143-2024")

CHARTS = [
    dict(
        key="discrimination_against_black_americans", out="discrimination-against-black-americans.png",
        title="Discrimination against Black Americans?",
        subtitle="Share saying Black people face \"a lot\" of discrimination\nin society today, by religion, February 2024.",
    ),
    dict(
        key="wears_religious_items", out="wears-religious-items.png",
        title="Who wears religious items or symbols?",
        subtitle="Share who wear or carry religious items or symbols,\nby religion, February 2024.",
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
            handle="@ithinkisam | data: Pew ATP Wave 143 (2024)",
            out_path=OUT_DIR / spec["out"],
            fonts=fonts,
        )


if __name__ == "__main__":
    main()

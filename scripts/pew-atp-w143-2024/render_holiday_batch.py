#!/usr/bin/env python3
"""Renders the four holiday-batch PNGs for ATP Wave 143 from
docs/datasets/pew-atp-w143-2024/holiday-batch.json (produced by
holiday_batch.py). Same shared magnitude-bar shape / row-order rule as
render_religious_minority_chart.py in this folder.

Usage: python scripts/pew-atp-w143-2024/render_holiday_batch.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from chart_style import sort_groups  # noqa: E402

DATA = Path("docs/datasets/pew-atp-w143-2024/holiday-batch.json")
OUT_DIR = Path("public/data-explorer/pew-atp-w143-2024")

CHARTS = [
    dict(
        key="fasts_for_holy_times", out="fasts-for-holy-times.png",
        title="Who fasts for holy times?",
        subtitle="Share who fast for certain periods during holy times,\nby religion, February 2024.",
    ),
    dict(
        key="lights_candles_incense", out="lights-candles-incense.png",
        title="Who lights candles or incense?",
        subtitle="Share who light incense or candles for spiritual or\nreligious reasons, by religion, February 2024.",
    ),
    dict(
        key="discrimination_against_muslims", out="discrimination-against-muslims.png",
        title="Discrimination against Muslims?",
        subtitle="Share saying Muslims face \"a lot\" of discrimination\nin society today, by religion, February 2024.",
    ),
    dict(
        key="discrimination_against_jews", out="discrimination-against-jews.png",
        title="Discrimination against Jewish Americans?",
        subtitle="Share saying Jewish people face \"a lot\" of discrimination\nin society today, by religion, February 2024.",
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

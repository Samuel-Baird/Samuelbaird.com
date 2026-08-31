#!/usr/bin/env python3
"""Renders the four second-batch holiday PNGs for ATP Wave 143 from
docs/datasets/pew-atp-w143-2024/holiday-batch-2.json (produced by
holiday_batch_2.py). Same shared magnitude-bar shape / row-order rule as
render_holiday_batch.py in this folder.

Usage: python scripts/pew-atp-w143-2024/render_holiday_batch_2.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from chart_style import sort_groups  # noqa: E402

DATA = Path("docs/datasets/pew-atp-w143-2024/holiday-batch-2.json")
OUT_DIR = Path("public/data-explorer/pew-atp-w143-2024")

CHARTS = [
    dict(
        key="president_strong_beliefs_important", out="president-strong-beliefs.png",
        title="Want a president with strong religious beliefs?",
        subtitle="Share saying it's very important to have a president with\nstrong religious beliefs, even if different from their own,\nby religion, February 2024.",
    ),
    dict(
        key="president_same_beliefs_important", out="president-same-beliefs.png",
        title="Want a president who shares your beliefs?",
        subtitle="Share saying it's very important to have a president whose\nreligious beliefs are the same as their own, by religion, February 2024.",
    ),
    dict(
        key="definitely_life_after_death", out="definitely-life-after-death.png",
        title="Is there definitely life after death?",
        subtitle="Share saying there is definitely life after death,\nby religion, February 2024.",
    ),
    dict(
        key="believe_ancestor_spirits", out="believe-ancestor-spirits.png",
        title="Can ancestors' spirits help or harm you?",
        subtitle="Share who believe the spirits of ancestors can help or\nharm them, by religion, February 2024.",
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

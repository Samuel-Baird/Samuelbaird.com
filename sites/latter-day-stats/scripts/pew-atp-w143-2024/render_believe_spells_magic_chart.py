#!/usr/bin/env python3
"""Renders the believe-spells-magic PNG for ATP Wave 143 from
docs/datasets/pew-atp-w143-2024/believe-spells-magic.json (produced by
believe_spells_magic.py). Same shared magnitude-bar shape / row-order rule
as render_holiday_batch_4.py in this folder.

Usage: python scripts/pew-atp-w143-2024/render_believe_spells_magic_chart.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from chart_style import sort_groups  # noqa: E402

DATA = Path("docs/datasets/pew-atp-w143-2024/believe-spells-magic.json")
OUT_DIR = Path("public/data-explorer/pew-atp-w143-2024")


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    fonts = load_fonts()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    results = data["believes_in_spells_magic"]
    values = {r: results[r]["pct"] for r in results}
    rows = sort_groups(list(results.keys()), lambda r: values[r])
    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        group_identity=True,
        title="Who believes in spells, curses, or magic?",
        subtitle="Share who believe spells, curses, or other magic can\ninfluence people's lives, by religion, February 2024.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew ATP Wave 143 (2024)",
        out_path=OUT_DIR / "believe-spells-magic.png",
        fonts=fonts,
    )


if __name__ == "__main__":
    main()

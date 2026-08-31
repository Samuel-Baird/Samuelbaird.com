#!/usr/bin/env python3
"""Renders the three adult-arrangements PNGs from
docs/datasets/pew-catholic-family-2015/adult-arrangements.json (produced by
adult_arrangements.py). Same shared magnitude-bar shape / row-order rule as
render_household_types.py in this folder.

Usage: python scripts/pew-catholic-family-2015/render_adult_arrangements.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from chart_style import sort_groups  # noqa: E402

DATA = Path("docs/datasets/pew-catholic-family-2015/adult-arrangements.json")
OUT_DIR = Path("public/data-explorer/pew-catholic-family-2015")

CHARTS = [
    dict(
        key="unmarried_cohabiting_couple", out="unmarried-cohabiting-couple.png",
        title="An unmarried couple living together?",
        subtitle="Share saying this is as good a way of life as any\nother, by religion, 2015.",
    ),
    dict(
        key="samesex_couple_living_together", out="samesex-couple-living-together.png",
        title="A same-sex couple living together?",
        subtitle="Share saying this is as good a way of life as any\nother, by religion, 2015.",
    ),
    dict(
        key="childless_by_choice", out="childless-by-choice.png",
        title="A couple who choose not to have children?",
        subtitle="Share saying this is as good a way of life as any\nother, by religion, 2015.",
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
            handle="@ithinkisam | data: Pew Catholics & Family Life (2015)",
            out_path=OUT_DIR / spec["out"],
            fonts=fonts,
        )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Renders the five household-types PNGs from
docs/datasets/pew-catholic-family-2015/household-types.json (produced by
household_types.py). Same shared magnitude-bar shape / row-order rule as
scripts/pew-atp-w143-2024/render_holiday_batch.py.

Usage: python scripts/pew-catholic-family-2015/render_household_types.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from chart_style import sort_groups  # noqa: E402

DATA = Path("docs/datasets/pew-catholic-family-2015/household-types.json")
OUT_DIR = Path("public/data-explorer/pew-catholic-family-2015")

CHARTS = [
    dict(
        key="raised_by_married_mother_father", out="raised-by-married-mother-father.png",
        title="Raised by a married mother and father?",
        subtitle="Share saying this is as good an arrangement for raising\nchildren as any other, by religion, 2015.",
    ),
    dict(
        key="raised_by_single_parent", out="raised-by-single-parent.png",
        title="Raised by a single parent?",
        subtitle="Share saying this is as good an arrangement for raising\nchildren as any other, by religion, 2015.",
    ),
    dict(
        key="raised_by_divorced_parents", out="raised-by-divorced-parents.png",
        title="Raised by divorced parents?",
        subtitle="Share saying this is as good an arrangement for raising\nchildren as any other, by religion, 2015.",
    ),
    dict(
        key="raised_by_cohabiting_unmarried_parents", out="raised-by-cohabiting-unmarried-parents.png",
        title="Raised by unmarried parents living together?",
        subtitle="Share saying this is as good an arrangement for raising\nchildren as any other, by religion, 2015.",
    ),
    dict(
        key="raised_by_gay_lesbian_couple", out="raised-by-gay-lesbian-couple.png",
        title="Raised by a gay or lesbian couple?",
        subtitle="Share saying this is as good an arrangement for raising\nchildren as any other, by religion, 2015.",
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

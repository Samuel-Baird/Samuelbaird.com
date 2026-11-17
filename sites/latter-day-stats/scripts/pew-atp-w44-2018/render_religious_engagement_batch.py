#!/usr/bin/env python3
"""Renders the three religious-engagement PNGs for ATP Wave 44 from
docs/datasets/pew-atp-w44-2018/religious-engagement-batch.json (produced
by religious_engagement_batch.py). Same shared magnitude-bar shape / row-
order rule as render_knowledge_batch.py in this folder.

Usage: python scripts/pew-atp-w44-2018/render_religious_engagement_batch.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from chart_style import sort_groups  # noqa: E402

DATA = Path("docs/datasets/pew-atp-w44-2018/religious-engagement-batch.json")
OUT_DIR = Path("public/data-explorer/pew-atp-w44-2018")

CHARTS = [
    dict(
        key="learns_about_own_religion_weekly_plus", out="learns-about-own-religion-weekly.png",
        title="Who studies their own faith weekly?",
        subtitle="Share who do things to learn about their own religion\n(reading scripture, podcasts, books) at least weekly, by religion, February 2019.",
    ),
    dict(
        key="personally_knows_a_mormon", out="personally-knows-a-mormon.png",
        title="Who personally knows a Mormon?",
        subtitle="Share who personally know someone who is Mormon,\nby the respondent's own religion, February 2019.",
    ),
    dict(
        key="religious_ed_4plus_years", out="religious-ed-4plus-years.png",
        title="Who had years of religious education?",
        subtitle="Share who attended Sunday school, CCD, or other\nreligious education for 4 or more years, by religion, February 2019.",
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
            handle="@ithinkisam | data: Pew ATP Wave 44 (2019)",
            out_path=OUT_DIR / spec["out"],
            fonts=fonts,
        )


if __name__ == "__main__":
    main()

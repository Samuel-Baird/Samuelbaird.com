#!/usr/bin/env python3
"""Renders the five second-batch PNGs for ATP Wave 44 from
docs/datasets/pew-atp-w44-2018/knowledge-batch-2.json (produced by
knowledge_batch_2.py). Same shared magnitude-bar shape / row-order rule /
caption handle as render_knowledge_batch.py in this folder.

Usage: python scripts/pew-atp-w44-2018/render_knowledge_batch_2.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from chart_style import sort_groups  # noqa: E402

DATA = Path("docs/datasets/pew-atp-w44-2018/knowledge-batch-2.json")
OUT_DIR = Path("public/data-explorer/pew-atp-w44-2018")

CHARTS = [
    dict(
        key="knows_sermon_on_mount_jesus", out="knows-sermon-on-mount-jesus.png",
        title="Who delivered the Sermon on the Mount?",
        subtitle="Share correctly answering Jesus, by religion, February 2019.",
    ),
    dict(
        key="knows_golden_rule_not_commandment", out="knows-golden-rule-not-commandment.png",
        title="Which is NOT one of the Ten Commandments?",
        subtitle="Share correctly identifying “do unto others as you would have\nthem do unto you” as not one of the Ten Commandments, by religion,\nFebruary 2019.",
    ),
    dict(
        key="knows_purgatory_purification", out="knows-purgatory-purification.png",
        title="What is purgatory in Catholic teaching?",
        subtitle="Share correctly identifying purgatory as where souls undergo\npurification before entering heaven, by religion, February 2019.",
    ),
    dict(
        key="knows_prosperity_gospel", out="knows-prosperity-gospel.png",
        title="What does the prosperity gospel teach?",
        subtitle="Share correctly identifying its teaching that the faithful will be\nblessed with financial success, by religion, February 2019.",
    ),
    dict(
        key="knows_about_mormonism_a_lot_or_some", out="knows-about-mormonism.png",
        title="How much do you know about Mormonism?",
        subtitle="Share saying they personally know “a lot” or “some” about\nMormonism, by religion, February 2019.",
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

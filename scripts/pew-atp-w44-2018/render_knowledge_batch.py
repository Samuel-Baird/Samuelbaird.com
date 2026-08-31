#!/usr/bin/env python3
"""Renders the five knowledge-quiz PNGs for ATP Wave 44 from
docs/datasets/pew-atp-w44-2018/knowledge-batch.json (produced by
knowledge_batch.py). Same shared magnitude-bar shape / row-order rule as
scripts/pew-atp-w143-2024/render_holiday_batch.py.

Usage: python scripts/pew-atp-w44-2018/render_knowledge_batch.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from chart_style import sort_groups  # noqa: E402

DATA = Path("docs/datasets/pew-atp-w44-2018/knowledge-batch.json")
OUT_DIR = Path("public/data-explorer/pew-atp-w44-2018")

CHARTS = [
    dict(
        key="knows_constitution_no_religious_test", out="knows-constitution-no-religious-test.png",
        title="What does the Constitution say about religion?",
        subtitle="Share correctly saying the Constitution requires no\nreligious test for federal officeholders, by religion, February 2019.",
    ),
    dict(
        key="knows_easter_is_resurrection", out="knows-easter-is-resurrection.png",
        title="What's commemorated on Easter Sunday?",
        subtitle="Share correctly identifying the Resurrection of Jesus,\nby religion, February 2019.",
    ),
    dict(
        key="knows_ramadan_is_islamic", out="knows-ramadan-is-islamic.png",
        title="What is Ramadan?",
        subtitle="Share correctly identifying Ramadan as an Islamic holy\nmonth, by religion, February 2019.",
    ),
    dict(
        key="knows_rosh_hashana_is_new_year", out="knows-rosh-hashana-is-new-year.png",
        title="What is Rosh Hashana?",
        subtitle="Share correctly identifying Rosh Hashana as the Jewish\nNew Year, by religion, February 2019.",
    ),
    dict(
        key="knows_mecca_is_pilgrimage_city", out="knows-mecca-is-pilgrimage-city.png",
        title="Where do Muslims make a pilgrimage?",
        subtitle="Share correctly identifying Mecca as Islam's pilgrimage\ncity, by religion, February 2019.",
    ),
    dict(
        key="knows_protestantism_teaches_faith_alone", out="knows-protestantism-faith-alone.png",
        title="Which tradition teaches salvation by faith alone?",
        subtitle="Share correctly identifying Protestantism as the tradition\nteaching salvation through faith alone, by religion, February 2019.",
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

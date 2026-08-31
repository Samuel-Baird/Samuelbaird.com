#!/usr/bin/env python3
"""Renders the "A lesson to learn from COVID" PNG for ATP Wave 70.
Reads only docs/datasets/pew-atp-w70-2020/covid-lesson-belief.json
(produced by covid_lesson_belief.py in this folder). Uses the shared
magnitude-bar shape in scripts/flagship-charts/.

Usage:
  python scripts/pew-atp-w70-2020/render_covid_lesson_chart.py \
    --out public/data-explorer/pew-atp-w70-2020/covid-lesson-belief.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-atp-w70-2020"
    / "covid-lesson-belief.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["group_order"]
    values = {r: data["believes_covid_lesson"][r]["pct"] for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        group_identity=True,
        title="A lesson to learn from COVID",
        subtitle="Share who believe there's a lesson (or set of lessons) for\nhumankind to learn from the coronavirus outbreak, July 2020.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew ATP Wave 70 (2020)",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()

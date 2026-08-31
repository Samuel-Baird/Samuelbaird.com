#!/usr/bin/env python3
"""Renders "How warmly do Americans feel toward Mormons?" from
docs/datasets/pew-atp-w44-2018/warmth-toward-mormons.json (produced by
warmth_toward_mormons.py). Uses the shared magnitude-bar shape in
scripts/flagship-charts/common.py, with value_suffix="/100" since the
plotted value is a feeling-thermometer mean, not a percentage.

Usage:
  python scripts/pew-atp-w44-2018/render_warmth_chart.py \
    --out public/data-explorer/pew-atp-w44-2018/warmth-toward-mormons.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from chart_style import sort_groups  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-atp-w44-2018"
    / "warmth-toward-mormons.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    results = data["warmth_toward_mormons"]
    values = {r: results[r]["mean"] for r in results}
    rows = sort_groups(list(results.keys()), lambda r: values[r])

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        group_identity=True,
        value_suffix="/100",
        title="How warmly do Americans feel toward Mormons?",
        subtitle="Mean feeling-thermometer rating toward Mormons (0=coldest,\n100=warmest), by the rater's own religion, February 2019.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew ATP Wave 44 (2019)",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()

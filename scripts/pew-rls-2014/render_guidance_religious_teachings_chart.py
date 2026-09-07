#!/usr/bin/env python3
"""Renders the "Religion as the main guide to right and wrong" PNG for the 2014 Religious Landscape Study.
Reads only docs/datasets/pew-rls-2014/guidance-religious-teachings.json (produced by guidance_religious_teachings.py in
this folder, which already applies chart_style.sort_groups to group_order).
Uses the shared magnitude-bar shape in scripts/flagship-charts/.

Usage:
  python scripts/pew-rls-2014/render_guidance_religious_teachings_chart.py \\
    --out public/data-explorer/pew-rls-2014/guidance-religious-teachings.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-rls-2014"
    / "guidance-religious-teachings.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["group_order"]
    values = {r: data["guidance_religious_teachings"][r]["pct"] for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        group_identity=True,
        title="Religious teachings are my main guide to right and wrong",
        subtitle="Share who look most to religious teachings and beliefs (vs.\nphilosophy, common sense, or science) for guidance on right\nand wrong, by religious tradition, 2014.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew 2014 RLS",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()

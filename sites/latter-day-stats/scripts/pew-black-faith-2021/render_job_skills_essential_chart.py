#!/usr/bin/env python3
"""Renders the "Churches should teach job skills" PNG for
pew-black-faith-2021. Reads only
docs/datasets/pew-black-faith-2021/job-skills-essential.json (produced by
job_skills_essential.py in this folder). Uses the shared magnitude-bar
shape in scripts/flagship-charts/.

Usage:
  python scripts/pew-black-faith-2021/render_job_skills_essential_chart.py \
    --out public/data-explorer/pew-black-faith-2021/job-skills-essential.png
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

DATA_JSON = (
    Path(__file__).parent / ".." / ".." / "docs" / "datasets" / "pew-black-faith-2021"
    / "job-skills-essential.json"
).resolve()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=DATA_JSON)
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    rows = data["group_order"]
    values = {r: data["job_skills_essential"][r]["pct"] for r in rows}

    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        group_identity=True,
        title="Should churches teach job skills?",
        subtitle="Share of Black Americans saying it's essential for houses of\nworship to teach practical job and life skills, by religion.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew Faith Among Black Americans (2021)",
        out_path=args.out,
        fonts=load_fonts(),
    )


if __name__ == "__main__":
    main()

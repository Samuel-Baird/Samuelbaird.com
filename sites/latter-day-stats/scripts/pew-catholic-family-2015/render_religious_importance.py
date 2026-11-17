#!/usr/bin/env python3
"""Renders the religious-importance PNG from
docs/datasets/pew-catholic-family-2015/religious-importance.json (produced
by religious_importance.py). Same shared magnitude-bar shape / row-order
rule as render_prayer_style.py in this folder.

Usage: python scripts/pew-catholic-family-2015/render_religious_importance.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from chart_style import sort_groups  # noqa: E402

DATA = Path("docs/datasets/pew-catholic-family-2015/religious-importance.json")
OUT_DIR = Path("public/data-explorer/pew-catholic-family-2015")


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    fonts = load_fonts()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    results = data["religion_very_important_pct"]
    values = {r: results[r]["pct"] for r in results}
    rows = sort_groups(list(results.keys()), lambda r: values[r])
    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        group_identity=True,
        title="How important is religion in your life?",
        subtitle="Share saying religion is \"very important\" in\ntheir life, by religion, 2015.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew Catholics & Family Life (2015)",
        out_path=OUT_DIR / "religious-importance.png",
        fonts=fonts,
    )
    print(f"Wrote {OUT_DIR / 'religious-importance.png'}")


if __name__ == "__main__":
    main()

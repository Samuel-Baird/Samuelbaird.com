#!/usr/bin/env python3
"""Renders the prayer-style PNG from
docs/datasets/pew-catholic-family-2015/prayer-style.json (produced by
prayer_style.py). Same shared magnitude-bar shape / row-order rule as
render_adult_arrangements.py in this folder.

Usage: python scripts/pew-catholic-family-2015/render_prayer_style.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "flagship-charts"))
from common import load_fonts, render_magnitude_bar  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from chart_style import sort_groups  # noqa: E402

DATA = Path("docs/datasets/pew-catholic-family-2015/prayer-style.json")
OUT_DIR = Path("public/data-explorer/pew-catholic-family-2015")


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    fonts = load_fonts()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    results = data["personal_conversation_prayer"]
    values = {r: results[r]["pct"] for r in results}
    rows = sort_groups(list(results.keys()), lambda r: values[r])
    render_magnitude_bar(
        rows=rows,
        values=values,
        highlight_rows=None,
        group_identity=True,
        title="When praying, personal conversation or memorized words?",
        subtitle="Share who say they mainly have a personal\nconversation with God when they pray, by religion, 2015.",
        caption_paragraphs=[],
        handle="@ithinkisam | data: Pew Catholics & Family Life (2015)",
        out_path=OUT_DIR / "prayer-style.png",
        fonts=fonts,
    )
    print(f"Wrote {OUT_DIR / 'prayer-style.png'}")


if __name__ == "__main__":
    main()

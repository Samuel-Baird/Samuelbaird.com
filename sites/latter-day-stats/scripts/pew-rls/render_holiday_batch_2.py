"""
Renders the second holiday-batch PNGs from
docs/datasets/pew-rls-2023-24/holiday-batch-2.json (produced by
holiday_batch_2.py). Same pattern as render_holiday_batch.py in this
folder.

Usage: python scripts/pew-rls/render_holiday_batch_2.py
"""
import json
from pathlib import Path

from render_practice_charts import DEFAULT_FONTS_DIR, load_fonts, render_magnitude_bar

DATA = Path("docs/datasets/pew-rls-2023-24/holiday-batch-2.json")
OUT_DIR = Path("public/data-explorer/pew-religious-landscape-study")

ROW_ORDER = [
    "Latter-day Saint", "Catholic", "Protestant", "Orthodox Christian",
    "Jehovah's Witness", "Other Christian", "Jewish", "Muslim", "Buddhist",
    "Hindu", "Other world religions", "Other faiths",
    "Religiously unaffiliated", "All groups average",
]

CHARTS = [
    dict(
        key="same_faith_spouse", out="same-faith-spouse.png",
        title="Whose spouse shares their religion?",
        subtitle="Share of married/partnered adults whose spouse or partner\nshares their current religion, by tradition",
        note=None,
    ),
    dict(
        key="asian_or_asian_american", out="asian-share-by-tradition.png",
        title="Who is Asian or Asian-American?",
        subtitle="Share of each religious tradition identifying as Asian\nor Asian-American",
        note=None,
    ),
    dict(
        key="two_or_more_children", out="two-or-more-children.png",
        title="Who has two or more children?",
        subtitle="Share with two or more children ever born, by religious tradition",
        note=None,
    ),
]


def main():
    data = json.loads(DATA.read_text())
    fonts = load_fonts(DEFAULT_FONTS_DIR)
    total_n = data["total_n"]
    for spec in CHARTS:
        results = data[spec["key"]]
        render_magnitude_bar(
            results, ROW_ORDER, spec["title"], spec["subtitle"], spec["note"],
            total_n, OUT_DIR / spec["out"], fonts,
        )


if __name__ == "__main__":
    main()

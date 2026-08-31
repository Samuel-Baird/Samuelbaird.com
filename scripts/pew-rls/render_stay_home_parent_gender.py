"""
Renders the stay-home-parent-gender PNG from
docs/datasets/pew-rls-2023-24/stay-home-parent-gender.json (produced by
stay_home_parent_gender.py). Same pattern as render_holiday_batch.py in
this folder.

Usage: python scripts/pew-rls/render_stay_home_parent_gender.py
"""
import json
from pathlib import Path

from render_practice_charts import DEFAULT_FONTS_DIR, load_fonts, render_magnitude_bar

DATA = Path("docs/datasets/pew-rls-2023-24/stay-home-parent-gender.json")
OUT_DIR = Path("public/data-explorer/pew-religious-landscape-study")

ROW_ORDER = [
    "Latter-day Saint", "Catholic", "Protestant", "Orthodox Christian",
    "Jehovah's Witness", "Other Christian", "Jewish", "Muslim", "Buddhist",
    "Hindu", "Other world religions", "Other faiths",
    "Religiously unaffiliated", "All groups average",
]


def main():
    data = json.loads(DATA.read_text())
    fonts = load_fonts(DEFAULT_FONTS_DIR)
    render_magnitude_bar(
        data["should_be_mother"], ROW_ORDER,
        "If a parent stays home, should it be the mother?",
        "Of those who say a parent should stay home to focus on\nfamily, share saying specifically the mother, by tradition",
        None, data["total_n"], OUT_DIR / "stay-home-parent-gender.png", fonts,
    )


if __name__ == "__main__":
    main()

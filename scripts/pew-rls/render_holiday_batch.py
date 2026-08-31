"""
Renders the holiday-batch PNGs from docs/datasets/pew-rls-2023-24/holiday-batch.json
(produced by holiday_batch.py). Reuses render_practice_charts.render_magnitude_bar
and load_fonts directly rather than duplicating the layout math - same
canvas/fonts/colors as every other RLS chart; see STYLE.md.

Usage: python scripts/pew-rls/render_holiday_batch.py
"""
import json
from pathlib import Path

from render_practice_charts import DEFAULT_FONTS_DIR, load_fonts, render_magnitude_bar

DATA = Path("docs/datasets/pew-rls-2023-24/holiday-batch.json")
OUT_DIR = Path("public/data-explorer/pew-religious-landscape-study")

ROW_ORDER = [
    "Latter-day Saint", "Catholic", "Protestant", "Orthodox Christian",
    "Jehovah's Witness", "Other Christian", "Jewish", "Muslim", "Buddhist",
    "Hindu", "Other world religions", "Other faiths",
    "Religiously unaffiliated", "All groups average",
]

CHARTS = [
    dict(
        key="works_for_pay", out="labor-day-works-for-pay.png",
        title="Who works full or part time for pay?",
        subtitle="Share who currently work for pay, by religious tradition",
        note="\"Not currently working,\" unable to work due to disability, and retired excluded from the numerator.",
    ),
    dict(
        key="very_happy", out="happiness-by-tradition.png",
        title="Who says they're very happy with life?",
        subtitle="Share saying they are \"very happy\" these days, by religious tradition",
        note="Options were very happy, pretty happy, not too happy.",
    ),
    dict(
        key="hispanic", out="hispanic-share-by-tradition.png",
        title="Who is Hispanic, Latino, or Spanish?",
        subtitle="Share of each religious tradition, by self-identification",
        note=None,
    ),
    dict(
        key="christian_nation_favor", out="christian-nation-favor.png",
        title="Should the U.S. be declared a Christian nation?",
        subtitle="Share favoring the federal government declaring the U.S. a Christian nation",
        note="Strongly favor + favor (top two box).",
    ),
    dict(
        key="stay_home_parent_better", out="stay-home-parent-view.png",
        title="Is a stay-at-home parent better for kids?",
        subtitle="Share saying children are better off when a parent stays home to focus on family",
        note="vs. children being just as well off with both parents working outside the home.",
    ),
    dict(
        key="religious_symbols_favor", out="religious-symbols-public-property.png",
        title="Religious symbols on public property?",
        subtitle="Share favoring cities and towns placing religious symbols on public property",
        note="Strongly favor + favor (top two box).",
    ),
    dict(
        key="school_prayer_favor", out="school-prayer-jesus-favor.png",
        title="Teacher-led prayer in public schools?",
        subtitle="Share favoring public school teachers leading classes in prayers that refer to Jesus",
        note="Strongly favor + favor (top two box).",
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

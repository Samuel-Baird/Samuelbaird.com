"""Renders the four study graphics for Pew's "Mormons in America" (2012)
survey - a religious-practice magnitude bar, a Mormons-vs-general-public
paired bar, a mission-service magnitude bar, and a perceived-discrimination
magnitude bar.

Every number comes from docs/study-data/<study-slug>/data.json (see that
file's `sources` for the transcription provenance); nothing is typed here.
Regenerate with:

    python3 scripts/study-graphics/pew-mormons-in-america-2012/render_charts.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))
sys.path.insert(0, str(SCRIPTS_DIR / "flagship-charts"))

from chart_style import MUTED, color_for_group  # noqa: E402
from common import load_fonts, render_magnitude_bar, render_paired_bar  # noqa: E402

STUDY_SLUG = "pew-mormons-in-america-2012"
REPO = SCRIPTS_DIR.parent
DATA = json.loads((REPO / "docs" / "study-data" / STUDY_SLUG / "data.json").read_text())
OUT_DIR = REPO / "public" / "study-graphics" / STUDY_SLUG
HANDLE = f"@ithinkisam | data: {DATA['source_short_title']}"


def main() -> None:
    fonts = load_fonts()

    practice = {r["label"]: r["pct"] for r in DATA["charts"]["religious-practice"]["rows"]}
    # "All three of the above" is the combined stat, kept last regardless of
    # value so it reads as the summary row it is.
    practice_rows = sorted(
        (label for label in practice if label != "All three of the above"),
        key=lambda label: -practice[label],
    ) + ["All three of the above"]
    render_magnitude_bar(
        rows=practice_rows,
        values=practice,
        highlight_rows=None,
        title="Religious practice among U.S. Mormons",
        subtitle="Share of self-identified Mormon adults,\nOct.–Nov. 2011 (n = 1,019)",
        caption_paragraphs=[],
        handle=HANDLE,
        out_path=OUT_DIR / "religious-practice.png",
        fonts=fonts,
    )

    vs = DATA["charts"]["mormons-vs-public"]["rows"]
    vs_values = {r["label"]: {"Mormons": r["mormon"], "U.S. general public": r["public"]} for r in vs}
    render_paired_bar(
        rows=sorted(vs_values, key=lambda label: -vs_values[label]["Mormons"]),
        series_order=["Mormons", "U.S. general public"],
        # The subject group carries the Latter-day Saint identity color; the
        # general public is a population baseline, so it takes MUTED, per
        # chart_style's aggregate-row convention.
        series_colors={
            "Mormons": color_for_group("Latter-day Saint"),
            "U.S. general public": MUTED,
        },
        values=vs_values,
        title="Mormons and the general public, side by side",
        subtitle="Percent of each group, 2011",
        caption_paragraphs=[],
        handle=HANDLE,
        out_path=OUT_DIR / "mormons-vs-public.png",
        fonts=fonts,
    )

    # A second, narrower cut of the same mormons-vs-public rows: drops
    # "Satisfied with their own life" and "Prefer a smaller government",
    # leaving the three items that read as a "core values" comparison
    # (morality, family, and social issues) rather than mixing in general
    # well-being and political preference. Reuses the same data.json rows
    # (nothing new to transcribe) - just a filtered view, rendered
    # alongside (not replacing) the original 5-row chart above.
    core_labels = [
        "Premarital sex is morally wrong",
        "Currently married",
        "Homosexuality should be discouraged",
    ]
    vs_core_values = {label: vs_values[label] for label in core_labels}
    render_paired_bar(
        rows=sorted(vs_core_values, key=lambda label: -vs_core_values[label]["Mormons"]),
        series_order=["Mormons", "U.S. general public"],
        series_colors={
            "Mormons": color_for_group("Latter-day Saint"),
            "U.S. general public": MUTED,
        },
        values=vs_core_values,
        title="Mormons and the public on core values",
        subtitle="Percent of each group, 2011",
        caption_paragraphs=[],
        handle=HANDLE,
        out_path=OUT_DIR / "mormons-vs-public-core-values.png",
        fonts=fonts,
    )

    mission = {r["label"]: r["pct"] for r in DATA["charts"]["mission-service"]["rows"]}
    render_magnitude_bar(
        rows=["Men", "Women", "All Mormons"],
        values=mission,
        highlight_rows={"Men", "Women"},
        title="Who has served a full-time mission",
        subtitle="Share of self-identified U.S. Mormons who have\nserved a full-time mission, 2011",
        caption_paragraphs=[],
        handle=HANDLE,
        out_path=OUT_DIR / "mission-service.png",
        fonts=fonts,
    )

    disc = {r["label"]: r["pct"] for r in DATA["charts"]["perceived-discrimination"]["rows"]}
    render_magnitude_bar(
        rows=sorted(disc, key=lambda label: -disc[label]),
        values=disc,
        highlight_rows=None,
        title="Perceptions of discrimination, as Mormons see it",
        subtitle="Share of U.S. Mormons saying each group faces\na lot of discrimination in America, 2011",
        caption_paragraphs=[],
        handle=HANDLE,
        out_path=OUT_DIR / "perceived-discrimination.png",
        fonts=fonts,
    )


if __name__ == "__main__":
    main()

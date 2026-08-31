"""Renders the two study graphics for Dyer et al.'s "Latter-day Saint
Religiousness, Well-Being, and Retention in the United States" (BYU Studies,
2026) - a smartphone-ownership magnitude bar and a video-clip-watching
magnitude bar, both from the "Digital Media" section's FFYD logistic
regression on deidentification by 2024.

Every number comes from docs/study-data/<study-slug>/data.json (see that
file's `sources` for the transcription provenance); nothing is typed here.
Regenerate with:

    python3 scripts/study-graphics/dyer-lds-trends-us-byu-studies-2026/render_charts.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))
sys.path.insert(0, str(SCRIPTS_DIR / "flagship-charts"))

from common import load_fonts, render_magnitude_bar  # noqa: E402

STUDY_SLUG = "dyer-lds-trends-us-byu-studies-2026"
REPO = SCRIPTS_DIR.parent
DATA = json.loads((REPO / "docs" / "study-data" / STUDY_SLUG / "data.json").read_text())
OUT_DIR = REPO / "public" / "study-graphics" / STUDY_SLUG
HANDLE = f"@ithinkisam | data: {DATA['source_short_title']}"


def main() -> None:
    fonts = load_fonts()

    phone = {r["label"]: r["pct"] for r in DATA["charts"]["smartphone-ownership"]["rows"]}
    render_magnitude_bar(
        rows=["Owned a smartphone", "No smartphone"],
        values=phone,
        # The higher, statistically significant rate is the finding; "No
        # smartphone" is the baseline it's measured against.
        highlight_rows={"Owned a smartphone"},
        title="Smartphone ownership and deidentifying",
        subtitle="Share of FFYD youth who had deidentified as\nLatter-day Saint by 2024, by smartphone ownership",
        caption_paragraphs=[],
        handle=HANDLE,
        out_path=OUT_DIR / "smartphone-ownership.png",
        fonts=fonts,
    )

    video = {r["label"]: r["pct"] for r in DATA["charts"]["video-clip-watching"]["rows"]}
    render_magnitude_bar(
        rows=["No video clips", "1 hour a day", "2 hours a day", "3 hours a day"],
        values=video,
        # A single ordered trend, not a highlight-vs-context comparison -
        # every bar carries the same weight.
        highlight_rows=None,
        title="Watching video clips and deidentifying",
        subtitle="Share of FFYD youth who had deidentified as\nLatter-day Saint by 2024, by daily video-clip watching",
        caption_paragraphs=[],
        handle=HANDLE,
        out_path=OUT_DIR / "video-clip-watching.png",
        fonts=fonts,
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Renders "Christian traditions only" variants of 12 existing Pew RLS
Data Explorer charts, alongside (not replacing) their original wide-
population versions.

Requested population for all 12: Latter-day Saint, Catholic, Protestant,
Orthodox Christian, Jehovah's Witness - plus Religiously unaffiliated for
the seven items whose original chart already carried that row (the five
"beliefs" items below in scripts/pew-rls/render_beliefs_charts.py, plus
relimpact/vol12 in scripts/pew-rls/render_public_life_charts.py, both of
which use that file's WIDEST_ORDER). Everything else about each chart
(title, subtitle, data source, chart shape) is unchanged from the
original - only the row set is narrower. Reuses each item's existing
compute step and JSON (practice.json, beliefs.json, public-life.json) and
the render *functions* already defined in render_practice_charts.py,
render_beliefs_charts.py, and render_public_life_charts.py - imported as
modules rather than reimplemented, so a future change to those shapes
doesn't have to be kept in sync by hand in two places. render_beliefs_charts's
render_magnitude_bar/render_paired_bar read their row order off that
module's own GROUP_ORDER global rather than taking it as a parameter, so
this script monkeypatches that global before each call.

Usage: python scripts/pew-rls/render_christian_only_variants.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import render_beliefs_charts as beliefs_r  # noqa: E402
import render_practice_charts as practice_r  # noqa: E402
import render_public_life_charts as public_r  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = REPO_ROOT / "docs" / "datasets" / "pew-rls-2023-24"
OUT_DIR = REPO_ROOT / "public" / "data-explorer" / "pew-religious-landscape-study"
FONTS_DIR = (Path(__file__).parent / ".." / "state-of-theology-graphics" / "fonts").resolve()

NARROW_ORDER = [
    "Latter-day Saint", "Catholic", "Protestant", "Orthodox Christian",
    "Jehovah's Witness",
]
NARROW_PLUS_UNAFFILIATED_ORDER = NARROW_ORDER + ["Religiously unaffiliated"]

CHRISTIAN_NOTE = (
    "Population: Christian traditions only (Latter-day Saint, Catholic, Protestant, "
    "Orthodox Christian, Jehovah's Witness)."
)
CHRISTIAN_PLUS_UNAFFILIATED_NOTE = (
    "Population: Christian traditions only (Latter-day Saint, Catholic, Protestant, "
    "Orthodox Christian, Jehovah's Witness), plus the religiously unaffiliated as "
    "their own row."
)


def main() -> None:
    fonts = practice_r.load_fonts(FONTS_DIR)

    with open(DATA_DIR / "practice.json", encoding="utf-8") as f:
        practice = json.load(f)
    total_n = practice["total_unweighted_n"]

    practice_r.render_distribution_stack(
        practice["attend_distribution"], NARROW_ORDER, practice["attend_order"],
        title="Attendance frequency, full distribution (Christian only)",
        subtitle="How often each tradition's members attend religious\nservices in person.",
        note=CHRISTIAN_NOTE, total_n=total_n,
        out_path=OUT_DIR / "practice-attend-distribution-christian.png", fonts=fonts,
        # Requested: group (y-axis) labels the same size as the legend key,
        # rather than this shape's usual smaller axis-label size - trying it
        # on this one chart first before rolling it out further.
        group_label_fontsize=practice_r.MIN.LEGEND,
    )
    practice_r.render_magnitude_bar(
        practice["attend_monthly_plus_either"], NARROW_ORDER,
        title="Attend in-person and/or online, monthly+ (Christian only)",
        subtitle="Share attending religious services monthly+ either\nin person or online/on TV.",
        note=CHRISTIAN_NOTE + " Derived: monthly+ on ATTNDPERRLS or ATTNDONRLS.",
        total_n=total_n,
        out_path=OUT_DIR / "practice-attend-monthly-plus-christian.png", fonts=fonts,
    )
    practice_r.render_magnitude_bar(
        practice["memb_member"], NARROW_ORDER,
        title="Member of a house of worship (Christian only)",
        subtitle="Share who are personally a member of a church,\nsynagogue, mosque, temple, or other house of worship.",
        note=CHRISTIAN_NOTE, total_n=total_n,
        out_path=OUT_DIR / "practice-memb-christian.png", fonts=fonts,
    )
    practice_r.render_distribution_stack(
        practice["pray_distribution"], NARROW_ORDER, practice["pray_order"],
        title="Prayer frequency (Christian only)",
        subtitle="How often each tradition's members pray, outside of\nattending religious services.",
        note=CHRISTIAN_NOTE + " Collapsed from Pew's 7-category scale to 4 (see "
             "practice.py's design_decisions).",
        total_n=total_n,
        out_path=OUT_DIR / "practice-pray-distribution-christian.png", fonts=fonts,
    )
    practice_r.render_magnitude_bar(
        practice["pracb_weekly_plus"], NARROW_ORDER,
        title="Read scripture outside of services, weekly+ (Christian only)",
        subtitle="Share reading scripture at least once a week, outside\nof religious services.",
        note=CHRISTIAN_NOTE, total_n=total_n,
        out_path=OUT_DIR / "practice-pracb-christian.png", fonts=fonts,
    )

    with open(DATA_DIR / "beliefs.json", encoding="utf-8") as f:
        beliefs = json.load(f)
    beliefs_total_n = beliefs["total_unweighted_n"]
    beliefs_r.GROUP_ORDER = NARROW_PLUS_UNAFFILIATED_ORDER

    beliefs_r.render_magnitude_bar(
        beliefs["soul_belief"],
        title="Believe people have a soul or spirit (Christian only)",
        subtitle="Share who believe people have a soul or spirit in\naddition to their physical body.",
        note=CHRISTIAN_PLUS_UNAFFILIATED_NOTE, total_n=beliefs_total_n,
        out_path=OUT_DIR / "beliefs-soul-christian.png", fonts=fonts,
    )
    beliefs_r.render_magnitude_bar(
        beliefs["heaven_belief"],
        title="Believe in heaven (Christian only)",
        subtitle="Share who believe there is a heaven where people who\nled good lives are eternally rewarded.",
        note=CHRISTIAN_PLUS_UNAFFILIATED_NOTE, total_n=beliefs_total_n,
        out_path=OUT_DIR / "beliefs-heaven-christian.png", fonts=fonts,
    )
    beliefs_r.render_magnitude_bar(
        beliefs["hell_belief"],
        title="Believe in hell (Christian only)",
        subtitle="Share who believe there is a hell where people who led\nbad lives are eternally punished.",
        note=CHRISTIAN_PLUS_UNAFFILIATED_NOTE, total_n=beliefs_total_n,
        out_path=OUT_DIR / "beliefs-hell-christian.png", fonts=fonts,
    )
    beliefs_r.render_paired_bar(
        beliefs["heaven_belief"], beliefs["hell_belief"],
        title="Belief in heaven vs. hell (Christian only)",
        subtitle="The same two questions, compared side by side per\ntradition.",
        note=CHRISTIAN_PLUS_UNAFFILIATED_NOTE, total_n=beliefs_total_n,
        out_path=OUT_DIR / "beliefs-heaven-vs-hell-christian.png", fonts=fonts,
    )
    beliefs_r.render_magnitude_bar(
        beliefs["evolution_guided_by_god"],
        title="Evolution guided by God (Christian only)",
        subtitle="Share who say humans evolved over time due to\nprocesses guided or allowed by God.",
        note=CHRISTIAN_PLUS_UNAFFILIATED_NOTE, total_n=beliefs_total_n,
        out_path=OUT_DIR / "beliefs-evolution-christian.png", fonts=fonts,
    )

    with open(DATA_DIR / "public-life.json", encoding="utf-8") as f:
        public_life = json.load(f)
    public_total_n = public_life["total_unweighted_n"]

    public_r.render_magnitude_bar(
        public_life["relimpact_more_good"], NARROW_PLUS_UNAFFILIATED_ORDER,
        title="Religion does more good than harm (Christian only)",
        subtitle="Share who say religion's overall impact on American\nsociety is more good than harm.",
        note=CHRISTIAN_PLUS_UNAFFILIATED_NOTE, total_n=public_total_n,
        out_path=OUT_DIR / "public-relimpact-christian.png", fonts=fonts,
    )
    public_r.render_magnitude_bar(
        public_life["vol12_volunteered"], NARROW_PLUS_UNAFFILIATED_ORDER,
        title="Volunteered in the past 12 months (Christian only)",
        subtitle="Share who spent any time volunteering in the past 12\nmonths.",
        note=CHRISTIAN_PLUS_UNAFFILIATED_NOTE, total_n=public_total_n,
        out_path=OUT_DIR / "public-vol12-christian.png", fonts=fonts,
    )


if __name__ == "__main__":
    main()

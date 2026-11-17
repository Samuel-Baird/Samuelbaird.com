#!/usr/bin/env python3
"""Render Saint Capybara NEUTRAL-pose candidates for the user to pick from,
or lock in a picked candidate as the sprite base.

This is Step 1 of the Saint Capybara pipeline (see
../docs/saint-capybara/brand.md and ../docs/types/saint-capybara.md): the
user reviews 3-4 neutral-pose variants, picks a favorite, and that variant
becomes the base every other pose in capy_sprite_sheet.py is derived from.

Every candidate keeps the FIXED character design from the brief -- a
brown capybara, small gold halo, and a crucifix necklace on bare fur, no
robe, no permanent Bible -- across all 21 future poses. The body and head
are a single continuous rounded shape (capybaras have no visible neck),
with a wide two-tone muzzle patch as the main "reads as a capybara"
feature. What varies between candidates is body/snout proportions,
outline weight, fur/snout color choice, ear style, and eye style (see
VARIANTS below).

Usage:
    python capy_sprite_candidates.py
    python capy_sprite_candidates.py --out assets/saint-capybara/sprites/candidates.png
    python capy_sprite_candidates.py --pick B
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from capy.compose import compose, contact_sheet, save_png, upscale
from capy.palette import kit_dir

VARIANTS: dict[str, dict] = {
    "A": {
        "body_rx": 46, "body_ry": 42, "snout_rx": 22, "snout_ry": 15, "outline": 2,
        "ear_style": "small", "eye_style": "dot",
        "blurb": "Baseline proportions, small ears, round muzzle patch, dot eyes.",
    },
    "B": {
        "body_rx": 50, "body_ry": 40, "snout_rx": 26, "snout_ry": 17, "outline": 2,
        "ear_style": "round", "eye_style": "dot",
        "blurb": "Wider/flatter body, bigger muzzle, rounder ears -- chunkier and more clearly capybara-shaped.",
    },
    "C": {
        "body_rx": 44, "body_ry": 44, "snout_rx": 20, "snout_ry": 14, "outline": 2,
        "ear_style": "small", "eye_style": "dot",
        "fur": "fur_shade", "fur_shade": "fur",
        "blurb": "Rounder/taller body, slightly darker/richer fur tone.",
    },
    "D": {
        "body_rx": 46, "body_ry": 42, "snout_rx": 22, "snout_ry": 15, "outline": 3,
        "ear_style": "round", "eye_style": "bead",
        "blurb": "Thicker outline, bead eyes, round ears -- bolder/simpler silhouette.",
    },
}


def render_candidates(out_path: Path) -> None:
    labeled: list[tuple[str, object]] = []
    for letter in "ABCD":
        variant = VARIANTS[letter]
        img = compose("neutral", variant)
        labeled.append((f"{letter} (native 128px)", img))
    for letter in "ABCD":
        variant = VARIANTS[letter]
        img = upscale(compose("neutral", variant), 4)
        labeled.append((f"{letter} (x4 = 512px)", img))

    sheet = contact_sheet(labeled, cols=4, cell=280)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    save_png(sheet, out_path)
    print(f"Wrote {out_path}")
    print()
    for letter in "ABCD":
        print(f"  {letter}: {VARIANTS[letter]['blurb']}")
    print()
    print("Review the sheet, then run:")
    print("    python capy_sprite_candidates.py --pick <A|B|C|D>")


def pick_candidate(letter: str, kit: Path) -> None:
    letter = letter.upper()
    if letter not in VARIANTS:
        raise SystemExit(f"error: unknown candidate {letter!r}, choices are A/B/C/D")
    variant = dict(VARIANTS[letter])
    variant.pop("blurb", None)
    base = {
        "variant_letter": letter,
        "params": variant,
        "picked_at": datetime.now(timezone.utc).isoformat(),
    }
    out = kit / "sprites" / "base.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(base, indent=2), encoding="utf-8")
    print(f"Wrote {out} -- variant {letter} is now the sprite base.")
    print("Next: python capy_sprite_sheet.py")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, default=None, help="Contact sheet output path")
    parser.add_argument("--pick", choices=list(VARIANTS), help="Lock in a candidate as sprites/base.json")
    parser.add_argument("--kit", type=Path, default=None, help="Override the assets/saint-capybara kit dir")
    args = parser.parse_args()

    kit = kit_dir(args.kit)
    if args.pick:
        pick_candidate(args.pick, kit)
        return 0

    out_path = args.out or (kit / "sprites" / "candidates.png")
    render_candidates(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

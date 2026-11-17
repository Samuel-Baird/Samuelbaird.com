#!/usr/bin/env python3
"""One-time (re-runnable) import of the finalized Saint Capybara sprite art.

The user supplied finished, finalized PNG art at
``D:\\saint-capybara\\finalized images\\saint-capybara-<pose>.png`` (see
docs/saint-capybara/brand.md section "Sprite art is AI-generated, not
code-drawn"). This script is integration only -- it does NOT generate or
alter the art's content. It:

1. Converts every source PNG to RGBA (one file, ``deadpan``, was delivered
   as flat RGB with no alpha channel).
2. Normalizes every source PNG onto a fixed square canonical canvas
   (``CANONICAL_SIZE``, default 1024x1024) by a "contain" fit (preserve
   aspect ratio, pad with transparency, centered) -- this matters because
   one file (``quote.png``, 1448x1086) is not square, unlike the other 24
   files (1254x1254). A single square canonical size means every
   downstream consumer (tools/capy/plates.py) can treat the sprite box as
   one fixed square region read from theme.yaml and scale down uniformly,
   rather than special-casing one file's aspect ratio.
3. Strips PNG metadata/text chunks (anonymity requirement -- see brand.md
   "Operational anonymity checklist"; mirrors capy.compose.save_png).
4. Writes clean pose-keyed filenames into assets/saint-capybara/sprites/
   (e.g. neutral.png, sign-father.png) -- no "saint-capybara-" prefix,
   since the project folder itself makes the identity clear.
5. Writes assets/saint-capybara/sprites/manifest.json: pose name -> filename,
   using the 21-pose roster's `reading_source`/`explaining_quote` naming
   (matching tools/capy/poses.py's FUNCTION_TO_POSE and POSE_ORDER) even
   though the finalized files use the shorter `source`/`quote` names --
   see MAPPING below for the two renames, plus the 4 additional
   sign-of-the-cross outro poses that aren't in the original 21.

Usage:
    python tools/capy_import_sprites.py [--src "D:\\saint-capybara\\finalized images"] [--size 1024]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SRC = Path(r"D:\saint-capybara\finalized images")
DEST_DIR = REPO_ROOT / "assets" / "saint-capybara" / "sprites"

# pose key (as used in beats.yaml / FUNCTION_TO_POSE) -> source filename stem
# (without the "saint-capybara-" prefix or .png extension).
#
# Mapping decisions (see docs/saint-capybara/brand.md sec 5 and the task
# brief this was built against):
#   - reading_source -> "source" (finalized art's closest match: Bible in
#     one paw with a scroll/document visible -- reads as "reading a source")
#   - explaining_quote -> "quote" (finalized art: pointing toward empty
#     space where quote text can be composited -- reads as "explaining a
#     quote")
# All other 19 of the original 21-pose roster use identical names in both
# places. The 4 sign-* poses are new additions for the mandatory outro
# sequence (brand.md sec 5a) and were not part of the original 21-pose brief.
POSE_TO_SOURCE_STEM = {
    "neutral": "neutral",
    "talking": "talking",
    "teaching": "teaching",
    "reading": "reading",
    "thoughtful": "thoughtful",
    "pointing": "pointing",
    "happy": "happy",
    "concerned": "concerned",
    "confused": "confused",
    "surprised": "surprised",
    "skeptical": "skeptical",
    "amused": "amused",
    "prayerful": "prayerful",
    "solemn": "solemn",
    "encouraging": "encouraging",
    "reading_source": "source",
    "researching": "researching",
    "explaining_quote": "quote",
    "listening": "listening",
    "deadpan": "deadpan",
    "disappointed": "disappointed",
    # Outro sign-of-the-cross sequence (brand.md sec 5a) -- not part of the
    # rhetorical-function roster, selected explicitly by the fixed outro
    # beat block (tools/capy/beats.py OUTRO_BEATS).
    "sign-father": "sign-father",
    "sign-son": "sign-son",
    "sign-holy": "sign-holy",
    "sign-spirit-amen": "sign-spirit-amen",
}


def fit_square(img: Image.Image, size: int) -> Image.Image:
    """Contain-fit `img` onto a transparent size x size square canvas,
    preserving aspect ratio, centered. No-op in aspect terms for the 24
    already-square 1254x1254 files; only actually pads quote.png
    (1448x1086)."""
    img = img.convert("RGBA")
    w, h = img.size
    scale = min(size / w, size / h)
    new_w, new_h = max(1, round(w * scale)), max(1, round(h * scale))
    resized = img.resize((new_w, new_h), resample=Image.LANCZOS)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    canvas.paste(resized, ((size - new_w) // 2, (size - new_h) // 2), resized)
    return canvas


def save_clean_png(img: Image.Image, path: Path) -> None:
    """Save with no text/metadata chunks -- anonymity requirement, mirrors
    capy.compose.save_png."""
    img.save(path, format="PNG")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--src", type=Path, default=DEFAULT_SRC)
    ap.add_argument("--size", type=int, default=1024)
    args = ap.parse_args()

    if not args.src.is_dir():
        print(f"error: source dir not found: {args.src}")
        return 1

    DEST_DIR.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, dict] = {
        "_comment": (
            "pose -> filename. Generated by tools/capy_import_sprites.py from "
            "D:\\saint-capybara\\finalized images. Canonical size: square, "
            "padded with transparency where the source wasn't square "
            "(quote.png only). See that script's docstring for the "
            "reading_source->source / explaining_quote->quote rename."
        ),
        "canonical_size": args.size,
        "poses": {},
        "mouth_open": {},  # no separate mouth-open frames in the finalized art (scope reduction, see brand.md)
        "function_to_pose": {
            "evidence": ["reading_source", "reading", "neutral"],
            "uncertainty": ["thoughtful", "confused"],
            "serious": ["concerned", "solemn"],
            "questionable_premise": ["skeptical"],
            "factual_failure": ["disappointed", "deadpan"],
            "light": ["amused", "happy"],
            "explain": ["teaching", "explaining_quote", "pointing"],
            "listen": ["listening"],
            "closing": ["encouraging", "prayerful"],
        },
        "sensitive_forbidden": ["amused", "happy"],
        "outro_sequence": ["sign-father", "sign-son", "sign-holy", "sign-spirit-amen"],
    }

    missing = []
    for pose, stem in POSE_TO_SOURCE_STEM.items():
        src_path = args.src / f"saint-capybara-{stem}.png"
        if not src_path.exists():
            missing.append(src_path)
            continue
        img = Image.open(src_path)
        fitted = fit_square(img, args.size)
        out_name = f"{pose}.png"
        save_clean_png(fitted, DEST_DIR / out_name)
        manifest["poses"][pose] = out_name
        print(f"  {pose:20s} <- {src_path.name}  ({img.size} {img.mode} -> {args.size}x{args.size} RGBA)")

    if missing:
        print("WARNING: missing source files:")
        for m in missing:
            print(f"  {m}")

    manifest_path = DEST_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\nWrote {len(manifest['poses'])} sprites + manifest to {DEST_DIR}")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Thin accessor over assets/saint-capybara/theme.yaml's `layout`/`palette`/
`fonts`/`captions`/`card_text`/`cache` blocks, so tools/capy/plates.py,
sprites.py, text.py, and capy_caption_cards.py never hardcode a zone's
pixel coordinates -- everything is read from theme.yaml.

    from capy.layout import Theme
    theme = Theme.load()                 # 9:16 (shorts, Instagram long form)
    theme = Theme.for_doc(doc)           # picks 16:9 for video_type: long-youtube
    theme.mode_for(beat)                 # "clip" | "host" | "card"
    theme.sprite_spec("clip")            # SpriteSpec(...)
    theme.caption_zone("host")           # CaptionZone(y0, y1, max_width)

layout.version 2 (2026-09-09): three frame modes (clip/host/card) replacing
the old fixed stage/captions/character-band zoning. See
docs/saint-capybara/brand.md sec 8.

Orientation: theme.yaml's `layout` is the 9:16 portrait layout;
`layout.landscape` is the 16:9 YouTube long-form layout. Loading with
orientation="landscape" swaps it in as `self.layout` and deep-merges its
`overrides` over the captions/card_text blocks, so every caller keeps
reading the same accessors without caring which canvas it's on.
"""
from __future__ import annotations

import copy
import hashlib
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
THEME_PATH = REPO_ROOT / "assets" / "saint-capybara" / "theme.yaml"
FONTS_DIR = REPO_ROOT / "assets" / "saint-capybara" / "fonts"
SPRITES_DIR = REPO_ROOT / "assets" / "saint-capybara" / "sprites"

# Finalized AI-generated art (brand.md sec "Sprite art is AI-generated, not
# code-drawn") lives outside this repo, on the same machine. This is the
# current pipeline's actual sprite source -- SPRITES_DIR above is the
# retired code-drawn renderer's output directory, kept only as a fallback.
FINALIZED_SPRITES_DIR = Path(r"D:\saint-capybara\finalized images")

# Beat kind -> frame mode. Anything not listed raises (should not happen
# once capy.beats.BEAT_KINDS and this map are kept in sync).
MODE_FOR_KIND = {
    "clip": "clip",
    "narration": "host",
    "card": "card",
    "evidence": "card",
    "chart": "card",
    "excerpt": "card",
}


def _hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


@dataclass
class SpriteSpec:
    box: tuple[int, int, int, int]   # (x0, y0, x1, y1), a square
    outline_px: int
    shadow: dict | None              # {dx, dy, alpha} hard shadow (clip mode)
    ground_shadow: dict | None       # {rx, ry, alpha} ellipse (host mode)


@dataclass
class CaptionZone:
    y0: int
    y1: int
    max_width: int
    x_center: int = 540
    max_lines: int | None = None     # per-zone override of captions.max_lines


class ThemeError(RuntimeError):
    pass


ORIENTATIONS = ("portrait", "landscape")


def _deep_merge(base: dict, over: dict) -> None:
    for k, v in over.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _deep_merge(base[k], v)
        else:
            base[k] = copy.deepcopy(v)


class Theme:
    def __init__(self, data: dict):
        self.data = data
        self.orientation = "portrait"
        self._sprite_hash_cache: dict[str, str] = {}
        self._font_hash_cache: dict[str, str] = {}

    @classmethod
    def load(cls, path: Path | None = None, *, orientation: str = "portrait") -> "Theme":
        if orientation not in ORIENTATIONS:
            raise ThemeError(f"unknown orientation {orientation!r} (expected one of {ORIENTATIONS})")
        path = path or THEME_PATH
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if orientation == "landscape":
            landscape = data["layout"].get("landscape")
            if not landscape:
                raise ThemeError("theme.yaml has no layout.landscape block")
            data["layout"] = copy.deepcopy(landscape)
            _deep_merge(data, data["layout"].pop("overrides", {}) or {})
        else:
            data["layout"] = {k: v for k, v in data["layout"].items() if k != "landscape"}
        theme = cls(data)
        theme.orientation = orientation
        return theme

    @classmethod
    def for_doc(cls, doc: dict, path: Path | None = None) -> "Theme":
        """The theme for a loaded beats.yaml: 16:9 for a long-youtube
        video, 9:16 otherwise (capy.beats.orientation_for)."""
        from capy.beats import orientation_for
        return cls.load(path, orientation=orientation_for(doc))

    # ---- basics -----------------------------------------------------

    @property
    def layout(self) -> dict:
        return self.data["layout"]

    @property
    def layout_version(self) -> int:
        return int(self.layout.get("version", 1))

    @property
    def canvas_size(self) -> tuple[int, int]:
        c = self.layout["canvas"]
        return c["width"], c["height"]

    @property
    def fps(self) -> int:
        return self.layout["canvas"]["fps"]

    @property
    def sprite_bottom(self) -> int:
        return int(self.layout["sprite_bottom"])

    def zone(self, name: str) -> dict:
        return self.layout[name]

    # ---- frame modes --------------------------------------------------

    def mode_for(self, beat: dict) -> str:
        """Frame mode for a beat: 'clip' | 'host' | 'card'."""
        kind = beat.get("kind")
        mode = MODE_FOR_KIND.get(kind)
        if mode is None:
            raise ThemeError(f"no frame mode mapped for beat kind {kind!r}")
        return mode

    def sprite_spec(self, mode: str) -> SpriteSpec:
        m = self.layout[mode]
        s = m["sprite"]
        size = s["size"]
        bottom = m.get("sprite_bottom", self.sprite_bottom)
        if "x_center" in s:
            x0 = s["x_center"] - size // 2
        else:
            x0 = s["x0"]
        y0 = bottom - size
        box = (x0, y0, x0 + size, bottom)
        return SpriteSpec(
            box=box,
            outline_px=s.get("outline_px", 0),
            shadow=s.get("shadow"),
            ground_shadow=s.get("ground_shadow"),
        )

    def caption_zone(self, mode: str) -> CaptionZone:
        c = self.layout[mode]["captions"]
        w, _ = self.canvas_size
        return CaptionZone(y0=c["y0"], y1=c["y1"], max_width=c["max_width"],
                           x_center=c.get("x_center", w // 2), max_lines=c.get("max_lines"))

    def card_box(self) -> tuple[int, int, int, int]:
        b = self.layout["card"]["box"]
        return b["x0"], b["y0"], b["x1"], b["y1"]

    @property
    def card_pad(self) -> int:
        return int(self.layout["card"]["pad"])

    def letterbox_band(self) -> tuple[int, int]:
        b = self.layout["clip"]["letterbox_band"]
        return b["y0"], b["y1"]

    def fit_box(self) -> tuple[int, int, int, int]:
        """(x0, y0, x1, y1) a CLIP-mode source of the *other* orientation is
        fitted into: the 9:16 layout's full-width letterbox band, or the
        16:9 layout's `fit_band` (full height, pillarboxed)."""
        clip = self.layout["clip"]
        if "fit_band" in clip:
            b = clip["fit_band"]
            return b["x0"], b["y0"], b["x1"], b["y1"]
        w, _ = self.canvas_size
        y0, y1 = self.letterbox_band()
        return 0, y0, w, y1

    def source_fills_canvas(self, sw: int, sh: int) -> bool:
        """True when a source's orientation matches the canvas (cover-crop
        it full-bleed); False means fit it inside fit_box() over a blurred
        cover copy instead."""
        w, h = self.canvas_size
        return (sw <= sh) == (w <= h)

    def letterbox_bg(self) -> dict:
        return self.layout["clip"]["letterbox_bg"]

    def freeze_spec(self) -> dict:
        return self.layout["host"]["freeze"]

    def platform_safe(self) -> dict:
        return self.layout["platform_safe"]

    # ---- typography -----------------------------------------------------

    def text_style(self, name: str) -> dict:
        """A caption style (style_capy/style_source/style_card) or a
        card_text entry via dotted name, e.g. text_style("card_text.quote")."""
        if name.startswith("card_text."):
            node: Any = self.data["card_text"]
            for part in name.split(".")[1:]:
                node = node[part]
            return node
        return self.data["captions"][name]

    def caption_style(self, name: str) -> dict:
        return self.data["captions"][name]

    def font_path(self, which: str) -> Path:
        rel = self.data["fonts"][f"{which}_file"]
        return REPO_ROOT / "assets" / "saint-capybara" / rel

    def font_name(self, which: str) -> str:
        return self.data["fonts"][which]

    def font_hash(self, which: str) -> str:
        if which not in self._font_hash_cache:
            self._font_hash_cache[which] = hashlib.sha256(self.font_path(which).read_bytes()).hexdigest()
        return self._font_hash_cache[which]

    # ---- colors -----------------------------------------------------

    def color(self, key: str) -> tuple[int, int, int]:
        val = self.data["palette"][key]
        if isinstance(val, str):
            return _hex_to_rgb(val)
        return tuple(val[:3])  # type: ignore[return-value]

    def color_rgba(self, key: str, alpha: int = 255) -> tuple[int, int, int, int]:
        r, g, b = self.color(key)
        return (r, g, b, alpha)

    # ---- sprites -----------------------------------------------------

    def sprite_path(self, pose: str) -> Path:
        return SPRITES_DIR / f"{pose}.png"

    def finalized_sprite_path(self, pose: str) -> Path:
        """Path to the real, currently-used sprite art for `pose` -- see
        FINALIZED_SPRITES_DIR."""
        return FINALIZED_SPRITES_DIR / f"saint-capybara-{pose}.png"

    def sprite_hash(self, pose: str) -> str:
        if pose not in self._sprite_hash_cache:
            path = self.finalized_sprite_path(pose)
            if not path.exists():
                path = self.sprite_path(pose)
            self._sprite_hash_cache[pose] = hashlib.sha256(path.read_bytes()).hexdigest()
        return self._sprite_hash_cache[pose]

    # ---- cache dirs -----------------------------------------------------

    def cache_root(self) -> Path:
        root = os.environ.get("CAPY_CACHE_DIR") or self.data["cache"]["root"]
        path = Path(root)
        if not path.drive or not Path(path.drive + "\\").exists():
            raise ThemeError(
                f"cache root drive {path.drive!r} is not present (root={path}) -- "
                "set CAPY_CACHE_DIR or check the drive is attached before rendering."
            )
        return path

    def cache_dir(self, sub: str) -> Path:
        rel = self.data["cache"].get(sub, sub)
        path = self.cache_root() / rel
        path.mkdir(parents=True, exist_ok=True)
        return path

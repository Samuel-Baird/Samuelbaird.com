"""Thin accessor over assets/saint-capybara/theme.yaml's `layout`/`palette`/
`fonts`/`captions` blocks, so tools/capy/plates.py and captions.py never
hardcode a zone's pixel coordinates -- everything is read from theme.yaml.

    from capy.layout import Theme
    theme = Theme.load()
    theme.sprite_box()      # (x0, y0, x1, y1)
    theme.color("parchment") # (r,g,b,a) or (r,g,b)
"""
from __future__ import annotations

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


def _hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


class Theme:
    def __init__(self, data: dict):
        self.data = data

    @classmethod
    def load(cls, path: Path | None = None) -> "Theme":
        path = path or THEME_PATH
        return cls(yaml.safe_load(path.read_text(encoding="utf-8")))

    @property
    def layout(self) -> dict:
        return self.data["layout"]

    @property
    def canvas_size(self) -> tuple[int, int]:
        c = self.layout["canvas"]
        return c["width"], c["height"]

    @property
    def fps(self) -> int:
        return self.layout["canvas"]["fps"]

    def zone(self, name: str) -> dict:
        return self.layout[name]

    def sprite_box(self) -> tuple[int, int, int, int]:
        s = self.layout["sprite"]
        x0, y0, size = s["x0"], s["y0"], s["size"]
        return x0, y0, x0 + size, y0 + size

    def panel_box(self) -> tuple[int, int, int, int]:
        p = self.layout["panel"]
        return p["x0"], p["y0"], p["x1"], p["y1"]

    def stage_box(self) -> tuple[int, int, int, int]:
        s = self.layout["stage"]
        w, _ = self.canvas_size
        return 0, s["y0"], w, s["y1"]

    def caption_box(self) -> tuple[int, int, int, int]:
        c = self.layout["captions"]
        w, _ = self.canvas_size
        return 0, c["y0"], w, c["y1"]

    def wordmark_box(self) -> dict:
        return self.layout["wordmark"]

    def color(self, key: str) -> tuple[int, int, int]:
        val = self.data["palette"][key]
        if isinstance(val, str):
            return _hex_to_rgb(val)
        return tuple(val[:3])  # type: ignore[return-value]

    def color_rgba(self, key: str, alpha: int = 255) -> tuple[int, int, int, int]:
        r, g, b = self.color(key)
        return (r, g, b, alpha)

    def font_path(self, which: str) -> Path:
        rel = self.data["fonts"][f"{which}_file"]
        return REPO_ROOT / "assets" / "saint-capybara" / rel

    def font_name(self, which: str) -> str:
        return self.data["fonts"][which]

    def caption_style(self, name: str) -> dict:
        return self.data["captions"][name]

    def sprite_path(self, pose: str) -> Path:
        return SPRITES_DIR / f"{pose}.png"

    def sprite_manifest(self) -> dict:
        import json
        return json.loads((SPRITES_DIR / "manifest.json").read_text(encoding="utf-8"))

    def finalized_sprite_path(self, pose: str) -> Path:
        """Path to the real, currently-used sprite art for `pose` (or one
        of the four sign-* outro poses) -- see FINALIZED_SPRITES_DIR."""
        return FINALIZED_SPRITES_DIR / f"saint-capybara-{pose}.png"

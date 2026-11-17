"""Load the Saint Capybara theme (palette, fonts, layout) from
assets/saint-capybara/theme.yaml.

See ../../docs/saint-capybara/brand.md for what each color means and why
this is a *different* visual system from ../../docs/style-guide.md.

Usage (library only, no CLI):
    from capy.palette import load_theme, kit_dir
    theme = load_theme()
    rgba = theme["palette"]["fur"]
"""
from __future__ import annotations

import functools
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]


def kit_dir(kit: str | Path | None = None) -> Path:
    """Return the Saint Capybara shared-asset kit directory."""
    if kit:
        return Path(kit).resolve()
    return REPO_ROOT / "assets" / "saint-capybara"


@functools.lru_cache(maxsize=8)
def _load_yaml_cached(path_str: str) -> dict:
    path = Path(path_str)
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_theme(kit: str | Path | None = None) -> dict:
    """Load theme.yaml from the kit directory (cached per path)."""
    path = kit_dir(kit) / "theme.yaml"
    if not path.exists():
        raise FileNotFoundError(
            f"theme.yaml not found at {path} -- run from the repo, or pass --kit"
        )
    return _load_yaml_cached(str(path))


def rgba(theme: dict, key: str) -> tuple[int, int, int, int]:
    """Resolve a palette key to an (r, g, b, a) tuple.

    Accepts either a [r, g, b, a] list (already RGBA, as used for the
    sprite palette) or a "#RRGGBB" hex string (used for the frame/UI
    palette), and normalizes both to a 4-tuple.
    """
    value = theme["palette"][key]
    if isinstance(value, str):
        h = value.lstrip("#")
        r, g, b = (int(h[i : i + 2], 16) for i in (0, 2, 4))
        return (r, g, b, 255)
    r, g, b, a = value
    return (int(r), int(g), int(b), int(a))


def font_path(theme: dict, which: str, kit: str | Path | None = None) -> Path:
    """which is 'display' or 'body'."""
    rel = theme["fonts"][f"{which}_file"]
    return kit_dir(kit) / rel

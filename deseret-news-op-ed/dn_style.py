"""
Shared house style for the Deseret News op-ed graphics.

These charts are NOT produced by or for Deseret News' own art desk; they are
Latter-day Stats charts that borrow the newspaper's public color scheme so
they sit comfortably on its pages. Palette values come from the Deseret News
Brand Guide v.02 (8 Aug 2019): Deseret Yellow #ffd217, White/light gray
#f2f2f2, Gray 1 #424242, Gray 2 (off-black) #1e1e1e, True Black #000000.
No Deseret News logo, wordmark, beehive, or "period" device is used.

Typefaces are open substitutes for the guide's licensed faces:
  Poynter Old Style  -> Newsreader  (display: opsz 36; text: opsz 16)
  Benton Sans        -> Libre Franklin (an open Franklin Gothic revival; Benton
                        Sans is itself a Franklin Gothic descendant)
  Benton Sans Extra Compressed (the guide's "numbers and infographics" face)
                     -> Oswald
All font files are static instances in ./fonts/ generated from the Google
Fonts variable masters, so matplotlib can pick weights reliably.

Chart form follows the dataviz skill's rules: emphasis form (one hue + grays),
thin marks, hairline solid gridlines, direct labels in ink (text never wears
the series color), a legend whenever there are 2+ series, source line always.

Every render script does:

    import dn_style as dn
    fonts = dn.load_fonts()
    fig = dn.new_figure()                       # 12 x 8 in, 2400 x 1600 px
    y = dn.draw_header(fig, fonts, title, dek)  # returns y just below the dek
    dn.draw_footer(fig, fonts, source_lines)
    ... axes between y and dn.FOOTER_TOP ...
    dn.save(fig, "01_divergence")               # PNG @200dpi + SVG in ./out/
"""
from __future__ import annotations

import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.font_manager as fm  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
FONTS_DIR = HERE / "fonts"
OUT_DIR = HERE / "out"
DATA_JSON = HERE / "data" / "oped_data.json"

# ---- Palette (Deseret News brand guide values + two derived neutrals) ------
YELLOW = "#ffd217"      # Deseret Yellow - the emphasis hue (Latter-day Saints)
INK = "#1e1e1e"         # Gray 2 / off-black - primary text
BLACK = "#000000"       # True black - reserved; INK is the working dark
GRAY1 = "#424242"       # Gray 1 - the dark neutral series (Christians overall)
GRAY2 = "#8c8c8c"       # derived mid gray - the light neutral series (unaffiliated)
LIGHT = "#f2f2f2"       # guide's "white" - chip/track fills, table stripes
PAPER = "#ffffff"       # page surface
MUTED = "#5f5f5f"       # secondary text (>= 7:1 on white)
GRID = "#e3e3e3"        # hairline gridlines, one step off the surface
YELLOW_DEEP = "#c9a200" # only for a yellow *line's* end marker ring/edge if ever needed

# Entity colors: color follows the entity across every chart in the set.
SERIES = {
    "Latter-day Saints": YELLOW,
    "Christians": GRAY1,
    "All Christians": GRAY1,
    "Religiously unaffiliated": GRAY2,
    "Religiously affiliated": GRAY1,
}
# Ordinal gray ramp (light -> dark) for the children-ever-born distribution.
ORDINAL_GRAYS = ["#e6e6e6", "#bdbdbd", "#8c8c8c", "#5c5c5c", "#2b2b2b"]

# ---- Canvas -----------------------------------------------------------------
FIG_W_IN, FIG_H_IN, DPI = 12, 8, 200          # 2400 x 1600 px, 3:2 web graphic
SQUARE_W_IN, SQUARE_H_IN = 10, 10             # 2000 x 2000 px social variant
MARGIN_L, MARGIN_R = 0.055, 0.945             # figure-fraction text rail
FOOTER_TOP = 0.115                            # axes must stay above this

# Type sizes in points on the 12-in canvas (scale with fig width if square).
SIZE = {
    "title": 27,
    "dek": 14.5,
    "label": 13,
    "tick": 12.5,
    "value": 15,
    "hero": 44,
    "legend": 12.5,
    "source": 10.5,
    "note": 11,
}


def load_fonts() -> dict[str, fm.FontProperties]:
    files = {
        "display": "Newsreader36-Bold.ttf",
        "display_semi": "Newsreader36-SemiBold.ttf",
        "display_medium": "Newsreader36-Medium.ttf",
        "serif": "Newsreader16-Regular.ttf",
        "serif_semi": "Newsreader16-SemiBold.ttf",
        "serif_italic": "Newsreader16-Italic.ttf",
        "sans": "LibreFranklin-Regular.ttf",
        "sans_medium": "LibreFranklin-Medium.ttf",
        "sans_semibold": "LibreFranklin-SemiBold.ttf",
        "sans_bold": "LibreFranklin-Bold.ttf",
        "sans_xbold": "LibreFranklin-ExtraBold.ttf",
        "sans_italic": "LibreFranklin-Italic.ttf",
        "numeral": "Oswald-Medium.ttf",
        "numeral_regular": "Oswald-Regular.ttf",
        "numeral_semibold": "Oswald-SemiBold.ttf",
    }
    fonts = {}
    for key, name in files.items():
        path = FONTS_DIR / name
        if not path.exists():
            raise FileNotFoundError(f"missing font {path}")
        fonts[key] = fm.FontProperties(fname=str(path))
    return fonts


def fp(fonts, key: str, size: float) -> fm.FontProperties:
    """A copy of a loaded FontProperties at a given size."""
    p = fonts[key].copy()
    p.set_size(size)
    return p


def new_figure(square: bool = False):
    if square:
        fig = plt.figure(figsize=(SQUARE_W_IN, SQUARE_H_IN), dpi=DPI, facecolor=PAPER)
    else:
        fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI, facecolor=PAPER)
    return fig


def wrap(text: str, width: int) -> str:
    return "\n".join(textwrap.wrap(text, width=width))


def draw_header(fig, fonts, title: str, dek: str | None = None, *, top: float = 0.945,
                title_wrap: int = 52, dek_wrap: int = 105, kicker: str | None = None) -> float:
    """Title (serif display, ink) and dek (sans, muted) on the left rail.
    Returns the y (figure fraction) just below the last header line."""
    y = top
    if kicker:
        fig.text(MARGIN_L, y, kicker.upper(), fontproperties=fp(fonts, "sans_semibold", 11.5),
                 color=MUTED, ha="left", va="top")
        y -= 0.036
    title_lines = textwrap.wrap(title, width=title_wrap)
    fig.text(MARGIN_L, y, "\n".join(title_lines), fontproperties=fp(fonts, "display", SIZE["title"]),
             color=INK, ha="left", va="top", linespacing=1.12)
    y -= 0.062 * len(title_lines) + 0.012
    if dek:
        dek_lines = textwrap.wrap(dek, width=dek_wrap)
        fig.text(MARGIN_L, y, "\n".join(dek_lines), fontproperties=fp(fonts, "sans", SIZE["dek"]),
                 color=MUTED, ha="left", va="top", linespacing=1.35)
        # 14.5pt * 1.35 linespacing = 19.6pt per line = 0.034 of an 8in canvas,
        # plus a real gap so a legend row placed at the returned y clears the dek.
        y -= 0.034 * len(dek_lines) + 0.028
    return y


def draw_footer(fig, fonts, source_lines: list[str], *, credit: str = "Chart: Latter-day Stats",
                rule: bool = True) -> None:
    """Hairline rule, then source/method lines (left) and the credit (right),
    all in muted sans. Keep to 1-3 short lines; wrap at ~150 chars."""
    y_rule = FOOTER_TOP - 0.02
    if rule:
        fig.add_artist(plt.Line2D([MARGIN_L, MARGIN_R], [y_rule, y_rule], transform=fig.transFigure,
                                  color=GRID, linewidth=1.0))
    # Credit sits on its own, right-aligned just ABOVE the rule, so it can never
    # collide with a long first source line below the rule.
    fig.text(MARGIN_R, y_rule + 0.008, credit, fontproperties=fp(fonts, "sans_semibold", SIZE["source"]),
             color=INK, ha="right", va="bottom")
    # Two 10.5pt lines at 1.25 leading end ~50px above the 1600px canvas edge
    # (1.4 leading left only ~30px, which read as cramped next to the 92px top
    # margin). A third line still does not fit - keep footers to two lines.
    y = y_rule - 0.019
    lines = [ln for para in source_lines for ln in textwrap.wrap(para, width=175)]
    if len(lines) > 2:
        raise ValueError(f"footer has {len(lines)} lines; keep source text to 2 wrapped lines")
    fig.text(MARGIN_L, y, "\n".join(lines), fontproperties=fp(fonts, "sans", SIZE["source"]),
             color=MUTED, ha="left", va="top", linespacing=1.25)


def style_axes(ax, *, fonts, grid_axis: str = "x", show_bottom: bool = True, show_left: bool = False):
    """Recessive chrome: no box, one hairline baseline, solid hairline grid."""
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(False)
    if show_bottom:
        ax.spines["bottom"].set_visible(True)
        ax.spines["bottom"].set_color(GRID)
        ax.spines["bottom"].set_linewidth(1.0)
    if show_left:
        ax.spines["left"].set_visible(True)
        ax.spines["left"].set_color(GRID)
        ax.spines["left"].set_linewidth(1.0)
    ax.set_facecolor(PAPER)
    ax.tick_params(axis="both", length=0, pad=8, colors=MUTED)
    for lab in ax.get_xticklabels() + ax.get_yticklabels():
        lab.set_fontproperties(fp(fonts, "sans", SIZE["tick"]))
        lab.set_color(MUTED)
    if grid_axis:
        ax.grid(axis=grid_axis, color=GRID, linewidth=1.0, linestyle="-", zorder=0)
        ax.set_axisbelow(True)


def chip_kwargs(fill: str = YELLOW, pad: float = 0.35):
    """bbox kwargs for the brand's yellow value chip (black text on yellow)."""
    return dict(boxstyle=f"round,pad={pad},rounding_size=0.25", facecolor=fill, edgecolor="none")


def legend_swatches(fig, fonts, entries: list[tuple[str, str]], *, x: float, y: float, gap: float = 0.018,
                    swatch: str = "square") -> None:
    """A horizontal legend row drawn in figure coordinates: colored swatch +
    ink label per entry. `entries` is [(label, color), ...]. Always call
    this when a chart has 2+ series, even if they are direct-labeled."""
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    cx = x
    for label, color in entries:
        if swatch == "line":
            fig.add_artist(plt.Line2D([cx, cx + 0.022], [y, y], transform=fig.transFigure,
                                      color=color, linewidth=4, solid_capstyle="round"))
            cx += 0.028
        else:
            fig.patches.append(plt.Rectangle((cx, y - 0.009), 0.012, 0.018, transform=fig.transFigure,
                                             facecolor=color, edgecolor="none"))
            cx += 0.018
        t = fig.text(cx, y, label, fontproperties=fp(fonts, "sans_medium", SIZE["legend"]),
                     color=INK, ha="left", va="center")
        bb = t.get_window_extent(renderer=renderer)
        cx += bb.width / (fig.get_figwidth() * fig.dpi) + gap


def save(fig, stem: str, *, png: bool = True, svg: bool = True) -> list[Path]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    if png:
        p = OUT_DIR / f"{stem}.png"
        fig.savefig(p, dpi=DPI, facecolor=PAPER)
        written.append(p)
    if svg:
        p = OUT_DIR / f"{stem}.svg"
        fig.savefig(p, format="svg", facecolor=PAPER)
        written.append(p)
    plt.close(fig)
    return written

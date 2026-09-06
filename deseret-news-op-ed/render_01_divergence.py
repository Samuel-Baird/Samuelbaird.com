"""
Chart 01 - "Divergence": share of U.S. adults who are Christian, religiously
unaffiliated, or Latter-day Saint across Pew's three Religious Landscape
Studies (2007, 2014, 2023-24).

Every number is read from data/oped_data.json at run time; nothing is typed in.
Output: out/01_divergence.png (2400x1600 @200dpi) and out/01_divergence.svg.
"""
from __future__ import annotations

import json
import textwrap

from matplotlib.transforms import offset_copy

import dn_style as dn

STEM = "01_divergence"
WAVE_KEYS = ["2007", "2014", "2023-24"]
X_OF = {"2007": 2007.0, "2014": 2014.0, "2023-24": 2023.5}
X_FIRST, X_LAST = X_OF[WAVE_KEYS[0]], X_OF[WAVE_KEYS[-1]]

# (legend/label name, JSON key, color, line width, value decimals)
SERIES = [
    ("Christians", "Christian", dn.SERIES["Christians"], 3.0, 0),
    ("Religiously unaffiliated", "Religiously unaffiliated", dn.SERIES["Religiously unaffiliated"], 3.0, 0),
    ("Latter-day Saints", "Latter-day Saints", dn.SERIES["Latter-day Saints"], 4.5, 1),
]

DOT_PT = 7.2        # dot diameter in points (~20 px at 200 dpi, ~10 px at half scale)
RING_PT = 1.4       # paper ring width in points (~4 px at 200 dpi, ~2 px at half scale)
SIZE_START = dn.SIZE["tick"]     # 12.5pt muted start values
SIZE_END = 14.5                  # end labels: name (medium) + value (bold), ink


def pct(v: float, decimals: int) -> str:
    return f"{v:.{decimals}f}%"


def main() -> None:
    fonts = dn.load_fonts()
    with open(dn.DATA_JSON, encoding="utf-8") as f:
        data = json.load(f)
    waves = data["waves"]
    pub_lds = data["published"]["shares_rounded"]["Latter-day Saints"]
    pub_lds_vals = {pub_lds[k] for k in WAVE_KEYS}
    assert len(pub_lds_vals) == 1, "title assumes Pew rounds every wave to the same figure"
    pub_lds_round = next(iter(pub_lds_vals))

    # ---- Header ---------------------------------------------------------------
    title = (f"Christians shrank, the unaffiliated grew, and Latter-day Saints "
             f"held near {pub_lds_round}% of Americans")
    dek = ("Share of U.S. adults identifying with each group in Pew Research Center's "
           "three Religious Landscape Studies, fielded in 2007, 2014 and 2023-24.")
    fig = dn.new_figure()
    y_hdr = dn.draw_header(fig, fonts, title, dek)

    # Legend row (required for 2+ series even though the lines are direct-labeled).
    y_leg = y_hdr - 0.012
    dn.legend_swatches(fig, fonts, [(name, color) for name, _, color, _, _ in SERIES],
                       x=dn.MARGIN_L, y=y_leg, swatch="line")

    # ---- Footer ---------------------------------------------------------------
    n = {k: waves[k]["n"] for k in WAVE_KEYS}
    n_lds = {k: waves[k]["n_lds"] for k in WAVE_KEYS}
    lds = {k: waves[k]["Latter-day Saints"] for k in WAVE_KEYS}
    # Two explicit lines (a third line at draw_footer's spacing runs below the
    # canvas). Line 1 follows the set-wide source template exactly:
    #   "Source: Pew Research Center, Religious Landscape Study, <waves>;
    #    public-use microdata, weighted."
    footer_lines = [
        f"Source: Pew Research Center, Religious Landscape Study, 2007, 2014 and 2023-24; "
        f"public-use microdata, weighted (N={n['2007']:,}, {n['2014']:,} and {n['2023-24']:,}).",
        f"Latter-day Saint share shown to one decimal "
        f"({pct(lds['2007'], 1)}, {pct(lds['2014'], 1)}, {pct(lds['2023-24'], 1)}; unweighted "
        f"n={n_lds['2007']}, {n_lds['2014']}, {n_lds['2023-24']}); Pew rounds all three to {pub_lds_round}%. "
        f"2007 covers the continental U.S.",
    ]
    n_fig_texts_before = len(fig.texts)
    dn.draw_footer(fig, fonts, footer_lines)
    # Measured fit: every footer line must end inside the text rail (not merely
    # on the canvas), and draw_footer must not have wrapped either line.
    fig.canvas.draw()
    r0 = fig.canvas.get_renderer()
    W0 = fig.get_figwidth() * fig.dpi
    footer_texts = fig.texts[n_fig_texts_before:]
    body = [t for t in footer_texts if t.get_text().startswith("Source:")][0]
    assert body.get_text().count("\n") == len(footer_lines) - 1, "draw_footer wrapped a footer line"
    assert body.get_window_extent(r0).x1 <= dn.MARGIN_R * W0 + 1, \
        f"footer runs past the rail: {body.get_window_extent(r0).x1 / W0:.3f} > {dn.MARGIN_R}"

    # ---- Axes -----------------------------------------------------------------
    ax_left = 0.10                      # leaves room for "80%" tick labels on the rail
    ax_top = y_leg - 0.048
    ax_bottom = dn.FOOTER_TOP + 0.05 + 0.04  # x tick labels hang ~0.036 below the axes
    ax = fig.add_axes([ax_left, ax_bottom, dn.MARGIN_R - ax_left, ax_top - ax_bottom])

    ax.set_ylim(0, 80)
    ax.set_yticks([0, 20, 40, 60, 80])
    ax.set_yticklabels([f"{t}%" for t in [0, 20, 40, 60, 80]])
    ax.set_xticks([X_OF[k] for k in WAVE_KEYS])
    ax.set_xticklabels(WAVE_KEYS)
    ax.set_xlim(2005, 2033)             # provisional; recomputed from label widths below
    dn.style_axes(ax, fonts=fonts, grid_axis="y", show_bottom=True)

    # Lines and dots. Latter-day Saints drawn last so the yellow line sits on top.
    xs = [X_OF[k] for k in WAVE_KEYS]
    for i, (name, key, color, lw, _) in enumerate(SERIES):
        ys = [waves[k][key] for k in WAVE_KEYS]
        ax.plot(xs, ys, color=color, linewidth=lw, solid_capstyle="round",
                solid_joinstyle="round", zorder=2 + i, clip_on=False)
        # paper ring (a larger paper disc underneath) + filled dot, no strokes
        ax.scatter(xs, ys, s=(DOT_PT + 2 * RING_PT) ** 2, facecolor=dn.PAPER,
                   edgecolor="none", zorder=5 + i, clip_on=False)
        ax.scatter(xs, ys, s=DOT_PT ** 2, facecolor=color, edgecolor="none",
                   zorder=6 + i, clip_on=False)

    # ---- Direct labels ----------------------------------------------------------
    start_off = offset_copy(ax.transData, fig=fig, x=-10, y=0, units="points")
    end_off = offset_copy(ax.transData, fig=fig, x=11, y=0, units="points")
    start_texts, end_names, end_values = [], [], []
    for name, key, _, _, dec in SERIES:
        v0, v1 = waves[WAVE_KEYS[0]][key], waves[WAVE_KEYS[-1]][key]
        start_texts.append(ax.text(X_FIRST, v0, pct(v0, dec), transform=start_off,
                                   ha="right", va="center", color=dn.MUTED,
                                   fontproperties=dn.fp(fonts, "sans", SIZE_START), clip_on=False))
        end_names.append(ax.text(X_LAST, v1, name, transform=end_off, ha="left", va="center",
                                 color=dn.INK, fontproperties=dn.fp(fonts, "sans_medium", SIZE_END),
                                 clip_on=False))
        end_values.append((v1, pct(v1, dec)))

    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    px_per_pt = fig.dpi / 72.0

    # Place each end value just after its name (measured, so the gap is exact).
    value_texts = []
    for name_t, (v1, label) in zip(end_names, end_values):
        w_pt = name_t.get_window_extent(r).width / px_per_pt
        off = offset_copy(ax.transData, fig=fig, x=11 + w_pt + 4, y=0, units="points")
        value_texts.append(ax.text(X_LAST, v1, label, transform=off, ha="left", va="center",
                                   color=dn.INK, fontproperties=dn.fp(fonts, "sans_bold", SIZE_END),
                                   clip_on=False))
    fig.canvas.draw()

    # Fit xlim so start labels clear the left edge and end labels the right edge.
    ax_bb = ax.get_window_extent(r)
    x_first_px = ax.transData.transform((X_FIRST, 0))[0]
    x_last_px = ax.transData.transform((X_LAST, 0))[0]
    left_px = max(x_first_px - t.get_window_extent(r).x0 for t in start_texts) + 80
    right_px = max(t.get_window_extent(r).x1 - x_last_px for t in value_texts) + 12
    px_per_year = (ax_bb.width - left_px - right_px) / (X_LAST - X_FIRST)
    ax.set_xlim(X_FIRST - left_px / px_per_year, X_LAST + right_px / px_per_year)
    fig.canvas.draw()

    # No label may sit on a hairline. Lift any label whose box dips below the
    # baseline (the 1.5%-1.7% Latter-day Saint points), then nudge any label a
    # gridline grazes (e.g. "78%" under the 80% line) away from that gridline.
    px_per_unit = ax.transData.get_matrix()[1, 1]
    y0_px = ax.transData.transform((X_FIRST, 0))[1]
    grid_px = [ax.transData.transform((X_FIRST, g))[1] for g in ax.get_yticks()]
    clear = 3 * px_per_pt
    for t in start_texts + end_names + value_texts:
        bb = t.get_window_extent(r)
        if bb.y0 < y0_px + clear:
            x, y = t.get_position()
            t.set_position((x, y + (y0_px + clear - bb.y0) / px_per_unit))
            fig.canvas.draw()
            bb = t.get_window_extent(r)
        for gy in grid_px:
            if gy <= y0_px:
                continue
            if bb.y0 - clear < gy < bb.y1 + clear:
                mid = (bb.y0 + bb.y1) / 2
                shift_px = (gy - clear) - bb.y1 if gy > mid else (gy + clear) - bb.y0
                x, y = t.get_position()
                t.set_position((x, y + shift_px / px_per_unit))
                fig.canvas.draw()
                bb = t.get_window_extent(r)
    fig.canvas.draw()

    # ---- Overflow audit (fail loudly rather than ship a clipped label) -----------
    W, H = fig.get_figwidth() * fig.dpi, fig.get_figheight() * fig.dpi
    worst_right = 0.0
    for t in fig.texts + ax.texts:
        bb = t.get_window_extent(r)
        assert bb.x0 >= 0 and bb.y0 >= 0 and bb.x1 <= W and bb.y1 <= H, \
            f"text runs off canvas: {t.get_text()!r} {bb}"
        worst_right = max(worst_right, bb.x1 / W)
    for t in ax.texts:  # data labels must stay inside the axes box
        bb = t.get_window_extent(r)
        assert ax_bb.x0 <= bb.x0 and bb.x1 <= ax_bb.x1 + 1, f"label outside axes: {t.get_text()!r}"
    print(f"xlim={ax.get_xlim()}  widest text right edge = {worst_right:.3f} of canvas "
          f"(rail ends at {dn.MARGIN_R})")
    print("footer lines:", len(footer_lines))
    for ln in footer_lines:
        print("  ", ln)

    for p in dn.save(fig, STEM):
        print("wrote", p)


if __name__ == "__main__":
    main()

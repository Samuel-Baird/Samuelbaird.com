"""
Chart 03 - Completed fertility distribution (supporting graphic).

Two 100%-stacked horizontal bars: number of children ever born to U.S. adults
born in the 1960s-1970s, all Christians vs. religiously unaffiliated (the same
"All Christians" base chart 06 uses, so the 3+ share reads identically),
from the 2023-24 Pew RLS public-use file (data/oped_data.json).

Every number on the chart is read from the JSON at runtime and rounded for
display only.
"""
from __future__ import annotations

import json
from decimal import Decimal, ROUND_HALF_UP

import dn_style as dn

STEM = "03_completed_fertility"

ROWS = ["All Christians", "Religiously unaffiliated"]          # top -> bottom
CATS = ["None", "1", "2", "3", "4 or more"]                     # light -> dark
MIN_LABEL_PCT = 6.0       # label a segment only if it is at least this wide
BAR_H = 0.38              # bar height as a share of the row slot

TITLE = "Christian Americans finish their childbearing years with larger families than the unaffiliated"
DEK = ("Number of children ever born to U.S. adults born in the 1960s and 1970s "
       "(roughly ages 44 to 64 when surveyed), Christians compared with the religiously unaffiliated, 2023-24.")


def pct(v: float) -> int:
    """Round half-up for display (avoids banker's rounding on exact .5)."""
    return int(Decimal(str(v)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def rel_luminance(hex_color: str) -> float:
    h = hex_color.lstrip("#")
    rgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def text_color_on(fill: str) -> str:
    """White on dark fills, ink on light ones (contrast-driven)."""
    return dn.PAPER if rel_luminance(fill) < 0.18 else dn.INK


def text_width_frac(fig, renderer, s: str, prop) -> float:
    w_px = renderer.get_text_width_height_descent(s, prop, ismath=False)[0]
    return w_px / (fig.get_figwidth() * fig.dpi)


def measured_wrap(fig, renderer, text: str, prop, max_frac: float) -> list[str]:
    """Greedy word wrap using real glyph widths, not a character count."""
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if not cur or text_width_frac(fig, renderer, trial, prop) <= max_frac:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def check_bounds(fig, right_rail: float) -> None:
    """Warn if any text runs off the canvas or past the right text rail."""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    W, H = fig.get_figwidth() * fig.dpi, fig.get_figheight() * fig.dpi
    texts = list(fig.texts)
    for ax in fig.axes:
        texts += ax.texts + ax.get_xticklabels() + ax.get_yticklabels()
    bad = 0
    for t in texts:
        if not t.get_text():
            continue
        bb = t.get_window_extent(renderer=r)
        if bb.x0 < -0.5 or bb.y0 < -0.5 or bb.x1 > W + 0.5 or bb.y1 > H + 0.5:
            print(f"OFF-CANVAS: {t.get_text()[:40]!r} bbox={bb}")
            bad += 1
        elif bb.x1 > right_rail * W + 0.5:
            print(f"PAST RIGHT RAIL: {t.get_text()[:40]!r} x1={bb.x1:.0f} rail={right_rail * W:.0f}")
            bad += 1
    live = [(t, t.get_window_extent(renderer=r)) for t in texts if t.get_text()]
    for i in range(len(live)):
        for j in range(i + 1, len(live)):
            a, b = live[i][1], live[j][1]
            # Oswald's line box is far taller than its digit ink; the stacked
            # callout numerals are spaced by baseline and checked by eye.
            if all("Oswald" in str(live[k][0].get_fontproperties().get_file()) for k in (i, j)):
                continue
            if a.x0 < b.x1 and b.x0 < a.x1 and a.y0 < b.y1 and b.y0 < a.y1:
                print(f"OVERLAP: {live[i][0].get_text()[:30]!r} <-> {live[j][0].get_text()[:30]!r}")
                bad += 1
    print(f"bounds check: {len(texts)} text artists, {bad} problems")


def main() -> None:
    with open(dn.DATA_JSON, encoding="utf-8") as f:
        data = json.load(f)
    cohort = data["fertility_2023_24"]["born_1960s_1970s"]
    groups = cohort["groups"]
    pub = data["published"]["fertility_ages_40_59_mean_children"]

    fonts = dn.load_fonts()
    fig = dn.new_figure()
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()

    # ---- header + legend --------------------------------------------------
    y_hdr = dn.draw_header(fig, fonts, TITLE, DEK)
    y_leg = y_hdr - 0.006
    lead = "Number of children"
    lead_prop = dn.fp(fonts, "sans", dn.SIZE["legend"])
    fig.text(dn.MARGIN_L, y_leg, lead, fontproperties=lead_prop, color=dn.MUTED,
             ha="left", va="center")
    x_leg = dn.MARGIN_L + text_width_frac(fig, renderer, lead, lead_prop) + 0.014
    dn.legend_swatches(fig, fonts, list(zip(CATS, dn.ORDINAL_GRAYS)), x=x_leg, y=y_leg,
                       swatch="square", gap=0.022)

    # ---- footer + method note ---------------------------------------------
    # dn.draw_footer's third line falls below the canvas at 10.5pt x 1.4, so the
    # footer is held to two lines and the method caveat becomes a note block in
    # the space between the axis and the footer rule.
    n_chr = groups["All Christians"]["unweighted_n"]
    n_un = groups["Religiously unaffiliated"]["unweighted_n"]
    # Shared template across the set: "Source: Pew Research Center, Religious
    # Landscape Study, <waves>; public-use microdata, weighted."
    source = ("Source: Pew Research Center, Religious Landscape Study, 2023-24; "
              "public-use microdata, weighted. "
              f"Unweighted n: Christians {n_chr:,}; unaffiliated {n_un:,}.")
    rounding = "Percentages are rounded and may not sum to 100."
    method = (f"Note: Pew's published averages for adults ages 40-59 are {pub['Christians']} children "
              f"among Christians and {pub['Religiously unaffiliated']} among the religiously "
              "unaffiliated. The public-use file reports birth decade rather than exact age and "
              "caps counts at '4 or more', so this chart shows the full distribution instead.")
    src_prop = dn.fp(fonts, "sans", dn.SIZE["source"])
    note_prop = dn.fp(fonts, "sans", dn.SIZE["note"])
    rail = (dn.MARGIN_R - dn.MARGIN_L) * 0.995
    footer_lines = (measured_wrap(fig, renderer, source, src_prop, rail)
                    + measured_wrap(fig, renderer, rounding, src_prop, rail))
    note_lines = measured_wrap(fig, renderer, method, note_prop, rail)
    print("footer lines:", len(footer_lines), "| note lines:", len(note_lines))
    for ln in footer_lines + note_lines:
        print(f"  [{len(ln):3d} ch, {text_width_frac(fig, renderer, ln, src_prop):.3f} fig] {ln}")
    if len(footer_lines) > 2:
        raise SystemExit("footer would run off the canvas: keep it to 2 lines")
    if len(note_lines) > 2:
        raise SystemExit("method note too long: keep it to 2 lines")
    dn.draw_footer(fig, fonts, footer_lines)
    y_note_top = 0.205
    fig.text(dn.MARGIN_L, y_note_top, "\n".join(note_lines), fontproperties=note_prop,
             color=dn.MUTED, ha="left", va="top", linespacing=1.35)

    # ---- axes -------------------------------------------------------------
    ax_left, ax_right = dn.MARGIN_L, 0.77
    ax_bottom, ax_top = 0.27, y_leg - 0.07
    ax = fig.add_axes([ax_left, ax_bottom, ax_right - ax_left, ax_top - ax_bottom])
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.5, 1.5)
    ax.set_xticks(range(0, 101, 20))
    ax.set_xticklabels([f"{t}%" for t in range(0, 101, 20)])
    ax.set_yticks([])
    dn.style_axes(ax, fonts=fonts, grid_axis="x", show_bottom=True)
    ax.get_xticklabels()[0].set_ha("left")     # keep "0%" flush with the left rail

    seg_prop = dn.fp(fonts, "sans_semibold", 14)
    row_prop = dn.fp(fonts, "sans_semibold", 13.5)
    shown = []   # (label, value, json key) for the report
    bar_centers = {}
    for i, row in enumerate(ROWS):
        y = 1 - i
        bar_centers[row] = y
        dist = groups[row]["distribution_pct"]
        left = 0.0
        for k, cat in enumerate(CATS):
            v = dist[cat]
            fill = dn.ORDINAL_GRAYS[k]
            ax.barh(y, v, left=left, height=BAR_H, color=fill,
                    edgecolor=dn.PAPER, linewidth=2, zorder=3)
            if v >= MIN_LABEL_PCT:
                ax.text(left + v / 2, y, f"{pct(v)}%", ha="center", va="center",
                        color=text_color_on(fill), fontproperties=seg_prop, zorder=4)
                shown.append((f"{row} / {cat}", f"{pct(v)}%",
                              f"fertility_2023_24.born_1960s_1970s.groups[{row!r}].distribution_pct[{cat!r}]"))
            left += v
        ax.text(0, y + BAR_H / 2 + 0.07, row, ha="left", va="bottom",
                color=dn.INK, fontproperties=row_prop, zorder=4,
                bbox=dict(facecolor=dn.PAPER, edgecolor="none", pad=2.0))

    # ---- callouts to the right of each bar --------------------------------
    fig_h_px = fig.get_figheight() * fig.dpi
    x_call = ax_right + 0.018
    hero_prop = dn.fp(fonts, "numeral", 36)
    hero_word = dn.fp(fonts, "sans_medium", 14.5)
    sub_prop = dn.fp(fonts, "numeral_regular", 20)
    sub_word = dn.fp(fonts, "sans", 13)
    for row in ROWS:
        g = groups[row]
        y_c = ax.transData.transform((0, bar_centers[row]))[1] / fig_h_px
        # line 1: "36%  have 3+"
        s3 = f"{pct(g['share_3_or_more_pct'])}%"
        y1 = y_c - 0.006
        fig.text(x_call, y1, s3, fontproperties=hero_prop, color=dn.INK, ha="left", va="baseline")
        x2 = x_call + text_width_frac(fig, renderer, s3, hero_prop) + 0.007
        fig.text(x2, y1, "have 3+", fontproperties=hero_word, color=dn.INK, ha="left", va="baseline")
        shown.append((f"{row} / have 3+", s3,
                      f"fertility_2023_24.born_1960s_1970s.groups[{row!r}].share_3_or_more_pct"))
        # line 2: "15%  have none" (muted, smaller)
        s0 = f"{pct(g['share_none_pct'])}%"
        y2 = y1 - 0.043
        fig.text(x_call, y2, s0, fontproperties=sub_prop, color=dn.MUTED, ha="left", va="baseline")
        x3 = x_call + text_width_frac(fig, renderer, s0, sub_prop) + 0.006
        fig.text(x3, y2, "have none", fontproperties=sub_word, color=dn.MUTED, ha="left", va="baseline")
        shown.append((f"{row} / have none", s0,
                      f"fertility_2023_24.born_1960s_1970s.groups[{row!r}].share_none_pct"))

    check_bounds(fig, dn.MARGIN_R)
    print("numbers shown:")
    for lab, val, key in shown:
        print(f"  {lab:40s} {val:>5s}  <- {key}")
    print("footer n:", n_chr, n_un, "| published means:", pub["Christians"], pub["Religiously unaffiliated"])
    paths = dn.save(fig, STEM)
    for p in paths:
        print("wrote", p)


if __name__ == "__main__":
    main()

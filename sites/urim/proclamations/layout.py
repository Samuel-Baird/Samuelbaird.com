"""Typesetting engine: styled words, optimal justified line breaking, two-column fitting.

All lengths are in the page's logical units (a 612-unit-wide design page). Nothing here draws;
render.py turns the resulting lines into PDF operations.
"""
import re
from dataclasses import dataclass, field

from .fonts import space_width, text_width, to_caps, is_upper

INF = float("inf")
HYPHEN_PENALTY = 30.0      # cost of ending a line with a hyphenated word
_hyph = {"dic": None}
_justify = {"on": True, "chars": False}
_brk = {"fn": None}
_RUN = re.compile(r"[^\W\d_]+")
_DASHES = "-–—"


def set_hyphenation(lang):
    """lang: a pyphen dictionary name ('en_US', 'es') or None for no dictionary hyphenation.
    Breaks after dashes are always allowed."""
    if lang is None:
        _hyph["dic"] = None
    else:
        import pyphen
        _hyph["dic"] = pyphen.Pyphen(lang=lang, left=2, right=3)


def set_justify(on, chars=False):
    """Justified columns stretch spaces to fill the measure; ragged-right columns never do (and never shrink
    them), which suits languages without a hyphenation dictionary and long words. With chars=True (Chinese,
    Japanese, Thai, ...) the slack is spread between characters, since there are few or no spaces."""
    _justify["on"] = bool(on)
    _justify["chars"] = bool(on and chars)


def set_breaker(name):
    """Line-break opportunities for a script written without spaces ('cjk', 'thai', 'khmer', 'lao', 'myanmar')."""
    from . import linebreak
    _brk["fn"] = linebreak.get(name)


def find_breaks(text):
    """Break opportunities inside one word: [(index, needs_hyphen)]. Capitalised words (names) and
    short words are not hyphenated."""
    out = [(i + 1, False) for i, ch in enumerate(text[:-1]) if ch in _DASHES and text[i + 1] not in _DASHES]
    if _brk["fn"] is not None:
        out += [(i, False) for i in _brk["fn"](text) if 0 < i < len(text)]
    dic = _hyph["dic"]
    if dic is not None and len(text) >= 6:
        for m in _RUN.finditer(text):
            run = m.group()
            if len(run) < 6 or run[0].isupper():
                continue
            for p in dic.positions(run):
                i = m.start() + p
                if i >= 2 and len(text) - i >= 3:
                    out.append((i, True))
    return sorted(set(out))
MAX_STRETCH = 2.2      # spaces may grow to 3.2x their natural width before a line is rejected
MAX_SHRINK = 0.30      # and shrink by at most 30%


@dataclass
class Seg:
    text: str
    size: float
    style: str = "r"            # r / i / b
    color: tuple = (0, 0, 0)
    track: float = 0.0
    mode: str = "fill"          # fill / open
    stroke: tuple = None
    stroke_w: float = 0.0

    @property
    def width(self):
        return text_width(self.text, self.size, self.style, self.track)


@dataclass
class Word:
    segs: list
    width: float = 0.0
    breaks: tuple = ()          # [(char index, needs hyphen)] inside a single-segment word
    cont: bool = False          # this fragment continues the previous one (no space between)
    hy: bool = False            # a break before this fragment needs a hyphen

    def __post_init__(self):
        self.width = sum(s.width for s in self.segs)


def word(text, size, style="r", color=(0, 0, 0), hyphenate=True):
    w = Word([Seg(text, size, style, color)])
    if hyphenate:
        w.breaks = tuple(find_breaks(text))
    return w


def expand(words):
    """Replace each breakable word by its fragments (marked cont/hy) so the line breaker can split it."""
    items = []
    for w in words:
        if not w.breaks or len(w.segs) != 1:
            items.append(w)
            continue
        seg = w.segs[0]
        cuts = [0] + [i for i, _ in w.breaks] + [len(seg.text)]
        flags = [False] + [h for _, h in w.breaks]
        for k in range(len(cuts) - 1):
            frag = Word([Seg(seg.text[cuts[k]:cuts[k + 1]], seg.size, seg.style, seg.color, seg.track,
                             seg.mode, seg.stroke, seg.stroke_w)], cont=k > 0, hy=flags[k])
            items.append(frag)
    return items


def small_caps_word(text, big, small, color=(0, 0, 0), first_big=True, style="r"):
    """Capital initial at `big`, remaining letters as capitals at `small` (small caps). A caseless script has no
    small caps; its lead-in is set bold at about the body size instead."""
    if text.upper() == text.lower() and any(ch.isalpha() for ch in text) and not any(0x10400 <= ord(ch) <= 0x1044F for ch in text):
        return Word([Seg(text, small * 1.25, "b", color)])
    segs = []
    for i, ch in enumerate(text):
        if not ch.isalpha() and not (0x10400 <= ord(ch) <= 0x1044F):
            segs.append(("p", ch))
        elif i == 0 and first_big and is_upper(ch):
            segs.append(("b", ch))
        else:
            segs.append(("s", ch))
    out, cur = [], None
    for kind, ch in segs:
        if cur and cur[0] == kind:
            cur[1] += ch
        else:
            cur = [kind, ch]
            out.append(cur)
    result = []
    for kind, s in out:
        if kind == "b":
            result.append(Seg(s, big, style, color))
        elif kind == "s":
            result.append(Seg(to_caps(s), small, style, color))
        else:
            result.append(Seg(s, small, style, color))
    return Word(result)


@dataclass
class Para:
    words: list
    size: float                  # body size, for the space width
    leading: float
    gap_before: float = 0.0
    indent_first: float = 0.0    # first-line indent (LC style)
    dropcap_w: float = 0.0       # width reserved beside a drop cap
    dropcap_lines: int = 0
    justify: bool = True
    tag: str = ""                # lets the renderer find the first paragraph


@dataclass
class Line:
    words: list
    natural: float
    avail: float
    x_off: float                 # indent from the column's left edge
    last: bool                   # last line of its paragraph (not justified)
    gap_before: float = 0.0
    leading: float = 0.0
    para: int = 0
    first: bool = False
    hyphen: bool = False         # draw a hyphen after the last fragment (a word split across lines)
    justify: bool = True
    chars: bool = False          # spread the slack between characters instead of at spaces


def break_paragraph(para, col_w, space):
    """Minimum-badness line breaking (Knuth-Plass style). Words may be split at their break points,
    with a hyphen where the break needs one."""
    items = expand(para.words)
    ws = [w.width for w in items]
    n = len(ws)
    K = max(para.dropcap_lines, 1)
    hy_w = text_width("-", para.size) if any(w.hy for w in items) else 0.0
    shrink = MAX_SHRINK if _justify["on"] else 0.0

    def avail(k):
        a = col_w
        if para.dropcap_lines and k < para.dropcap_lines:
            a -= para.dropcap_w
        elif k == 0:
            a -= para.indent_first
        return a

    prefix, gaps_prefix = [0.0], [0]
    for k, w in enumerate(ws):
        prefix.append(prefix[-1] + w)
        gaps_prefix.append(gaps_prefix[-1] + (0 if (k == 0 or items[k].cont) else 1))

    best = {(0, 0): (0.0, None)}
    # states are processed in increasing item index; (i, k) with k = min(line_no, K)
    states_by_i = {0: {0}}
    for i in range(n):
        for k in sorted(states_by_i.get(i, ())):
            cost0 = best[(i, k)][0]
            a = avail(k)
            for j in range(i + 1, n + 1):
                gaps = gaps_prefix[j] - gaps_prefix[i + 1]       # spaces inside the line
                hyphen = j < n and items[j].cont and items[j].hy
                nat = prefix[j] - prefix[i] + gaps * space + (hy_w if hyphen else 0.0)
                if nat - gaps * space * (0.0 if _justify["chars"] else shrink) > a + 1e-6:
                    break
                last = j == n
                if last:
                    c = 0.0
                elif _justify["chars"]:
                    c = 100.0 * ((a - nat) / (0.5 * space * max(j - i - 1, 1))) ** 2
                elif gaps == 0:
                    c = 4000.0
                else:
                    r = (a - nat) / (gaps * space)
                    if r > MAX_STRETCH:
                        c = 300.0 + 400.0 * (r - MAX_STRETCH)
                    elif r >= 0:
                        c = 100.0 * r * r
                    else:
                        c = 100.0 * (r * 3.0) ** 2
                if hyphen:
                    c += HYPHEN_PENALTY
                if not last and j == n - 1:
                    c += 40.0           # discourage a single-word last line
                nk = min(k + 1, K)
                key = (j, nk)
                tot = cost0 + c
                if key not in best or tot < best[key][0]:
                    best[key] = (tot, (i, k))
                    states_by_i.setdefault(j, set()).add(nk)
    ends = [(best[(n, k)][0], (n, k)) for k in range(K + 1) if (n, k) in best]
    if not ends:
        return None
    _, state = min(ends)
    cuts = []
    while best[state][1] is not None:
        prev = best[state][1]
        cuts.append((prev[0], state[0], prev[1]))
        state = prev
    cuts.reverse()
    lines = []
    for idx, (i, j, k) in enumerate(cuts):
        gaps = gaps_prefix[j] - gaps_prefix[i + 1]
        hyphen = j < n and items[j].cont and items[j].hy
        nat = prefix[j] - prefix[i] + gaps * space + (hy_w if hyphen else 0.0)
        x_off = para.dropcap_w if (para.dropcap_lines and idx < para.dropcap_lines) else (para.indent_first if idx == 0 else 0.0)
        lines.append(Line(items[i:j], nat, avail(k), x_off, j == n, leading=para.leading, first=idx == 0, hyphen=hyphen,
                          justify=_justify["on"], chars=_justify["chars"]))
    return lines


def split_columns(lines, cap):
    """Split the line list into two columns at the most balanced point where both fit `cap`
    (distance from first to last baseline). Returns (col1, col2) or None."""
    def height(seq):
        if not seq:
            return 0.0
        h = 0.0
        for i, ln in enumerate(seq):
            if i:
                h += ln.leading + (ln.gap_before if ln.first else 0.0)
        return h

    best = None
    for k in range(1, len(lines)):
        h1, h2 = height(lines[:k]), height(lines[k:])
        if h1 <= cap + 1e-6 and h2 <= cap + 1e-6:
            score = max(h1, h2)
            if best is None or score < best[0] - 1e-6 or (abs(score - best[0]) <= 1e-6 and h1 >= h2):
                best = (score, k)
    if best is None:
        return None
    k = best[1]
    return lines[:k], lines[k:], height(lines[:k]), height(lines[k:])


def flow(paras, col_w, cap):
    """Break every paragraph and split into columns. Returns None if it does not fit `cap`."""
    lines = []
    for pi, p in enumerate(paras):
        space = space_width(p.size)
        ls = break_paragraph(p, col_w, space)
        if ls is None:
            return None
        for ln in ls:
            ln.para = pi
            if ln.first:
                ln.gap_before = p.gap_before if pi else 0.0
        lines.extend(ls)
    return split_columns(lines, cap)


def fit(build, col_w, cap, lo=0.55, hi=3.0, iters=22):
    """Largest size scale s for which build(s) fits two columns of height `cap(s)`.
    `build(s)` returns the paragraphs; `cap(s)` the baseline-to-baseline height available."""
    best = None
    for _ in range(iters):
        mid = (lo + hi) / 2
        res = flow(build(mid), col_w, cap(mid))
        if res is not None:
            best, lo = (mid, res), mid
        else:
            hi = mid
    if best is None:
        raise RuntimeError("text does not fit even at the smallest size")
    return best


def balanced_lines(words_text, size, style, max_w, n):
    """Split a short text into n visually balanced lines no wider than max_w (greedy search)."""
    toks = words_text.split()
    if n == 1 or len(toks) < 2:
        return [words_text]
    best = None
    import itertools
    for cuts in itertools.combinations(range(1, len(toks)), n - 1):
        parts, prev = [], 0
        for c in list(cuts) + [len(toks)]:
            parts.append(" ".join(toks[prev:c]))
            prev = c
        widths = [text_width(p, size, style) for p in parts]
        score = max(widths) - min(widths)
        if max(widths) <= max_w and (best is None or score < best[0]):
            best = (score, parts)
    return best[1] if best else [words_text]

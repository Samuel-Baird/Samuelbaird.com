"""Caption grouping and ASS/SRT generation for Saint Capybara.

    from capy.captions import group_phrases, build_ass, build_srt

`group_phrases` chunks a list of word-timing dicts ({w, s, e}) into
on-screen phrase groups per docs/saint-capybara/script-format.md's caption
rules (max_chars_per_line, max_words_per_phrase, a gap in speech forces a
break). `build_ass` renders those groups into an ASS subtitle file using
the styles/colors defined in theme.yaml (Capy/Source/Hook), with a
persistent-keyword highlight color. `build_srt` renders a plain SRT
(fallback / accessibility copy, not used for the burned-in captions
themselves, which go through libass via ffmpeg's `subtitles=` filter).
"""
from __future__ import annotations

from dataclasses import dataclass

from capy.layout import Theme


@dataclass
class WordTiming:
    w: str
    s: float
    e: float


@dataclass
class Phrase:
    text: str
    start: float
    end: float
    words: list[WordTiming]
    style: str = "Capy"
    highlight: list[str] | None = None


def group_phrases(
    words: list[dict],
    *,
    max_chars: int = 34,
    max_words: int = 6,
    gap_break: float = 0.35,
    style: str = "Capy",
    highlight: list[str] | None = None,
) -> list[Phrase]:
    """Chunk `words` ([{w,s,e}, ...]) into caption phrase groups.

    A new group starts when: adding the next word would exceed
    max_chars or max_words, or the gap since the previous word's end
    exceeds gap_break (a natural pause in speech).
    """
    groups: list[Phrase] = []
    cur: list[WordTiming] = []

    def flush():
        if not cur:
            return
        text = " ".join(w.w for w in cur)
        groups.append(Phrase(text=text, start=cur[0].s, end=cur[-1].e, words=list(cur), style=style, highlight=highlight))

    for raw in words:
        wt = WordTiming(w=raw["w"], s=raw["s"], e=raw["e"])
        if cur:
            gap = wt.s - cur[-1].e
            trial_text = " ".join([w.w for w in cur] + [wt.w])
            too_long = len(trial_text) > max_chars * 2  # two lines allowed
            too_many = len(cur) + 1 > max_words
            if gap > gap_break or too_long or too_many:
                flush()
                cur = []
        cur.append(wt)
    flush()
    return groups


def _wrap_two_lines(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    words = text.split()
    line1, line2 = [], []
    for w in words:
        if len(" ".join(line1 + [w])) <= max_chars or not line2 and not line1:
            line1.append(w)
        else:
            line2.append(w)
    if not line2:
        # split roughly in half by word count
        mid = max(1, len(words) // 2)
        line1, line2 = words[:mid], words[mid:]
    return "\\N".join([" ".join(line1), " ".join(line2)])


def _ass_time(t: float) -> str:
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h:d}:{m:02d}:{s:05.2f}"


def _ass_color(rgb: tuple[int, int, int]) -> str:
    r, g, b = rgb
    return f"&H00{b:02X}{g:02X}{r:02X}"


def build_ass(phrases: list[Phrase], theme: Theme, *, offset: dict[int, float] | None = None) -> str:
    """Render an ASS subtitle document. `offset` (unused placeholder for
    per-beat time offsets when concatenating segments in capy_render.py)."""
    w, h = theme.canvas_size
    styles = {
        "Capy": theme.caption_style("style_capy"),
        "Source": theme.caption_style("style_source"),
        "Hook": theme.caption_style("style_hook"),
    }
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {w}
PlayResY: {h}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
"""
    style_lines = []
    for name, s in styles.items():
        primary = _ass_color(theme.color(s["primary"]))
        outline = _ass_color(theme.color(s["outline"]))
        italic = -1 if s.get("italic") else 0
        style_lines.append(
            f"Style: {name},{theme.font_name('body' if s['font'] == 'body' else 'display')},{s['size']},"
            f"{primary},&H000000FF,{outline},&H00000000,0,{italic},0,0,100,100,0,0,1,{s['outline_px']},{s.get('shadow',0)},{s['alignment']},20,20,20,1"
        )

    events_header = """
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    max_chars = theme.data["captions"]["max_chars_per_line"]
    highlight_hex = _ass_color(theme.color(theme.data["captions"]["highlight_color"]))
    cap = theme.zone("captions")
    pos_y = (cap["y0"] + cap["y1"]) // 2
    canvas_w, _ = theme.canvas_size
    pos_x = canvas_w // 2

    for p in phrases:
        text = _wrap_two_lines(p.text, max_chars)
        if p.highlight:
            for hw in p.highlight:
                text = text.replace(hw, f"{{\\c{highlight_hex}}}{hw}{{\\r}}")
        line = f"Dialogue: 0,{_ass_time(p.start)},{_ass_time(p.end)},{p.style},,0,0,0,,{{\\an5\\pos({pos_x},{pos_y})}}{text}"
        events.append(line)

    return header + "\n".join(style_lines) + "\n" + events_header + "\n".join(events) + "\n"


def build_srt(phrases: list[Phrase]) -> str:
    def srt_time(t: float) -> str:
        h = int(t // 3600)
        m = int((t % 3600) // 60)
        s = t % 60
        ms = int(round((s - int(s)) * 1000))
        return f"{h:02d}:{m:02d}:{int(s):02d},{ms:03d}"

    lines = []
    for i, p in enumerate(phrases, start=1):
        lines.append(str(i))
        lines.append(f"{srt_time(p.start)} --> {srt_time(p.end)}")
        lines.append(p.text)
        lines.append("")
    return "\n".join(lines)

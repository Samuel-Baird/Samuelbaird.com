"""Caption grouping for Saint Capybara.

    from capy.captions import group_phrases, attach_punctuation, build_srt

`attach_punctuation` merges Kokoro/Whisper's standalone punctuation
tokens onto the adjacent word (fixes the shipped `publicly , repeatedly`
and `, a claim` captions, and the outro-01 caption card whose entire text
was a lone `,`). `group_phrases` chunks a list of word-timing dicts
({w, s, e}) into on-screen phrase groups per
docs/saint-capybara/script-format.md's caption rules (a measured-width
budget when a font measurer is supplied, else the max_chars_per_line
pre-estimate; max_words_per_phrase; a gap in speech forces a break).
`build_srt` renders a plain SRT (fallback / accessibility copy -- not
used for the burned-in captions themselves).

The old ASS/libass path (`build_ass`, `_wrap_two_lines`) is retired along
with the ffmpeg+libass burn-in it served (see
docs/saint-capybara/hybrid-resolve-pipeline.md) -- captions are PIL
stills now, laid out by tools/capy/text.py.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable

_PUNCT_ONLY = re.compile(r"^[,.;:!?…\"'’”)\]]+$")
_LEADING_HYPHEN_OR_PUNCT = re.compile(r"^[-\"'‘“)\]]")
_TRAILING_HYPHEN = re.compile(r"-$")


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


def attach_punctuation(words: list[dict]) -> list[dict]:
    """Merge a standalone-punctuation token (or one starting with a
    leading quote/hyphen) onto the previous word; a token ending in `-`
    merges onto the next word (Whisper's `30 -plus` -> `30-plus`).
    Non-destructive: returns a new list; input dicts are not mutated."""
    out: list[dict] = []
    pending_prefix = ""
    for raw in words:
        w = dict(raw)
        text = w.get("w", "")
        stripped = text.strip()
        if not stripped:
            continue
        if out and (_PUNCT_ONLY.match(stripped) or (_LEADING_HYPHEN_OR_PUNCT.match(stripped) and len(stripped) > 1)):
            out[-1]["w"] = out[-1]["w"] + stripped
            out[-1]["e"] = w.get("e", out[-1]["e"])
            continue
        if pending_prefix:
            text = pending_prefix + text
            pending_prefix = ""
        if _TRAILING_HYPHEN.search(stripped) and len(stripped) > 1:
            pending_prefix = stripped
            continue
        w["w"] = text
        out.append(w)
    if pending_prefix and out:
        out[-1]["w"] = out[-1]["w"] + pending_prefix
    return out


def group_phrases(
    words: list[dict],
    *,
    max_chars: int = 24,
    max_words: int = 6,
    gap_break: float = 0.35,
    style: str = "Capy",
    highlight: list[str] | None = None,
    measure: Callable[[str], float] | None = None,
    max_width: int | None = None,
) -> list[Phrase]:
    """Chunk `words` ([{w,s,e}, ...]) into caption phrase groups.

    A new group starts when: adding the next word would exceed the width
    budget (measured via `measure`+`max_width` when supplied, else
    `max_chars`) or `max_words`, or the gap since the previous word's end
    exceeds `gap_break` (a natural pause in speech).

    `measure`/`max_width` let the caller (capy_caption_cards.py) pass the
    actual font's `getlength`, so grouping and the eventual fit_text()
    wrap agree about what fits -- group_phrases only needs to avoid
    grouping so much text that fit_text would have to shrink below its
    floor, not do the wrapping itself.
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
            if measure is not None and max_width is not None:
                too_long = measure(trial_text) > 1.9 * max_width  # ~two lines minus wrap slack
            else:
                too_long = len(trial_text) > max_chars * 2
            too_many = len(cur) + 1 > max_words
            if gap > gap_break or too_long or too_many:
                flush()
                cur = []
        cur.append(wt)
    flush()
    return groups


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

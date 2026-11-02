"""Markdown-aware segmentation, placeholder protection and scripture-citation localization.

A document is split into blocks. `raw` blocks (frontmatter, code fences, blank lines,
rules, table rows) are emitted unchanged. `seg` blocks carry a `prefix` (heading hashes, list
bullet, footnote label) that is preserved while only the remaining text is translated.
Round-trip: join(blocks) with unchanged seg text reproduces the input exactly.
"""
import json
import re
from dataclasses import dataclass, field

from . import config

PH = "⟦{}⟧"                      # ⟦n⟧
PH_RE = re.compile(r"⟦(\d+)⟧")

_PROTECT = [
    re.compile(r"\[\^[^\]\s]+\]"),                 # footnote reference [^3]
    re.compile(r"(?<=\]\()[^)\s]+(?=\))"),         # markdown link target
    re.compile(r"https?://[^\s)\]>]+"),            # bare URL
    re.compile(r"`[^`\n]+`"),                      # inline code
    re.compile(r"</?[A-Za-z][^>\n]*>"),            # html tag
]
_LINE_PREFIX = re.compile(r"^(\s{0,3}(?:#{1,6}\s+|>\s?|[-*+]\s+|\d+[.)]\s+)|\[\^[^\]\s]+\]:\s*)")


@dataclass
class Block:
    raw: str = ""            # for raw blocks: the exact text; for seg blocks: unused
    prefix: str = ""
    text: str = ""
    is_seg: bool = False
    target: str = ""
    meta: dict = field(default_factory=dict)


def split_document(text: str):
    lines = text.split("\n")
    blocks = []
    i = 0
    if lines and lines[0].strip() == "---":
        j = next((k for k in range(1, len(lines)) if lines[k].strip() == "---"), None)
        if j is not None:
            blocks.append(Block(raw="\n".join(lines[: j + 1])))
            i = j + 1
    fence = None
    for line in lines[i:]:
        s = line.strip()
        if fence:
            blocks.append(Block(raw=line))
            if s.startswith(fence):
                fence = None
        elif s.startswith("```") or s.startswith("~~~"):
            fence = s[:3]
            blocks.append(Block(raw=line))
        elif not s or s.startswith("|") or re.fullmatch(r"[-*_]{3,}", s) or re.fullmatch(r"[|:\-\s]+", s):
            blocks.append(Block(raw=line))
        else:
            m = _LINE_PREFIX.match(line)
            prefix = m.group(0) if m else ""
            blocks.append(Block(prefix=prefix, text=line[len(prefix):], is_seg=True))
    return blocks


def join_blocks(blocks, use_target=True):
    out = []
    for b in blocks:
        if b.is_seg:
            out.append(b.prefix + (b.target if use_target and b.target else b.text))
        else:
            out.append(b.raw)
    return "\n".join(out)


class Books:
    """English scripture book names -> Church-localized names; builds the citation regex."""
    _cache = {}

    def __init__(self):
        self.map = json.loads(config.BOOKS_FILE.read_text(encoding="utf-8")) if config.BOOKS_FILE.exists() else {}
        names = sorted(self.map, key=len, reverse=True)
        alt = "|".join(re.escape(n) for n in names)
        self.rx = re.compile(
            r"(?<![\w])(" + alt + r")\s+(\d+)((?::\d+(?:[–—\-,]\s?\d+)*)?)(?![\w])") if names else None

    @classmethod
    def get(cls):
        if "b" not in cls._cache:
            cls._cache["b"] = cls()
        return cls._cache["b"]

    def localize(self, lang, m):
        book = self.map.get(m.group(1), {}).get(lang)
        return f"{book} {m.group(2)}{m.group(3)}" if book else m.group(0)


def protect(text: str, lang: str):
    """Mask footnotes/URLs/code/tags and scripture citations. Returns (masked, {n: restore_text})."""
    ph, n = {}, [0]

    def put(val):
        n[0] += 1
        ph[n[0]] = val
        return PH.format(n[0])

    books = Books.get()
    if books.rx:
        text = books.rx.sub(lambda m: put(books.localize(lang, m)), text)
    for rx in _PROTECT:
        text = rx.sub(lambda m: put(m.group(0)), text)
    return text, ph


def restore(text: str, ph: dict):
    return PH_RE.sub(lambda m: ph.get(int(m.group(1)), m.group(0)), text)


def placeholders_ok(target: str, ph: dict) -> bool:
    found = sorted(int(x) for x in PH_RE.findall(target))
    return found == sorted(ph)


def numbers(text: str):
    return sorted(re.findall(r"\d+", PH_RE.sub("", text)))

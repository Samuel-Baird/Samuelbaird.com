"""Source model for a Saint Capybara project: video or article.

A project's source is `kind: video | article` (see the plan's Part 4 and
docs/saint-capybara/research-protocol.md). For a video the existing
`source/source.mp4` + `source/source_info.json` pair is unchanged; for an
article the "media" is `source/source.md` -- the cleaned article text, one
numbered paragraph per block -- plus a richer `source_info.json` that pins
the text (sha256), the url, and the archive receipt.

    from capy.source import load_source_info, load_article, find_excerpt

    info = load_source_info(project)          # kind defaults to "video"
    article = load_article(project)           # requires source/source.md
    match = find_excerpt(article, beat["text"], beat["para"])
    if not match.ok: print(match.message)

`normalize()` lives here (moved out of capy_check_sources.py) so the card
quote check and the excerpt check use the exact same folding rules:
whitespace collapse, curly -> straight quotes, dash/ellipsis folding,
lower-case. Nothing else is stripped -- a one-word change must still fail.

Paragraph markers (`¶`) appear ONLY in source.md and in rendered
markdown/console output; beats.yaml carries `para:` as ints.
"""
from __future__ import annotations

import difflib
import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any

PARA_MARK = "¶"
ELLIPSIS_TOKEN = "[...]"

SOURCE_KINDS = {"video", "article"}

# ---------------------------------------------------------------------------
# Text folding
# ---------------------------------------------------------------------------

_QUOTE_MAP = {
    "‘": "'", "’": "'", "‚": "'", "‛": "'",
    "“": '"', "”": '"', "„": '"', "‟": '"',
    "′": "'", "″": '"',
    "–": "-", "—": "-", "―": "-", "−": "-",
    " ": " ", " ": " ", " ": " ",
    "…": "...",
}
_QUOTE_RE = re.compile("|".join(re.escape(k) for k in _QUOTE_MAP))


def fold_punctuation(text: str) -> str:
    """Curly quotes -> straight, en/em dashes -> hyphen, ellipsis char ->
    three dots, NBSP -> space. Case and everything else preserved."""
    return _QUOTE_RE.sub(lambda m: _QUOTE_MAP[m.group(0)], text or "")


def normalize(text: str) -> str:
    """Whitespace-collapsed, punctuation-folded, lower-cased text for
    substring comparison. Used for card quotes AND excerpts."""
    folded = fold_punctuation(text or "")
    folded = folded.replace("--", "-")
    return re.sub(r"\s+", " ", folded).strip().lower()


def sha256_text(text: str) -> str:
    """sha256 of `text` with line endings normalised to LF, UTF-8."""
    canon = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


def word_count(text: str | None) -> int:
    if not text:
        return 0
    return len([w for w in text.split() if w != ELLIPSIS_TOKEN])


# ---------------------------------------------------------------------------
# source_info.json
# ---------------------------------------------------------------------------

@dataclass
class SourceInfo:
    kind: str = "video"
    title: str | None = None
    # video fields (unchanged from capy_ingest.py's original shape)
    uploader: str | None = None
    upload_date: str | None = None
    canonical_url: str | None = None
    source_duration_seconds: float | None = None
    media_from: str | None = None
    # article fields
    byline: str | None = None
    publication: str | None = None
    publish_date: str | None = None
    url: str | None = None
    archive_url: str | None = None
    archive_captured_at: str | None = None
    accessed: str | None = None
    paywalled: bool = False
    text_from: str | None = None
    paragraph_count: int | None = None
    text_sha256: str | None = None
    present: bool = False          # False when source_info.json was missing
    raw: dict = field(default_factory=dict)

    @property
    def is_article(self) -> bool:
        return self.kind == "article"

    def to_json_dict(self) -> dict:
        """Serialisable dict in the on-disk key order (article shape)."""
        return {
            "kind": self.kind,
            "title": self.title,
            "byline": self.byline,
            "publication": self.publication,
            "publish_date": self.publish_date,
            "url": self.url,
            "canonical_url": self.canonical_url,
            "archive_url": self.archive_url,
            "archive_captured_at": self.archive_captured_at,
            "accessed": self.accessed,
            "paywalled": bool(self.paywalled),
            "text_from": self.text_from,
            "paragraph_count": self.paragraph_count,
            "text_sha256": self.text_sha256,
        }


def source_info_path(project: Path | str) -> Path:
    return Path(project) / "source" / "source_info.json"


def source_md_path(project: Path | str) -> Path:
    return Path(project) / "source" / "source.md"


def load_source_info(project: Path | str) -> SourceInfo:
    """Read source/source_info.json. A missing file, or one without `kind`,
    is a video source (the three pre-article projects never wrote `kind`)."""
    path = source_info_path(project)
    if not path.exists():
        return SourceInfo(kind="video", present=False)
    raw = json.loads(path.read_text(encoding="utf-8")) or {}
    kind = raw.get("kind") or "video"
    info = SourceInfo(
        kind=kind,
        title=raw.get("title"),
        uploader=raw.get("uploader"),
        upload_date=raw.get("upload_date"),
        canonical_url=raw.get("canonical_url"),
        source_duration_seconds=raw.get("source_duration_seconds"),
        media_from=raw.get("media_from"),
        byline=raw.get("byline"),
        publication=raw.get("publication"),
        publish_date=raw.get("publish_date"),
        url=raw.get("url") or (raw.get("canonical_url") if kind == "article" else None),
        archive_url=raw.get("archive_url"),
        archive_captured_at=raw.get("archive_captured_at"),
        accessed=raw.get("accessed"),
        paywalled=bool(raw.get("paywalled", False)),
        text_from=raw.get("text_from"),
        paragraph_count=raw.get("paragraph_count"),
        text_sha256=raw.get("text_sha256"),
        present=True,
        raw=raw,
    )
    return info


# ---------------------------------------------------------------------------
# source.md
# ---------------------------------------------------------------------------

@dataclass
class Article:
    paragraphs: dict[int, str]           # 1-based paragraph number -> text
    header_lines: list[str] = field(default_factory=list)
    path: Path | None = None

    @property
    def count(self) -> int:
        return len(self.paragraphs)

    @property
    def body_text(self) -> str:
        """The hashed form: paragraph texts in order, blank-line separated,
        WITHOUT the paragraph markers (so renumbering never changes the
        hash, but any wording edit does)."""
        return "\n\n".join(self.paragraphs[n] for n in sorted(self.paragraphs))

    @property
    def sha256(self) -> str:
        return sha256_text(self.body_text)

    @property
    def word_count(self) -> int:
        return sum(len(p.split()) for p in self.paragraphs.values())

    def span_text(self, para: int | list[int] | tuple[int, ...]) -> str:
        nums = para_span(para)
        missing = [n for n in nums if n not in self.paragraphs]
        if missing:
            raise KeyError(f"paragraph(s) not in source.md: {missing}")
        return " ".join(self.paragraphs[n] for n in nums)


_PARA_LINE_RE = re.compile(rf"^{PARA_MARK}(\d+)\s+(.*)$")
_HEADING_RE = re.compile(r"^\s*#{1,6}\s+")
_SKIP_LINE_RE = re.compile(r"^\s*(---+|\*\*\*+|___+|!\[[^\]]*\]\([^)]*\))\s*$")


def para_span(para: int | list[int] | tuple[int, ...]) -> list[int]:
    """Normalise a beat's `para:` (int or [a, b]) into an ordered list."""
    if isinstance(para, bool):
        raise TypeError("para must be an int or a list of ints")
    if isinstance(para, int):
        return [para]
    if isinstance(para, (list, tuple)) and para and all(isinstance(p, int) and not isinstance(p, bool) for p in para):
        return sorted(set(int(p) for p in para))
    raise TypeError("para must be an int or a list of ints")


def para_label(para: int | list[int] | tuple[int, ...]) -> str:
    """`¶12` or `¶4–¶5` for markdown/console output."""
    nums = para_span(para)
    if len(nums) == 1:
        return f"{PARA_MARK}{nums[0]}"
    return f"{PARA_MARK}{nums[0]}–{PARA_MARK}{nums[-1]}"


def number_paragraphs(raw_text: str) -> list[str]:
    """Split cleaned article text into paragraphs: blank-line separated
    blocks, single newlines inside a block joined by a space, markdown
    heading markers stripped (a subhead is its own paragraph), horizontal
    rules and image lines dropped, internal whitespace collapsed.
    Existing `¶n` markers are stripped so a source.md can be re-ingested."""
    text = (raw_text or "").replace("\r\n", "\n").replace("\r", "\n")
    blocks = re.split(r"\n\s*\n", text)
    out: list[str] = []
    for block in blocks:
        lines = []
        for line in block.split("\n"):
            if _SKIP_LINE_RE.match(line):
                continue
            line = _HEADING_RE.sub("", line)
            line = re.sub(rf"^\s*{PARA_MARK}\d+\s+", "", line)
            line = line.strip()
            if line:
                lines.append(line)
        para = re.sub(r"\s+", " ", " ".join(lines)).strip()
        if para:
            out.append(para)
    return out


def parse_article(text: str, *, path: Path | None = None) -> Article:
    """Parse source.md text: header lines until the first `¶n ` line, then
    one paragraph per `¶n text` block (blank-line separated; a paragraph
    may wrap onto continuation lines until the next blank line)."""
    lines = text.replace("\r\n", "\n").split("\n")
    header: list[str] = []
    paragraphs: dict[int, str] = {}
    current_no: int | None = None
    current: list[str] = []

    def flush():
        nonlocal current_no, current
        if current_no is not None:
            body = re.sub(r"\s+", " ", " ".join(current)).strip()
            if current_no in paragraphs:
                raise ValueError(f"duplicate paragraph number {PARA_MARK}{current_no} in {path or 'source.md'}")
            paragraphs[current_no] = body
        current_no, current = None, []

    for line in lines:
        m = _PARA_LINE_RE.match(line)
        if m:
            flush()
            current_no = int(m.group(1))
            current = [m.group(2)]
        elif current_no is not None:
            if line.strip():
                current.append(line.strip())
            else:
                flush()
        elif line.strip():
            header.append(line.rstrip())
    flush()

    if paragraphs:
        expected = list(range(1, len(paragraphs) + 1))
        if sorted(paragraphs) != expected:
            raise ValueError(
                f"{path or 'source.md'}: paragraph numbers must run {PARA_MARK}1..{PARA_MARK}{len(paragraphs)} "
                f"without gaps (got {sorted(paragraphs)[:5]}...)"
            )
    return Article(paragraphs=paragraphs, header_lines=header, path=path)


def load_article(project: Path | str) -> Article:
    path = source_md_path(project)
    if not path.exists():
        raise FileNotFoundError(f"{path} not found (article projects need source/source.md; run capy_ingest.py --article-file)")
    return parse_article(path.read_text(encoding="utf-8"), path=path)


def source_md_text(info: SourceInfo, paragraphs: list[str]) -> str:
    """Render source.md: header (headline; publication · byline · date;
    url; archived url) then `¶n text` blocks, blank-line separated."""
    head = [f"# {info.title or '(untitled)'}"]
    meta = " · ".join(p for p in (info.publication, info.byline, info.publish_date) if p)
    if meta:
        head.append(meta)
    head.append(f"Source: {info.url or info.canonical_url or '(no url)'}")
    head.append(f"Archived: {info.archive_url or '(none)'}")
    body = [f"{PARA_MARK}{i} {p}" for i, p in enumerate(paragraphs, start=1)]
    return "\n".join(head) + "\n\n" + "\n\n".join(body) + "\n"


def write_source_md(project: Path | str, info: SourceInfo, paragraphs: list[str]) -> Path:
    path = source_md_path(project)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source_md_text(info, paragraphs), encoding="utf-8", newline="\n")
    return path


# ---------------------------------------------------------------------------
# Excerpt matching
# ---------------------------------------------------------------------------

def excerpt_fragments(text: str) -> list[str]:
    """The `[...]`-separated pieces of an excerpt, stripped, empties dropped."""
    return [f.strip() for f in (text or "").split(ELLIPSIS_TOKEN) if f.strip()]


def strip_outer_quotes(text: str) -> str:
    t = (text or "").strip()
    pairs = [('"', '"'), ("“", "”"), ("'", "'"), ("‘", "’")]
    for open_q, close_q in pairs:
        if len(t) >= 2 and t.startswith(open_q) and t.endswith(close_q):
            return t[1:-1].strip()
    return t


@dataclass
class ExcerptMatch:
    ok: bool
    para: list[int]
    fragments: list[str]
    failed_fragment: str | None = None
    failed_index: int | None = None
    hint: str | None = None
    message: str = ""


def _nearest_paragraph(article: Article, fragment: str) -> tuple[int | None, float, str]:
    """Best windowed match of `fragment` across all paragraphs -> (para no,
    ratio, matched window text). Windowed so a long paragraph doesn't
    drown a short fragment's similarity."""
    frag_words = normalize(fragment).split()
    if not frag_words or not article.paragraphs:
        return None, 0.0, ""
    n = len(frag_words)
    best: tuple[int | None, float, str] = (None, 0.0, "")
    frag_norm = " ".join(frag_words)
    for no, para in article.paragraphs.items():
        words = para.split()
        norm_words = normalize(para).split()
        if not norm_words:
            continue
        step = max(1, n // 4)
        for start in range(0, max(1, len(norm_words) - n + 1), step):
            window = " ".join(norm_words[start:start + n])
            ratio = difflib.SequenceMatcher(None, frag_norm, window).ratio()
            if ratio > best[1]:
                best = (no, ratio, " ".join(words[start:start + n]))
        if best[1] >= 0.999:
            break
    return best


def find_excerpt(article: Article, text: str, para: int | list[int] | tuple[int, ...]) -> ExcerptMatch:
    """Verify an excerpt beat's `text` against the anchored paragraph(s):
    each `[...]`-separated fragment must be a normalised, in-order
    substring of the joined span. Curly/straight quotes and dash variants
    are folded (see normalize); any word change fails, with a difflib
    nearest-paragraph hint."""
    try:
        nums = para_span(para)
    except TypeError as e:
        return ExcerptMatch(False, [], [], message=str(e))
    missing = [n for n in nums if n not in article.paragraphs]
    if missing:
        return ExcerptMatch(False, nums, [], message=f"paragraph(s) {', '.join(PARA_MARK + str(n) for n in missing)} not in source.md (it has {PARA_MARK}1..{PARA_MARK}{article.count})")

    fragments = excerpt_fragments(strip_outer_quotes(text))
    if not fragments:
        return ExcerptMatch(False, nums, [], message="excerpt text is empty")

    haystack = normalize(article.span_text(nums))
    cursor = 0
    for i, frag in enumerate(fragments):
        needle = normalize(frag)
        pos = haystack.find(needle, cursor)
        if pos < 0:
            near_no, ratio, window = _nearest_paragraph(article, frag)
            if haystack.find(needle) >= 0:
                hint = f"fragment #{i + 1} does occur in {para_label(nums)} but out of order (fragments must appear in the source's order)"
            elif near_no is not None and ratio >= 0.6:
                hint = f"nearest match {PARA_MARK}{near_no} ({ratio:.0%}): “{window}”"
            else:
                hint = "no similar passage found in source.md"
            return ExcerptMatch(
                False, nums, fragments, failed_fragment=frag, failed_index=i, hint=hint,
                message=f"excerpt fragment #{i + 1} is not verbatim in {para_label(nums)}: “{frag}” -- {hint}",
            )
        cursor = pos + len(needle)
    return ExcerptMatch(True, nums, fragments, message="ok")


# ---------------------------------------------------------------------------
# Attribution / rendering helpers
# ---------------------------------------------------------------------------

_MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def format_date(value: str | None) -> str | None:
    """`2026-08-30` -> `Aug 30, 2026`; `2026-08` -> `Aug 2026`; `2026` and
    anything unparsable are returned as-is."""
    if not value:
        return None
    v = str(value).strip()
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", v)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 1 <= mo <= 12:
            return f"{_MONTHS[mo - 1]} {d}, {y}"
    m = re.match(r"^(\d{4})-(\d{2})$", v)
    if m and 1 <= int(m.group(2)) <= 12:
        return f"{_MONTHS[int(m.group(2)) - 1]} {m.group(1)}"
    m = re.match(r"^(\d{4})(\d{2})(\d{2})$", v)  # yt_dlp style 20240604
    if m and 1 <= int(m.group(2)) <= 12:
        return f"{_MONTHS[int(m.group(2)) - 1]} {int(m.group(3))}, {m.group(1)}"
    return v


def attribution_line(info: SourceInfo, *, cite_byline: bool = False) -> str:
    """`The Salt Lake Tribune · "Headline" · Aug 30, 2026` -- the
    publication is the institutional voice; the byline is opt-in
    (brand.md sec 2: don't put the reporter's name on every card)."""
    parts: list[str] = []
    who = info.publication or info.uploader
    if cite_byline and info.byline:
        who = f"{info.byline}, {who}" if who else info.byline
    if who:
        parts.append(who)
    if info.title:
        parts.append(f"“{info.title}”")
    d = format_date(info.publish_date or info.upload_date)
    if d:
        parts.append(d)
    return " · ".join(parts)


def excerpt_script_line(beat: dict, info: SourceInfo, *, voice: str | None = None) -> str:
    """The script.md line for an excerpt beat:
    `- **Excerpt (¶12):** “…” — attribution · voice: quote_female`."""
    text = strip_outer_quotes(beat.get("text", ""))
    try:
        label = para_label(beat.get("para"))
    except TypeError:
        label = f"{PARA_MARK}?"
    voice_label = voice
    if voice_label is None:
        v = beat.get("voice")
        if isinstance(v, dict):
            engine = v.get("engine", "kokoro")
            ident = v.get("name") if engine == "kokoro" else Path(v.get("ref", "?")).name
            voice_label = f"inline {ident} ({engine})"
        elif isinstance(v, str):
            voice_label = v
        else:
            voice_label = "quote_default"
    attribution = attribution_line(info, cite_byline=bool(beat.get("cite_byline")))
    return f"- **Excerpt ({label}):** “{text}” — {attribution} · voice: {voice_label}"


def source_header_lines(info: SourceInfo) -> list[str]:
    """Header lines for script.md describing the source."""
    if info.kind == "article":
        who = " · ".join(p for p in (info.publication, info.byline, format_date(info.publish_date)) if p)
        line = f"**Source:** article — “{info.title or '(untitled)'}”"
        if who:
            line += f" ({who})"
        lines = [line]
        if info.url:
            lines.append(f"**URL:** {info.url}")
        lines.append(f"**Archived:** {info.archive_url or '(no archive url)'}")
        if info.paragraph_count:
            lines.append(f"**Text:** {info.paragraph_count} paragraphs, sha256 {(info.text_sha256 or '')[:12]}…")
        return lines
    title = info.title or "(untitled)"
    who = f" ({info.uploader})" if info.uploader else ""
    lines = [f"**Source:** video — “{title}”{who}"]
    if info.canonical_url:
        lines.append(f"**URL:** {info.canonical_url}")
    return lines


def today_iso() -> str:
    return date.today().isoformat()


def wayback_timestamp_to_iso(ts: str) -> str | None:
    try:
        return datetime.strptime(ts[:14], "%Y%m%d%H%M%S").isoformat() + "Z"
    except (ValueError, TypeError):
        return None

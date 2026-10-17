#!/usr/bin/env python3
"""Clips type (docs/types/clips.md): validate script/clips.yaml against the
long-form source's Whisper transcript and render the review document; after
the user's written approval, write the per-clip Resolve build plan.

    python tools/clips_plan.py --project D:\\Videos\\<slug>
    python tools/clips_plan.py --project D:\\Videos\\<slug> --build-plan \\
        --fps 29.97 --source-size 1920x1080

Default (review) mode writes:
    script/clips.md   -- numbered proposed clips + the full source transcript
                         at the bottom, with each clip's start/end marked in it

--build-plan (only after clips.yaml `approval:` records the user's written
approval) also writes:
    script/clips.build.json  -- per approved clip: timeline name, export path,
                                source frame ranges (cuts removed, split at
                                reframe switches), record frames, and the
                                horizontal Pan for each piece
    captions/<id>.srt        -- per approved clip, times rebased to the clip's
                                own timeline (only when `captions: burned`)

Transcript: transcripts/source.json (tools/transcribe.py output, written with
word timestamps). Override with --transcript.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

FORMATS = {
    "vertical": (1080, 1920),
    "landscape": (1920, 1080),
    "square": (1080, 1080),
}
CAPTIONS = ("burned", "none")
REFRAME_NAMES = {"center": 0.5, "left": 0.25, "right": 0.75}
DEFAULT_MIN_SECONDS = 15.0
DEFAULT_MAX_SECONDS = 90.0
# Hard ceiling for the vertical platforms (Shorts / Reels / TikTok feed).
VERTICAL_HARD_MAX_SECONDS = 180.0
# A clip boundary this close to a word edge counts as on the edge.
EDGE_TOLERANCE = 0.05
CAPTION_MAX_WORDS = 6
CAPTION_MAX_CHARS = 32
SENTENCE_END = re.compile(r"[.!?…][\"'”’)]*$")


@dataclass
class Issue:
    level: str  # "error" | "warn"
    where: str
    message: str

    def __str__(self) -> str:
        return f"{self.level.upper():5} {self.where}: {self.message}"


@dataclass
class Clip:
    number: int
    id: str
    title: str
    start: float
    end: float
    cuts: list[tuple[float, float]] = field(default_factory=list)
    reframe: list[tuple[float, float]] = field(default_factory=list)  # (at, x)
    raw: dict = field(default_factory=dict)

    @property
    def kept(self) -> list[tuple[float, float]]:
        """The source spans that survive this clip's internal cuts, in order."""
        spans, cursor = [], self.start
        for cs, ce in sorted(self.cuts):
            if cs > cursor:
                spans.append((cursor, cs))
            cursor = max(cursor, ce)
        if cursor < self.end:
            spans.append((cursor, self.end))
        return spans

    @property
    def duration(self) -> float:
        return sum(e - s for s, e in self.kept)

    def in_cut(self, t: float) -> bool:
        return any(cs <= t < ce for cs, ce in self.cuts)

    def to_clip_time(self, t: float) -> float:
        """Source time -> seconds from the start of this clip's own timeline."""
        out = 0.0
        for s, e in self.kept:
            if t >= e:
                out += e - s
            else:
                return out + max(0.0, t - s)
        return out


# ---- time parsing / formatting ---------------------------------------------

def parse_time(value) -> float:
    """Seconds from a number or "ss.s" / "mm:ss.s" / "h:mm:ss.s"."""
    if isinstance(value, (int, float)):
        return float(value)
    parts = str(value).strip().split(":")
    if not 1 <= len(parts) <= 3:
        raise ValueError(f"bad time {value!r}")
    seconds = 0.0
    for p in parts:
        seconds = seconds * 60 + float(p)
    return seconds


def fmt_time(t: float, hours: bool = False) -> str:
    h, rem = divmod(max(0.0, t), 3600)
    m, s = divmod(rem, 60)
    if hours or h:
        return f"{int(h)}:{int(m):02d}:{s:05.2f}"
    return f"{int(m):02d}:{s:05.2f}"


def fmt_srt(t: float) -> str:
    ms = int(round(max(0.0, t) * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


# ---- loading ----------------------------------------------------------------

def load_transcript(path: Path) -> tuple[list[dict], list[dict]]:
    """(segments, words) from a Whisper JSON written with word timestamps."""
    data = json.loads(path.read_text(encoding="utf-8"))
    segments = [s for s in data.get("segments", []) if s.get("text", "").strip()]
    words = []
    for seg in segments:
        for w in seg.get("words", []) or []:
            if w.get("word", "").strip():
                words.append({"word": w["word"].strip(), "start": float(w["start"]),
                              "end": float(w["end"])})
    return segments, words


def _reframe_x(value, where: str, issues: list[Issue]) -> float | None:
    if isinstance(value, str) and value in REFRAME_NAMES:
        return REFRAME_NAMES[value]
    if isinstance(value, (int, float)) and 0.0 <= float(value) <= 1.0:
        return float(value)
    issues.append(Issue("error", where,
                        f"reframe {value!r} must be center/left/right or a 0-1 crop centre"))
    return None


def parse_clips(doc: dict, issues: list[Issue]) -> list[Clip]:
    clips, seen = [], set()
    for n, raw in enumerate(doc.get("clips") or [], start=1):
        cid = str(raw.get("id") or f"c{n:02d}")
        where = f"clip {n:02d} ({cid})"
        if cid in seen:
            issues.append(Issue("error", where, "duplicate clip id"))
        seen.add(cid)
        try:
            start, end = parse_time(raw["start"]), parse_time(raw["end"])
        except (KeyError, ValueError) as e:
            issues.append(Issue("error", where, f"start/end missing or unreadable ({e})"))
            continue
        cuts = []
        for c in raw.get("cuts") or []:
            try:
                cuts.append((parse_time(c[0]), parse_time(c[1])))
            except (IndexError, TypeError, ValueError):
                issues.append(Issue("error", where, f"cut {c!r} must be [start, end]"))
        reframe = []
        rf = raw.get("reframe", "center")
        if isinstance(rf, list):
            for sw in rf:
                try:
                    at = parse_time(sw.get("at", start))
                except ValueError:
                    issues.append(Issue("error", where, f"reframe switch {sw!r}: bad `at`"))
                    continue
                x = _reframe_x(sw.get("x"), where, issues)
                if x is not None:
                    reframe.append((at, x))
            reframe.sort()
        else:
            x = _reframe_x(rf, where, issues)
            if x is not None:
                reframe.append((start, x))
        clips.append(Clip(n, cid, str(raw.get("title", "")).strip(), start, end,
                          cuts, reframe, raw))
    return clips


def load_plan(path: Path) -> dict:
    doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    doc.setdefault("format", "vertical")
    doc.setdefault("captions", "burned")
    doc.setdefault("min_seconds", DEFAULT_MIN_SECONDS)
    doc.setdefault("max_seconds", DEFAULT_MAX_SECONDS)
    return doc


# ---- validation -------------------------------------------------------------

def approved_numbers(doc: dict, clips: list[Clip], issues: list[Issue]) -> list[int]:
    """Clip numbers the user approved in writing; [] when nothing is approved yet."""
    appr = doc.get("approval") or {}
    sel = appr.get("clips")
    if sel in (None, [], ""):
        return []
    if not str(appr.get("words", "")).strip() or not str(appr.get("date", "")).strip():
        issues.append(Issue("error", "approval",
                            "record the date and the user's own written words, not just clip numbers"))
        return []
    numbers = {c.number for c in clips}
    if sel == "all":
        return sorted(numbers)
    out = []
    for v in sel if isinstance(sel, list) else [sel]:
        if v not in numbers:
            issues.append(Issue("error", "approval", f"approved clip {v!r} doesn't exist"))
        else:
            out.append(v)
    return sorted(set(out))


def validate(doc: dict, clips: list[Clip], words: list[dict],
             source_seconds: float | None) -> list[Issue]:
    issues: list[Issue] = []
    if doc["format"] not in FORMATS:
        issues.append(Issue("error", "format", f"must be one of {', '.join(FORMATS)}"))
    if doc["captions"] not in CAPTIONS:
        issues.append(Issue("error", "captions", f"must be one of {', '.join(CAPTIONS)}"))
    if not clips:
        issues.append(Issue("error", "clips", "no clips proposed"))
    lo, hi = float(doc["min_seconds"]), float(doc["max_seconds"])

    for c in clips:
        where = f"clip {c.number:02d} ({c.id})"
        if not c.title:
            issues.append(Issue("warn", where, "no title"))
        if c.end <= c.start:
            issues.append(Issue("error", where, "end is not after start"))
            continue
        if source_seconds is not None and c.end > source_seconds + 0.5:
            issues.append(Issue("error", where,
                                f"ends at {fmt_time(c.end)}, past the source's {fmt_time(source_seconds)}"))
        prev_end = c.start
        for cs, ce in sorted(c.cuts):
            if not (c.start < cs < ce < c.end):
                issues.append(Issue("error", where,
                                    f"cut {fmt_time(cs)}-{fmt_time(ce)} must sit strictly inside the clip"))
            elif cs < prev_end:
                issues.append(Issue("error", where, "cuts overlap"))
            prev_end = max(prev_end, ce)
        for at, _x in c.reframe:
            if not c.start <= at < c.end:
                issues.append(Issue("error", where, f"reframe switch at {fmt_time(at)} is outside the clip"))
        d = c.duration
        if d < lo:
            issues.append(Issue("warn", where, f"{d:.1f}s is under the {lo:.0f}s minimum"))
        if d > hi:
            issues.append(Issue("warn", where, f"{d:.1f}s is over the {hi:.0f}s target"))
        if doc["format"] != "landscape" and d > VERTICAL_HARD_MAX_SECONDS:
            issues.append(Issue("error", where,
                                f"{d:.1f}s exceeds the {VERTICAL_HARD_MAX_SECONDS:.0f}s vertical-platform ceiling"))

        # Boundaries must not split a word.
        for t, label in [(c.start, "start"), *[(t, "cut edge") for cut in c.cuts for t in cut],
                         (c.end, "end")]:
            for w in words:
                if w["start"] + EDGE_TOLERANCE < t < w["end"] - EDGE_TOLERANCE:
                    issues.append(Issue("warn", where,
                                        f"{label} {fmt_time(t)} splits the word {w['word']!r} "
                                        f"({fmt_time(w['start'])}-{fmt_time(w['end'])})"))
                    break
        inside = clip_words(c, words)
        if not inside:
            issues.append(Issue("error", where, "no transcript words inside this clip"))
        elif not SENTENCE_END.search(inside[-1]["word"]):
            issues.append(Issue("warn", where,
                                f"ends mid-sentence (last word {inside[-1]['word']!r}) -- "
                                "a clip should land on a finished thought"))

    for a in clips:
        for b in clips:
            if a.number < b.number and a.start < b.end and b.start < a.end:
                issues.append(Issue("warn", f"clip {a.number:02d}/{b.number:02d}",
                                    "these clips overlap in the source (fine if intentional)"))
    approved_numbers(doc, clips, issues)
    return issues


def clip_words(c: Clip, words: list[dict]) -> list[dict]:
    """Words whose midpoint falls inside the clip and outside its cuts."""
    out = []
    for w in words:
        mid = (w["start"] + w["end"]) / 2
        if c.start <= mid < c.end and not c.in_cut(mid):
            out.append(w)
    return out


# ---- review document --------------------------------------------------------

def _span_text(c: Clip, words: list[dict]) -> str:
    """Verbatim words across the whole clip span, cut words struck through."""
    parts, struck = [], []
    for w in words:
        mid = (w["start"] + w["end"]) / 2
        if not c.start <= mid < c.end:
            continue
        if c.in_cut(mid):
            struck.append(w["word"])
            continue
        if struck:
            parts.append(f"~~{' '.join(struck)}~~")
            struck = []
        parts.append(w["word"])
    if struck:
        parts.append(f"~~{' '.join(struck)}~~")
    return " ".join(parts)


def _opening_line(text_words: list[dict]) -> str:
    out = []
    for w in text_words:
        out.append(w["word"])
        if SENTENCE_END.search(w["word"]) or len(out) >= 30:
            break
    return " ".join(out)


def _reframe_text(c: Clip, hours: bool) -> str:
    names = {v: k for k, v in REFRAME_NAMES.items()}
    if len(c.reframe) == 1:
        return names.get(c.reframe[0][1], f"x={c.reframe[0][1]:.2f}")
    return "; ".join(f"{fmt_time(at, hours)} → {names.get(x, f'x={x:.2f}')}" for at, x in c.reframe)


def render_review(doc: dict, clips: list[Clip], segments: list[dict], words: list[dict],
                  issues: list[Issue], source_seconds: float | None) -> str:
    src = doc.get("source") or {}
    hours = (source_seconds or 0) >= 3600
    w, h = FORMATS.get(doc["format"], (0, 0))
    total = sum(c.duration for c in clips)
    lines = [
        f"# Clips — {src.get('title') or doc.get('slug', '')}",
        "",
        f"> **Source:** {src.get('title', 'REPLACE')} — {src.get('creator', 'REPLACE')}"
        + (f" — {src['url']}" if src.get("url") else "") + "<br>",
        f"> **Kind:** {src.get('kind', 'unspecified')}",
        "",
        f"**Slug:** `{doc.get('slug', '')}` | **Format:** {doc['format']} {w}x{h} | "
        f"**Captions:** {doc['captions']} | **Clips proposed:** {len(clips)} "
        f"({total:.0f}s total) | **Source length:** "
        + (fmt_time(source_seconds, hours) if source_seconds else "unknown"),
        "",
        "Review each clip, then **approve in writing** — reply `approved` for all, or "
        "`approve 1, 3, 4` for a subset. Per clip you can also write `DROP`, "
        "`TRIM START mm:ss` / `TRIM END mm:ss`, `EXTEND ...`, or a plain-language note. "
        "Nothing is built in DaVinci Resolve until you approve.",
        "",
    ]
    for c in clips:
        cw = clip_words(c, words)
        r = c.raw
        lines.append(f"## {c.number:02d}. {c.title or c.id} (~{c.duration:.1f}s)")
        span = f"[{fmt_time(c.start, hours)}–{fmt_time(c.end, hours)}]"
        if c.cuts:
            span += " — cuts removed: " + ", ".join(
                f"{fmt_time(s, hours)}–{fmt_time(e, hours)}" for s, e in sorted(c.cuts))
        lines.append(f"- **In–out (source):** {span}")
        lines.append(f"- **Opens on:** {_opening_line(cw)}")
        if r.get("hook"):
            lines.append(f"- **On-screen hook:** {r['hook']}")
        lines.append(f"- **Why it works:** {r.get('why', '')}")
        if r.get("speakers"):
            lines.append(f"- **Speakers:** {', '.join(map(str, r['speakers']))}")
        if doc["format"] != "landscape":
            lines.append(f"- **Reframe:** {_reframe_text(c, hours)}")
        if r.get("caption"):
            lines.append(f"- **Post caption:** {r['caption']}")
        if r.get("context"):
            lines.append(f"- **Context check:** {r['context']}")
        lines.append(f"- **Transcript:** {_span_text(c, words)}")
        lines.append("- **Notes:**")
        lines.append("")

    lines += [
        "## Full source transcript",
        "",
        "Every line of the long-form source, timestamped, with each proposed clip's "
        "start and end marked — for checking what each clip leaves out.",
        "",
    ]
    starts = sorted(clips, key=lambda c: c.start)
    pending_ends: list[Clip] = []
    si = 0
    for seg in segments:
        s, e = float(seg["start"]), float(seg["end"])
        # A clip that ended in the gap before this line closes before it.
        for c in sorted([c for c in pending_ends if c.end <= s + EDGE_TOLERANCE], key=lambda c: c.end):
            lines.append(f"- **■ Clip {c.number:02d} ends**")
            pending_ends.remove(c)
        while si < len(starts) and starts[si].start < e:
            c = starts[si]
            lines.append(f"- **▶ Clip {c.number:02d} starts — {c.title or c.id}**")
            pending_ends.append(c)
            si += 1
        lines.append(f"- `[{fmt_time(s, hours)}–{fmt_time(e, hours)}]` {seg['text'].strip()}")
        for c in sorted([c for c in pending_ends if c.end <= e + EDGE_TOLERANCE],
                        key=lambda c: c.end):
            lines.append(f"- **■ Clip {c.number:02d} ends**")
            pending_ends.remove(c)
    for c in starts[si:] + pending_ends:
        lines.append(f"- **■ Clip {c.number:02d} ends** (past the last transcript line)")
    lines.append("")

    lines += ["## Source credit", "",
              f"Original: {src.get('title', 'REPLACE')} — {src.get('creator', 'REPLACE')}"
              + (f" — {src['url']}" if src.get("url") else "") + ". Credit goes in each clip's "
              "post description.", ""]
    if issues:
        lines += ["## Lint", ""] + [f"- {i}" for i in issues] + [""]
    return "\n".join(lines)


# ---- build plan -------------------------------------------------------------

def pan_for(x: float, canvas: tuple[int, int], source: tuple[int, int]) -> float:
    """Horizontal Pan (timeline pixels) that centres the crop on source x (0-1),
    for a timeline set to scale-to-fill ("Scale full frame with crop")."""
    cw, ch = canvas
    sw, sh = source
    scaled_w = sw * max(cw / sw, ch / sh)
    limit = max(0.0, (scaled_w - cw) / 2)
    return round(max(-limit, min(limit, (0.5 - x) * scaled_w)), 1)


def clip_pieces(c: Clip) -> list[tuple[float, float, float]]:
    """(src_start, src_end, x) pieces: kept spans split at reframe switches."""
    switches = c.reframe or [(c.start, 0.5)]
    pieces = []
    for s, e in c.kept:
        bounds = sorted({s, e, *[at for at, _ in switches if s < at < e]})
        for a, b in zip(bounds, bounds[1:]):
            x = [sx for at, sx in switches if at <= a] or [switches[0][1]]
            pieces.append((a, b, x[-1]))
    return pieces


def build_plan(doc: dict, clips: list[Clip], approved: list[int], fps: float,
               source_size: tuple[int, int], slug: str) -> dict:
    canvas = FORMATS[doc["format"]]
    out = {"slug": slug, "format": doc["format"], "canvas": list(canvas), "fps": fps,
           "source_size": list(source_size), "captions": doc["captions"],
           "approval": doc.get("approval"), "clips": []}
    for c in clips:
        if c.number not in approved:
            continue
        record, pieces = 0, []
        for s, e, x in clip_pieces(c):
            sf, ef = round(s * fps), round(e * fps)
            pieces.append({"src_start": round(s, 3), "src_end": round(e, 3),
                           "start_frame": sf, "end_frame": ef - 1, "record_frame": record,
                           "pan": pan_for(x, canvas, source_size) if doc["format"] != "landscape" else 0.0})
            record += ef - sf
        out["clips"].append({
            "number": c.number, "id": c.id, "title": c.title,
            "timeline": f"{slug}-{c.id}", "export": f"exports/{slug}-{c.id}.mp4",
            "captions_srt": f"captions/{c.id}.srt" if doc["captions"] == "burned" else None,
            "total_frames": record, "pieces": pieces,
        })
    return out


def caption_srt(c: Clip, words: list[dict]) -> str:
    """Short caption chunks, times on the clip's own timeline (cuts closed up)."""
    chunks: list[list[dict]] = []
    cur: list[dict] = []
    for w in clip_words(c, words):
        text_len = len(" ".join(x["word"] for x in cur + [w]))
        if cur and (len(cur) >= CAPTION_MAX_WORDS or text_len > CAPTION_MAX_CHARS
                    or w["start"] - cur[-1]["end"] > 0.7
                    or any(cur[-1]["end"] - EDGE_TOLERANCE <= cs and ce <= w["start"] + EDGE_TOLERANCE
                           for cs, ce in c.cuts)):
            chunks.append(cur)
            cur = []
        cur.append(w)
        if re.search(r"[.!?,;:]$", w["word"]):
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    out = []
    for i, ch in enumerate(chunks, start=1):
        a = c.to_clip_time(max(ch[0]["start"], c.start))
        b = c.to_clip_time(min(ch[-1]["end"], c.end))
        if i < len(chunks):
            b = min(b, c.to_clip_time(chunks[i][0]["start"]))
        out.append(f"{i}\n{fmt_srt(a)} --> {fmt_srt(max(b, a + 0.3))}\n"
                   f"{' '.join(w['word'] for w in ch)}\n")
    return "\n".join(out)


# ---- main -------------------------------------------------------------------

def _source_seconds(project: Path, segments: list[dict]) -> float | None:
    info = project / "source" / "source_info.json"
    if info.exists():
        try:
            d = json.loads(info.read_text(encoding="utf-8")).get("duration")
            if d:
                return float(d)
        except (ValueError, OSError):
            pass
    return float(segments[-1]["end"]) if segments else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", type=Path, required=True, help="D:\\Videos\\<slug>")
    ap.add_argument("--transcript", type=Path, help="default: transcripts/source.json")
    ap.add_argument("--build-plan", action="store_true",
                    help="write clips.build.json + captions (requires recorded approval)")
    ap.add_argument("--fps", type=float, help="source frame rate (--build-plan)")
    ap.add_argument("--source-size", help="source WxH, e.g. 1920x1080 (--build-plan)")
    args = ap.parse_args()

    project = args.project
    plan_path = project / "script" / "clips.yaml"
    doc = load_plan(plan_path)
    segments, words = load_transcript(args.transcript or project / "transcripts" / "source.json")
    if not words:
        print("error: transcript has no word timestamps -- re-run tools/transcribe.py", file=sys.stderr)
        return 1
    issues: list[Issue] = []
    clips = parse_clips(doc, issues)
    source_seconds = _source_seconds(project, segments)
    issues += validate(doc, clips, words, source_seconds)
    slug = str(doc.get("slug") or project.name)

    review = project / "script" / "clips.md"
    review.write_text(render_review(doc, clips, segments, words, issues, source_seconds),
                      encoding="utf-8")
    for i in issues:
        print(i)
    print(f"wrote {review}")
    errors = [i for i in issues if i.level == "error"]

    if args.build_plan:
        if errors:
            print("error: fix the lint errors above before building", file=sys.stderr)
            return 1
        approved = approved_numbers(doc, clips, [])
        if not approved:
            print("error: no written approval recorded in clips.yaml `approval:` -- "
                  "the user approves the clips in writing before anything is built", file=sys.stderr)
            return 1
        if not args.fps or not args.source_size:
            print("error: --build-plan needs --fps and --source-size (ffprobe the source)", file=sys.stderr)
            return 1
        sw, sh = (int(v) for v in args.source_size.lower().split("x"))
        plan = build_plan(doc, clips, approved, args.fps, (sw, sh), slug)
        (project / "script" / "clips.build.json").write_text(json.dumps(plan, indent=2), encoding="utf-8")
        if doc["captions"] == "burned":
            cap_dir = project / "captions"
            cap_dir.mkdir(exist_ok=True)
            for c in clips:
                if c.number in approved:
                    (cap_dir / f"{c.id}.srt").write_text(caption_srt(c, words), encoding="utf-8")
        print(f"wrote build plan for clips {', '.join(f'{n:02d}' for n in approved)}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

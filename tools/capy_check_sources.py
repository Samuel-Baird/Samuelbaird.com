#!/usr/bin/env python3
"""Lint a Saint Capybara project's beats.yaml against research/sources.yaml
(and, for article projects, against source/source.md + source_info.json).

Rules (see docs/saint-capybara/research-protocol.md and script-format.md):
  - every factual beat cites >=1 source id, unless opinion: true
    (`excerpt` beats are exempt: they are validated against source.md)
  - every cited source id resolves in sources.yaml and is inspected: true
  - a card beat's quote is a normalized-substring of its source's recorded quote
  - a source whose type is apologetic-lead must have traced_to set, and any
    beat relying ONLY on apologetic-lead sources (no traced primary/scholarly
    backing among its other cited sources) is a warning (--strict: error)
  - sensitive: true forbids amused/happy poses anywhere in the video
  - the closing beat's text must end on "...God bless." (brand.md sec 5a)
  - unused sources (declared but never cited by any beat) are reported as info
  - source time (clip + excerpt beats) must be <= 30% of the runtime
    (error; --draft: warning)
  - `stage: freeze` before any clip beat is an error (nothing to freeze)
  Article projects (source_info.json `kind: article`):
  - excerpt beats require kind: article; source.md's sha256 must equal
    source_info.json's text_sha256 (the text responded to is pinned)
  - each excerpt's `[...]`-separated fragments must be verbatim, in-order
    substrings of the anchored paragraph(s) (nearest-paragraph hint on failure)
  - excerpted words > 25% of the article -> warning, > 40% -> error;
    zero excerpts -> warning
  - the responded-to article is the `type: critic` entry with
    `source_kind: article`; it must have `url`, and `archive_url`
    (warning; --strict: error)

Usage:
    python tools/capy_check_sources.py --project D:\\Videos\\<slug> [--strict] [--draft]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import yaml
from capy import beats as beats_mod
from capy import excerpts as excerpts_mod
from capy import source as source_mod
from capy.poses import SENSITIVE_FORBIDDEN
from capy.source import normalize  # noqa: F401  (re-exported; was defined here before capy.source existed)

try:  # ¶ in hints needs a utf-8 console on Windows
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

Issue = beats_mod.Issue

EXCERPT_ARTICLE_WARN_FRACTION = 0.25
EXCERPT_ARTICLE_MAX_FRACTION = 0.40


def load_sources(path: Path) -> dict:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return {s["id"]: s for s in data.get("sources", []) if s.get("id")}


def _excerpt_kind_shim(issues: list[Issue]) -> list[Issue]:
    """Until capy.beats.BEAT_KINDS includes "excerpt", beats.validate()
    reports every excerpt beat as an unknown kind. Those beats are fully
    validated by capy.excerpts instead, so drop that one message here."""
    if excerpts_mod.EXCERPT_KIND in beats_mod.BEAT_KINDS:
        return issues
    kept = []
    dropped = 0
    for i in issues:
        if i.level == "error" and i.message.startswith("unknown kind 'excerpt'"):
            dropped += 1
            continue
        kept.append(i)
    if dropped:
        kept.append(Issue("info", None, f"{dropped} excerpt beat(s) validated by capy.excerpts (capy.beats.BEAT_KINDS does not list 'excerpt' yet)"))
    return kept


def check_source_time(doc: dict, total: float, per_beat: dict[str, float], *, draft: bool) -> list[Issue]:
    issues: list[Issue] = []
    if total <= 0:
        return issues
    src = excerpts_mod.source_time_seconds(doc, per_beat)
    frac = src / total
    if frac > excerpts_mod.SOURCE_TIME_MAX_FRACTION:
        level = "warning" if draft else "error"
        issues.append(Issue(level, None, f"source time (clips + excerpts) is {src:.1f}s of {total:.1f}s ({frac:.0%}), over the {excerpts_mod.SOURCE_TIME_MAX_FRACTION:.0%} budget -- trim clips/excerpts or add response"))
    return issues


def find_critic_article_entry(sources: dict) -> dict | None:
    for s in sources.values():
        if s.get("type") == "critic" and (s.get("source_kind") == "article" or str(s.get("locator", "")).replace("\\", "/").endswith("source/source.md")):
            return s
    return None


def check_source_fields(project: Path, doc: dict, info: source_mod.SourceInfo, sources: dict, *, strict: bool) -> tuple[list[Issue], source_mod.Article | None]:
    """Article-level checks. Returns (issues, article-or-None)."""
    issues: list[Issue] = []
    excerpt_beats = [b for b in doc.get("beats", []) if excerpts_mod.is_excerpt(b)]

    if info.kind not in source_mod.SOURCE_KINDS:
        issues.append(Issue("error", None, f"source_info.json kind '{info.kind}' is not one of {sorted(source_mod.SOURCE_KINDS)}"))
        return issues, None

    if info.kind != "article":
        if excerpt_beats:
            ids = ", ".join(b.get("id", "?") for b in excerpt_beats)
            issues.append(Issue("error", None, f"excerpt beat(s) [{ids}] need an article source (source_info.json kind: article, written by capy_ingest.py --article-file); this project's source is '{info.kind}'"))
        return issues, None

    # --- article project ---
    article: source_mod.Article | None = None
    try:
        article = source_mod.load_article(project)
    except FileNotFoundError as e:
        issues.append(Issue("error", None, str(e)))
    except ValueError as e:
        issues.append(Issue("error", None, f"source.md is malformed: {e}"))

    if article is not None:
        if not info.text_sha256:
            issues.append(Issue("error", None, "source_info.json has no text_sha256 -- re-run capy_ingest.py --article-file so the article text is pinned"))
        elif article.sha256 != info.text_sha256:
            issues.append(Issue("error", None, f"source/source.md has been edited since ingest: sha256 {article.sha256[:12]}… != source_info.json text_sha256 {info.text_sha256[:12]}… (re-ingest, or restore the archived text; excerpts are only valid against the pinned text)"))
        if info.paragraph_count and info.paragraph_count != article.count:
            issues.append(Issue("error", None, f"source.md has {article.count} paragraphs but source_info.json says {info.paragraph_count}"))
        if not excerpt_beats:
            issues.append(Issue("warning", None, "article project has no excerpt beats -- the source's own words are how the viewer sees what is being responded to"))
        elif article.word_count:
            used = excerpts_mod.excerpt_word_total(doc)
            frac = used / article.word_count
            if frac > EXCERPT_ARTICLE_MAX_FRACTION:
                issues.append(Issue("error", None, f"excerpts quote {used} of the article's {article.word_count} words ({frac:.0%}), over the {EXCERPT_ARTICLE_MAX_FRACTION:.0%} cap (copyright: short, transformative excerpts only)"))
            elif frac > EXCERPT_ARTICLE_WARN_FRACTION:
                issues.append(Issue("warning", None, f"excerpts quote {used} of the article's {article.word_count} words ({frac:.0%}), above the {EXCERPT_ARTICLE_WARN_FRACTION:.0%} guideline"))

    if not info.url:
        issues.append(Issue("error", None, "source_info.json has no url for the article"))
    if not info.archive_url:
        issues.append(Issue("error" if strict else "warning", None, "source_info.json has no archive_url (run capy_ingest.py with --archive auto, or pass --archive-url from a capture made in the publishing browser profile)"))
    if info.paywalled and info.text_from != "user_paste":
        issues.append(Issue("warning", None, f"paywalled: true but text_from is '{info.text_from}' (expected user_paste -- an archive of a paywalled page is a stub)"))

    critic = find_critic_article_entry(sources)
    if critic is None:
        issues.append(Issue("error", None, "sources.yaml needs the responded-to article as a `type: critic` entry with `source_kind: article` and `locator: source/source.md` (see templates/sources.yaml)"))
    else:
        cid = critic.get("id")
        if not critic.get("url"):
            issues.append(Issue("error", None, f"critic article source '{cid}' has no url"))
        elif info.url and critic["url"] != info.url and critic["url"] != info.canonical_url:
            issues.append(Issue("warning", None, f"critic article source '{cid}' url differs from source_info.json url"))
        if not critic.get("archive_url"):
            issues.append(Issue("error" if strict else "warning", None, f"critic article source '{cid}' has no archive_url"))
        if critic.get("quote"):
            issues.append(Issue("warning", None, f"critic article source '{cid}' should have quote: null -- excerpt beats quote source.md directly"))
        if not critic.get("inspected"):
            issues.append(Issue("error", None, f"critic article source '{cid}' is not marked inspected: true"))
    return issues, article


def check_excerpts(doc: dict, article: source_mod.Article | None) -> list[Issue]:
    issues: list[Issue] = []
    if article is None:
        return issues
    for beat in doc.get("beats", []):
        if not excerpts_mod.is_excerpt(beat):
            continue
        bid = beat.get("id")
        text, para = beat.get("text"), beat.get("para")
        if not text or para is None:
            continue  # validate_excerpt_beats already reported it
        match = source_mod.find_excerpt(article, str(text), para)
        if not match.ok:
            issues.append(Issue("error", bid, match.message))
    return issues


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--strict", action="store_true", help="upgrade apologetic-only-support and missing-archive warnings to errors")
    ap.add_argument("--draft", action="store_true", help="downgrade duration/source-time budget errors to warnings")
    args = ap.parse_args()

    beats_path = args.project / "script" / "beats.yaml"
    sources_path = args.project / "research" / "sources.yaml"
    escalation_path = args.project / "research" / "ESCALATION.md"

    if not beats_path.exists():
        print(f"error: {beats_path} not found")
        return 2

    doc = beats_mod.load_beats(beats_path)
    sources = load_sources(sources_path)
    info = source_mod.load_source_info(args.project)

    issues: list[Issue] = _excerpt_kind_shim(list(beats_mod.validate(doc)))
    # beats.validate() delegates to capy.excerpts.validate_excerpt_beats once
    # wired; only call it here if it doesn't, so nothing is reported twice.
    if "validate_excerpt_beats" not in beats_mod.validate.__code__.co_names:
        issues += excerpts_mod.validate_excerpt_beats(doc)

    total, per_beat = beats_mod.resolve_durations(doc)
    issues += beats_mod.check_duration_budget(doc, total, draft=args.draft)
    issues += check_source_time(doc, total, per_beat, draft=args.draft)

    used_ids: set[str] = set()
    for beat in doc.get("beats", []):
        bid = beat["id"]
        cited = beat.get("sources") or []
        used_ids.update(cited)

        for sid in cited:
            src = sources.get(sid)
            if src is None:
                issues.append(Issue("error", bid, f"cites unknown source id '{sid}' (not in sources.yaml)"))
                continue
            if not src.get("inspected"):
                issues.append(Issue("error", bid, f"source '{sid}' is not marked inspected: true"))
            if src.get("type") == "apologetic-lead" and not src.get("traced_to"):
                issues.append(Issue("error", bid, f"apologetic-lead source '{sid}' has no traced_to (must trace to a primary/scholarly source)"))

        if cited:
            all_apologetic = cited and all(sources.get(s, {}).get("type") == "apologetic-lead" for s in cited)
            if all_apologetic:
                level = "error" if args.strict else "warning"
                issues.append(Issue(level, bid, "relies only on apologetic-lead source(s) with no traced primary/scholarly backing among its citations"))

        if beat.get("kind") == "card":
            quote = beat.get("card", {}).get("quote", "")
            src_ids = cited
            if quote and src_ids:
                matched = False
                for sid in src_ids:
                    src = sources.get(sid)
                    if src and src.get("quote") and normalize(quote) in normalize(src["quote"]):
                        matched = True
                        break
                if not matched:
                    issues.append(Issue("error", bid, "card quote is not a substring of any cited source's recorded quote"))

    field_issues, article = check_source_fields(args.project, doc, info, sources, strict=args.strict)
    issues += field_issues
    issues += check_excerpts(doc, article)
    critic = find_critic_article_entry(sources) if info.kind == "article" else None
    if critic and critic.get("id"):
        used_ids.add(critic["id"])  # the excerpt beats are its citations

    # unused sources -> info
    for sid in sources:
        if sid not in used_ids:
            issues.append(Issue("info", None, f"source '{sid}' is declared but not cited by any beat (fine if researched-but-unused)"))

    if escalation_path.exists():
        issues.append(Issue("error", None, f"unresolved {escalation_path.name} present -- blocks Gate A until addressed"))

    errors = [i for i in issues if i.level == "error"]
    warnings = [i for i in issues if i.level == "warning"]
    infos = [i for i in issues if i.level == "info"]

    for i in issues:
        print(i)

    print(f"\n{len(errors)} error(s), {len(warnings)} warning(s), {len(infos)} info. Total runtime estimate: {total:.1f}s")
    if info.kind == "article" and total:
        src_time = excerpts_mod.source_time_seconds(doc, per_beat)
        print(f"Source time (excerpts): {src_time:.1f}s of {total:.1f}s ({src_time / total:.0%}); budget {excerpts_mod.SOURCE_TIME_MAX_FRACTION:.0%}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

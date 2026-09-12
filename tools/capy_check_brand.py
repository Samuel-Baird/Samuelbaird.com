#!/usr/bin/env python3
"""Anonymity / brand-separation lint for a Saint Capybara project.

See docs/saint-capybara/brand.md sec 9-10. Scans beats.yaml narration
text, research/sources.yaml notes, research/claims.md, the source text
(source/source.md + source/source_info.json -- pasted article text or a
local path can leak a home directory), and (if present) the export
description, for:
  - banned phrases from assets/saint-capybara/banned.txt (gitignored,
    real names/handles) + banned.example.txt (generic cross-promotion
    phrasing, committed)
  - runtime-derived identity tokens (home directory name, os.getlogin(),
    git user.name/user.email) -- computed at scan time, NEVER written to
    any file this tool produces
  - literal home-directory-style paths (C:\\Users\\<name>\\...) appearing
    in any scanned text
  - (--banned) additionally requires banned.txt to actually exist (a
    project can be lint-clean without it, but this flag treats a missing
    banned.txt as a warning so it doesn't go unnoticed)
  - (--mp4 PATH) ffprobe's format tags against an allow-list (title,
    major_brand, minor_version, compatible_brands only -- no `encoder`)
  - PNG files under the project for leftover text/metadata chunks

Usage:
    python tools/capy_check_brand.py --project D:\\Videos\\<slug> [--mp4 exports\\x.mp4] [--banned]
"""
from __future__ import annotations

import argparse
import getpass
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

REPO_ROOT = Path(__file__).resolve().parent.parent
ALLOWED_MP4_TAGS = {"title", "major_brand", "minor_version", "compatible_brands"}


def _git_config(key: str) -> str | None:
    try:
        out = subprocess.run(["git", "config", "--get", key], capture_output=True, text=True)
        val = out.stdout.strip()
        return val or None
    except Exception:
        return None


def runtime_identity_tokens() -> list[str]:
    """Tokens derived from the current runtime environment that must never
    appear in committed/published text. Computed fresh every run, never
    persisted."""
    tokens: set[str] = set()
    try:
        tokens.add(getpass.getuser())
    except Exception:
        pass
    home = Path.home()
    tokens.add(home.name)
    for key in ("user.name", "user.email"):
        val = _git_config(key)
        if val:
            tokens.add(val)
            if key == "user.email" and "@" in val:
                tokens.add(val.split("@")[0])
    return [t for t in tokens if t and len(t) > 2]


def load_banned_phrases(include_missing_warning: bool) -> tuple[list[str], list[str]]:
    """Returns (phrases, warnings)."""
    phrases: list[str] = []
    warnings: list[str] = []
    example = REPO_ROOT / "assets" / "saint-capybara" / "banned.example.txt"
    real = REPO_ROOT / "assets" / "saint-capybara" / "banned.txt"
    for f in (example, real):
        if f.exists():
            for line in f.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    phrases.append(line)
        elif f == real:
            msg = f"{f} does not exist -- creating an empty placeholder so this tool has something to read (see brand.md sec 10)"
            warnings.append(msg)
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(
                "# GITIGNORED. Put the creator's real other names/handles/brand names\n"
                "# here, one per line, case-insensitive substring match. Never commit\n"
                "# this file with real content. See docs/saint-capybara/brand.md sec 10.\n",
                encoding="utf-8",
            )
    return phrases, warnings


def scan_text(label: str, text: str, phrases: list[str], tokens: list[str]) -> list[str]:
    hits = []
    lower = text.lower()
    for p in phrases:
        if p.lower() in lower:
            hits.append(f"{label}: banned phrase match: '{p}'")
    for t in tokens:
        if t.lower() in lower:
            hits.append(f"{label}: runtime identity token leaked: '{t}'")
    if re.search(r"[A-Za-z]:\\Users\\[^\\\"'\n]+", text):
        hits.append(f"{label}: contains a home-directory-style path")
    return hits


def collect_project_text(project: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    beats_path = project / "script" / "beats.yaml"
    if beats_path.exists():
        out["script/beats.yaml"] = beats_path.read_text(encoding="utf-8")
    sources_path = project / "research" / "sources.yaml"
    if sources_path.exists():
        out["research/sources.yaml"] = sources_path.read_text(encoding="utf-8")
    claims_path = project / "research" / "claims.md"
    if claims_path.exists():
        out["research/claims.md"] = claims_path.read_text(encoding="utf-8")
    # Article sources: pasted text or a local path can leak a home directory
    # (plan Part 4.4). source_info.json is scanned for video projects too --
    # its local_file_source is a literal path.
    for rel in ("source/source.md", "source/source_info.json"):
        p = project / rel
        if p.exists():
            out[rel] = p.read_text(encoding="utf-8")
    for desc in (project / "exports").glob("*-description.txt") if (project / "exports").exists() else []:
        out[f"exports/{desc.name}"] = desc.read_text(encoding="utf-8")
    # Multi-angle research briefs and script critique files (research-protocol.md
    # sec 15) -- exactly where a subagent's own chatter ("as an AI...", a local
    # path it happened to mention, etc.) is most likely to leak, since they are
    # free-form prose rather than the structured beats.yaml/sources.yaml/claims.md
    # above. Glob broadly rather than naming exact filenames so a future brief/
    # critique naming convention change doesn't silently stop being scanned.
    research_dir = project / "research"
    if research_dir.exists():
        for md in research_dir.rglob("*.md"):
            rel = md.relative_to(project).as_posix()
            if rel in out:
                continue
            out[rel] = md.read_text(encoding="utf-8")
    return out


def check_png_metadata(project: Path) -> list[str]:
    problems = []
    try:
        from PIL import Image
    except ImportError:
        return ["PIL not available -- skipped PNG metadata scan"]
    for png in project.rglob("*.png"):
        try:
            img = Image.open(png)
            info_keys = [k for k in img.info.keys() if k not in ("transparency",)]
            if info_keys:
                problems.append(f"{png}: has metadata/text chunks: {info_keys}")
        except Exception as e:
            problems.append(f"{png}: could not inspect ({e})")
    return problems


def check_filenames(project: Path, tokens: list[str]) -> list[str]:
    problems = []
    for p in project.rglob("*"):
        name = p.name.lower()
        for t in tokens:
            if t.lower() in name:
                problems.append(f"filename leaks identity token '{t}': {p}")
    return problems


def check_mp4(path: Path) -> list[str]:
    from capy import ff
    problems = []
    tags = ff.probe_tags(path)
    for k in tags:
        if k not in ALLOWED_MP4_TAGS:
            problems.append(f"{path}: disallowed container tag '{k}' = {tags[k]!r}")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--mp4", type=Path, default=None, help="path to an exported mp4 to also check container tags on")
    ap.add_argument("--banned", action="store_true", help="warn if banned.txt is missing (still runs a scan either way)")
    args = ap.parse_args()

    project = args.project
    phrases, load_warnings = load_banned_phrases(args.banned)
    tokens = runtime_identity_tokens()

    problems: list[str] = list(load_warnings)

    for label, text in collect_project_text(project).items():
        problems += scan_text(label, text, phrases, tokens)

    problems += check_png_metadata(project)
    problems += check_filenames(project, tokens)

    if args.mp4:
        if args.mp4.exists():
            problems += check_mp4(args.mp4)
        else:
            problems.append(f"--mp4 path does not exist: {args.mp4}")

    if not problems:
        print("capy_check_brand: clean -- no banned phrases, identity tokens, leaked paths, PNG metadata, or bad filenames found.")
        return 0

    for p in problems:
        print(f"PROBLEM: {p}")
    print(f"\n{len(problems)} problem(s) found.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

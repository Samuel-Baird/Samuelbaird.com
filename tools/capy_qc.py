#!/usr/bin/env python3
"""Automated QC report for a rendered Saint Capybara export -- partial
automation of docs/saint-capybara/review-checklist.md Part B.

Automates the mechanical checks that were previously eyeball/manual:
  - Duration: export duration vs. the beat-clip manifest's summed duration.
  - Loudness: the final export's integrated LUFS against theme.yaml's
    audio.target_lufs (checklist item 5's "metadata clean" spirit, extended
    to loudness since a wrong remux/render step can silently change it).
  - Metadata tags: ffprobe format tags against the allow-list
    (title/major_brand/minor_version/compatible_brands only -- reuses
    capy_check_brand.py's own constant so the two tools can't drift).
  - Response-incoming banner window: frame grabs at t=0 and just after the
    first narration beat starts (checklist item 3a) -- still a human looks
    at the two PNGs, but this tool finds the right timestamps and pulls them.
  - Audio-content-matches-script: transcribes each narration-family beat's
    own span of the FINAL EXPORT (not the standalone beat clip) with
    Whisper and sequence-matches it against that beat's script text --
    this is the automated version of hybrid-resolve-pipeline.md's own
    documented fix for its worst failure mode ("a render can come out
    wrong even when the timeline API says it's correct" -- stale/
    out-of-order beat audio that duration/frame-count checks don't catch).
    A low match ratio is a WARNING, not a hard failure (pronunciation-
    dictionary respellings and Chatterbox's imperfect diction both lower
    the ratio without meaning the beat is actually wrong) -- but a beat
    scoring far below its neighbours is exactly the pattern that bug
    produced, and is worth a manual listen.

Does NOT replace Part B in full. Caption-sync-by-eye, phone-legibility,
the muted-viewing pass, and Gate B (the user's own watch-through) all stay
manual -- this tool exists to clear the mechanical checks first so a human
QC pass is shorter and starts from evidence instead of a checklist.

    python tools/capy_qc.py --project D:\\Videos\\<slug> [--mp4 exports\\x.mp4] [--skip-audio-content]

Without --mp4, uses exports/<slug>.mp4 if present, else the newest
exports/*.mp4 that isn't a *-resolve.mp4 intermediate.

Writes qc/report.json (machine-readable), qc/report.md (human-readable
summary), and qc/frames/*.png (t=0, first-narration-start, and one frame
per distinct beat kind present in the manifest).
"""
from __future__ import annotations

import argparse
import difflib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from capy import ff
from capy.beats import load_beats, NARRATION_FAMILY_KINDS
from capy.layout import Theme

LOUDNESS_TOLERANCE_LU = 1.5  # matches the TP=-1.5 headroom used everywhere else in this pipeline
DURATION_TOLERANCE_SECONDS = 1.0  # remux/container overhead, not a real mismatch signal below this
MIN_CONTENT_MATCH_RATIO = 0.5  # below this, flag for a manual listen (see module docstring)


def find_export(project: Path, mp4: Path | None) -> Path:
    if mp4:
        p = mp4 if mp4.is_absolute() else project / mp4
        if not p.exists():
            raise FileNotFoundError(f"--mp4 given but not found: {p}")
        return p
    named = project / "exports" / f"{project.name}.mp4"
    if named.exists():
        return named
    candidates = sorted(
        (p for p in (project / "exports").glob("*.mp4") if "-resolve" not in p.stem),
        key=lambda p: p.stat().st_mtime, reverse=True,
    )
    if not candidates:
        raise FileNotFoundError(
            f"no export found under {project / 'exports'} -- pass --mp4, or run the "
            "Resolve build + metadata-strip remux first (hybrid-resolve-pipeline.md)"
        )
    return candidates[0]


def load_manifest(project: Path) -> list[dict]:
    path = project / "frames" / "beat_clips_manifest.json"
    if not path.exists():
        raise FileNotFoundError(f"{path} not found -- run capy_render_beat_clips.py first")
    return json.loads(path.read_text(encoding="utf-8"))


def beat_spans(manifest: list[dict]) -> dict[str, tuple[float, float]]:
    """Cumulative [start, end) for each beat id, assuming manifest order
    matches the assembled timeline (hard-cut, back-to-back -- true by
    construction per hybrid-resolve-pipeline.md, as long as the Resolve
    build followed the checklist)."""
    spans: dict[str, tuple[float, float]] = {}
    t = 0.0
    for m in manifest:
        spans[m["id"]] = (t, t + m["duration"])
        t += m["duration"]
    return spans


def check_duration(export: Path, manifest: list[dict]) -> dict:
    expected = sum(m["duration"] for m in manifest)
    actual = ff.probe_duration(export)
    diff = actual - expected
    return {
        "expected_seconds": round(expected, 3),
        "actual_seconds": round(actual, 3),
        "diff_seconds": round(diff, 3),
        "ok": abs(diff) <= DURATION_TOLERANCE_SECONDS,
    }


def check_loudness(export: Path, target_lufs: float) -> dict:
    summary = ff.ebur128_summary(export)
    if summary is None:
        return {"ok": False, "note": "could not parse ebur128 output"}
    lufs = summary.get("lufs")
    ok = lufs is not None and abs(lufs - target_lufs) <= LOUDNESS_TOLERANCE_LU
    return {"lufs": lufs, "lra": summary.get("lra"), "target_lufs": target_lufs, "ok": ok}


def check_tags(export: Path) -> dict:
    import capy_check_brand as brand_lint  # tools/ is on sys.path; reuse its allow-list, don't fork it

    tags = ff.probe_tags(export)
    disallowed = sorted(set(tags) - brand_lint.ALLOWED_MP4_TAGS)
    return {"tags": tags, "disallowed": disallowed, "ok": not disallowed}


def extract_frame(export: Path, at_seconds: float, out_path: Path) -> None:
    ff.run(["ffmpeg", "-y", "-ss", f"{max(0.0, at_seconds):.3f}", "-i", str(export), "-frames:v", "1", str(out_path)])


def grab_frames(project: Path, export: Path, doc: dict, manifest: list[dict], spans: dict[str, tuple[float, float]]) -> list[dict]:
    out_dir = project / "qc" / "frames"
    out_dir.mkdir(parents=True, exist_ok=True)
    grabs: list[dict] = []

    grabs.append({"label": "t0", "at": 0.0})
    beats = doc.get("beats", [])
    first_narration = next((b for b in beats if b.get("kind") in NARRATION_FAMILY_KINDS), None)
    if first_narration and first_narration["id"] in spans:
        start, _ = spans[first_narration["id"]]
        grabs.append({"label": f"first_narration_{first_narration['id']}", "at": start + 0.2})

    seen_kinds: set[str] = set()
    for m in manifest:
        if m["kind"] in seen_kinds:
            continue
        seen_kinds.add(m["kind"])
        s, e = spans[m["id"]]
        grabs.append({"label": f"kind_{m['kind']}_{m['id']}", "at": (s + e) / 2})

    for g in grabs:
        out_path = out_dir / f"{g['label']}.png"
        extract_frame(export, g["at"], out_path)
        g["path"] = str(out_path.relative_to(project))
    return grabs


def _beat_script_text(beat: dict) -> str:
    if beat.get("kind") == "excerpt":
        try:
            from capy.excerpts import speech_text as excerpt_speech_text
            return excerpt_speech_text(beat)
        except ImportError:
            pass
    return (beat.get("text") or "").replace("[...]", "...")


def check_audio_content(export: Path, doc: dict, manifest: list[dict], spans: dict[str, tuple[float, float]]) -> list[dict]:
    """Whisper-transcribe each narration-family beat's span of the FINAL
    EXPORT and sequence-match it against that beat's own script text --
    see module docstring. `clip` beats are skipped (their audio is the
    reacted-to source, not narration text, so there's no script to match)."""
    import tempfile

    from capy.align import _get_whisper_model, _normalize  # internal helpers, same package -- see docstring

    manifest_by_id = {m["id"]: m for m in manifest}
    results: list[dict] = []
    model = None

    for beat in doc.get("beats", []):
        bid = beat["id"]
        if beat.get("kind") not in NARRATION_FAMILY_KINDS or bid not in spans:
            continue
        script_text = _beat_script_text(beat)
        script_words = script_text.split()
        if not script_words:
            continue

        start, end = spans[bid]
        with tempfile.TemporaryDirectory() as td:
            wav = Path(td) / f"{bid}.wav"
            ff.run(["ffmpeg", "-y", "-ss", f"{start:.3f}", "-to", f"{end:.3f}", "-i", str(export), "-ar", "16000", "-ac", "1", str(wav)])
            if model is None:
                model = _get_whisper_model()
            try:
                heard = model.transcribe(str(wav), word_timestamps=False)
            except Exception as e:
                results.append({"beat_id": bid, "ok": False, "note": f"whisper failed: {e}"})
                continue

        heard_words = [_normalize(w) for w in (heard.get("text") or "").split() if _normalize(w)]
        script_norm = [_normalize(w) for w in script_words]
        matcher = difflib.SequenceMatcher(a=script_norm, b=heard_words, autojunk=False)
        n_matched = sum((a1 - a0) for tag, a0, a1, _b0, _b1 in matcher.get_opcodes() if tag == "equal")
        ratio = n_matched / len(script_norm)
        results.append({
            "beat_id": bid, "kind": beat.get("kind"), "match_ratio": round(ratio, 3),
            "ok": ratio >= MIN_CONTENT_MATCH_RATIO,
            "recognized_preview": (heard.get("text") or "")[:120],
        })
    return results


def render_markdown(report: dict) -> str:
    lines = [f"# QC report — {report['project']}", "", f"Export: `{report['export']}`", ""]

    d = report["duration"]
    mark = "OK" if d["ok"] else "MISMATCH"
    lines.append(f"## Duration — {mark}")
    lines.append(f"expected {d['expected_seconds']}s, actual {d['actual_seconds']}s (diff {d['diff_seconds']:+.2f}s)")
    lines.append("")

    l = report["loudness"]
    mark = "OK" if l.get("ok") else "OUT OF RANGE"
    lines.append(f"## Loudness — {mark}")
    lines.append(f"{l.get('lufs')} LUFS (target {l.get('target_lufs')} ± {LOUDNESS_TOLERANCE_LU}), LRA {l.get('lra')}")
    lines.append("")

    t = report["tags"]
    mark = "OK" if t["ok"] else "DISALLOWED TAGS PRESENT"
    lines.append(f"## Metadata tags — {mark}")
    if t["disallowed"]:
        lines.append(f"disallowed: {', '.join(t['disallowed'])}")
    lines.append(f"all tags: {json.dumps(t['tags'])}")
    lines.append("")

    lines.append("## Frames (Part B item 3a — response-incoming banner, item 3 — phone legibility)")
    for g in report["frames"]:
        lines.append(f"- `{g['label']}` at {g['at']:.2f}s -> `{g['path']}`")
    lines.append("")

    if report.get("audio_content") is not None:
        rows = report["audio_content"]
        flagged = [r for r in rows if not r.get("ok")]
        mark = "OK" if not flagged else f"{len(flagged)} BEAT(S) FLAGGED FOR A LISTEN"
        lines.append(f"## Audio content vs. script — {mark}")
        lines.append("(low match ratio can also mean a pronunciation respelling or Chatterbox diction — flagged, not failed)")
        for r in rows:
            if "match_ratio" in r:
                flag = "" if r["ok"] else "  <-- listen to this one"
                lines.append(f"- `{r['beat_id']}` ({r['kind']}): match {r['match_ratio']:.0%}{flag}")
            else:
                lines.append(f"- `{r['beat_id']}`: {r.get('note')}")
        lines.append("")

    lines.append("## Still manual (Part B)")
    lines.append("- Caption sync spot-check by eye")
    lines.append("- Phone-size legibility read of the frames above")
    lines.append("- Evidence hold (long enough to actually read)")
    lines.append("- Muted-viewing pass (captions alone convey the argument)")
    lines.append("- Anonymity re-pass beyond capy_check_brand.py (filenames under D:\\Videos\\<slug>\\)")
    lines.append("- Gate B: the user's own watch-through")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--mp4", type=Path, default=None)
    ap.add_argument("--skip-audio-content", action="store_true", help="skip the whisper-based per-beat content check (slow: loads a whisper model)")
    args = ap.parse_args()

    project = args.project.resolve()
    export = find_export(project, args.mp4)
    doc = load_beats(project / "script" / "beats.yaml")
    manifest = load_manifest(project)
    spans = beat_spans(manifest)
    theme = Theme.load()
    target_lufs = theme.data.get("audio", {}).get("target_lufs", -16)

    print(f"QC: {project.name} -> {export}")
    report: dict = {
        "project": project.name,
        "export": str(export.relative_to(project)) if export.is_relative_to(project) else str(export),
        "duration": check_duration(export, manifest),
        "loudness": check_loudness(export, target_lufs),
        "tags": check_tags(export),
    }
    print("duration:", report["duration"])
    print("loudness:", report["loudness"])
    print("tags:", report["tags"])

    report["frames"] = grab_frames(project, export, doc, manifest, spans)
    print(f"frames: {len(report['frames'])} grabbed -> {project / 'qc' / 'frames'}")

    if args.skip_audio_content:
        report["audio_content"] = None
    else:
        print("audio content check: loading whisper (once)...")
        report["audio_content"] = check_audio_content(export, doc, manifest, spans)
        flagged = [r for r in report["audio_content"] if not r.get("ok")]
        print(f"audio content: {len(report['audio_content'])} beat(s) checked, {len(flagged)} flagged")

    qc_dir = project / "qc"
    qc_dir.mkdir(parents=True, exist_ok=True)
    (qc_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (qc_dir / "report.md").write_text(render_markdown(report), encoding="utf-8")
    print(f"\nWrote {qc_dir / 'report.json'} and {qc_dir / 'report.md'}")

    hard_fail = not (report["duration"]["ok"] and report["loudness"]["ok"] and report["tags"]["ok"])
    return 1 if hard_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())

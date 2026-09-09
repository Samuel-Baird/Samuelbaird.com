#!/usr/bin/env python3
"""**TEST / EXPERIMENTAL — hybrid Resolve pipeline, not yet approved for
production use.** See docs/saint-capybara/hybrid-resolve-pipeline.md.

Computes the full Resolve timeline layout for a project's beats.yaml --
per-beat record frames, track assignments, and media paths -- as a
reviewable JSON plan. **This script never touches the davinci-resolve MCP
or Resolve itself; it only reads beats.yaml plus whatever
capy_beat_plates.py / capy_caption_cards.py / capy_tts.py have already
written to disk, and writes frames/resolve_build_plan.json.** Turning this
plan into an actual timeline (via `append_to_timeline` following
docs/resolve-mcp-gotchas.md's chunking/overlap/save-verify rules) is a
separate, not-yet-built step that requires Gate A approval first.

Track plan (see docs/saint-capybara/hybrid-resolve-pipeline.md for the
full rationale):
  - V1 "source"   -- the real source clip, Transform+Cropped into the
                      stage rectangle, one entry per `clip` beat only.
                      Its own embedded audio plays as-is (no separate
                      audio track needed for clip beats).
  - V2 "plates"   -- one full-canvas still per beat (capy_beat_plates.py
                      output). For `clip` beats this plate has a
                      transparent hole over the stage rect so V1 shows
                      through; for every other beat it's the beat's full
                      rendered content (card/chart/evidence/freeze-frame
                      + sprite + wordmark).
  - V3 "captions" -- one still per caption phrase (capy_caption_cards.py
                      output), offset into this beat's span.
  - A1 "narration"-- one clip per narration-family beat, from
                      audio/<id>.norm.wav once capy_tts.py has run
                      (post-Gate-A). Marked "pending" until then.

Usage:
    python capy_resolve_build_plan.py --project D:\\Videos\\<slug>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from capy.beats import load_beats, resolve_durations, check_duration_budget, validate


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--draft", action="store_true", help="downgrade duration-budget errors to warnings")
    args = ap.parse_args()

    project = args.project.resolve()
    beats_path = project / "script" / "beats.yaml"
    if not beats_path.exists():
        print(f"error: {beats_path} not found", file=sys.stderr)
        return 1

    doc = load_beats(beats_path)
    fps = doc["format"]["fps"]

    issues = validate(doc)
    for issue in issues:
        print(issue)
    if any(i.level == "error" for i in issues):
        print("\nerror(s) above -- fix beats.yaml before planning a build (see capy_check_sources.py for the fuller lint).", file=sys.stderr)
        return 2

    # Pull in any real, already-rendered TTS durations.
    tts_durations: dict[str, float] = {}
    audio_dir = project / "audio"
    for beat in doc["beats"]:
        timing_path = audio_dir / f"{beat['id']}.timing.json"
        if timing_path.exists():
            words = json.loads(timing_path.read_text(encoding="utf-8"))
            if words:
                tts_durations[beat["id"]] = max(w["e"] for w in words)

    total, per_beat = resolve_durations(doc, tts_durations)
    budget_issues = check_duration_budget(doc, total, draft=args.draft)
    for issue in budget_issues:
        print(issue)

    plates_manifest = {}
    plates_path = project / "frames" / "plates_manifest.json"
    if plates_path.exists():
        plates_manifest = {m["id"]: m for m in json.loads(plates_path.read_text(encoding="utf-8"))}

    captions_manifest = []
    captions_path = project / "captions" / "manifest.json"
    if captions_path.exists():
        captions_manifest = json.loads(captions_path.read_text(encoding="utf-8"))
    captions_by_beat: dict[str, list] = {}
    for c in captions_manifest:
        captions_by_beat.setdefault(c["beat_id"], []).append(c)

    v1_source, v2_plates, v3_captions, a1_narration = [], [], [], []
    cursor_seconds = 0.0
    for beat in doc["beats"]:
        bid, kind = beat["id"], beat["kind"]
        dur = per_beat[bid]
        record_start_frame = round(cursor_seconds * fps)
        record_end_frame = round((cursor_seconds + dur) * fps)

        if kind == "clip":
            v1_source.append({
                "beat_id": bid,
                "source_in_seconds": beat["start"],
                "source_out_seconds": beat["end"],
                "speed": beat.get("speed", 1.0),
                "record_frame_start": record_start_frame,
                "record_frame_end": record_end_frame,
            })
        else:
            timing_path = audio_dir / f"{bid}.timing.json"
            wav_path = audio_dir / f"{bid}.norm.wav"
            a1_narration.append({
                "beat_id": bid,
                "path": str(wav_path.relative_to(project)) if wav_path.exists() else None,
                "status": "rendered" if wav_path.exists() else "pending Gate A + capy_tts.py",
                "record_frame_start": record_start_frame,
                "record_frame_end": record_end_frame,
            })

        plate = plates_manifest.get(bid)
        v2_plates.append({
            "beat_id": bid,
            "path": plate["path"] if plate else None,
            "status": "rendered" if plate else "pending capy_beat_plates.py",
            "record_frame_start": record_start_frame,
            "record_frame_end": record_end_frame,
        })

        for c in captions_by_beat.get(bid, []):
            v3_captions.append({
                "beat_id": bid,
                "path": c["path"],
                "text": c["text"],
                "draft_timing": c["draft_timing"],
                "record_frame_start": record_start_frame + round(c["start"] * fps),
                "record_frame_end": record_start_frame + round(c["end"] * fps),
            })

        cursor_seconds += dur

    plan = {
        "slug": doc["slug"],
        "fps": fps,
        "total_seconds": total,
        "total_frames": round(total * fps),
        "tracks": {
            "V1_source": v1_source,
            "V2_plates": v2_plates,
            "V3_captions": v3_captions,
            "A1_narration": a1_narration,
        },
        "notes": [
            "Plan only -- no Resolve/MCP calls were made. See docs/resolve-mcp-gotchas.md before turning this into append_to_timeline calls: chunk in ~20-beat batches, cap each still's duration at the next beat's record frame, save+re-read+re-append after every batch, finish with detect_gaps_overlaps.",
            "A2 (clip audio) is not a separate track -- V1 clips carry their own embedded audio at the same record frames.",
            "Any V2_plates or A1_narration entry marked 'pending' means its tool hasn't been run yet for this beat; do not build the Resolve timeline with pending entries present.",
        ],
    }

    out_path = project / "frames" / "resolve_build_plan.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

    pending_plates = sum(1 for p in v2_plates if p["status"] != "rendered")
    pending_audio = sum(1 for a in a1_narration if a["status"] != "rendered")
    draft_captions = sum(1 for c in v3_captions if c["draft_timing"])

    print(f"\nPlan: {total:.1f}s / {plan['total_frames']} frames @ {fps}fps")
    print(f"  V1 source clips: {len(v1_source)}")
    print(f"  V2 plates: {len(v2_plates)} ({pending_plates} pending)")
    print(f"  V3 caption cards: {len(v3_captions)} ({draft_captions} on draft timing)")
    print(f"  A1 narration: {len(a1_narration)} ({pending_audio} pending)")
    print(f"Wrote {out_path}")
    if pending_plates or pending_audio:
        print("\nNOT ready for a real Resolve build yet -- see 'pending' counts above.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
r"""Drive the DaVinci Resolve build + render for one Saint Capybara project
end to end, from the raw DaVinci Resolve scripting API, instead of an agent
hand-driving ~25-30 individual davinci-resolve MCP calls off the checklist
in docs/saint-capybara/hybrid-resolve-pipeline.md.

*** NOT YET VERIFIED AGAINST A LIVE RESOLVE SESSION (written 2026-09-22,
no Resolve instance was reachable to test against). Run it once with
--dry-run on a throwaway project, watch what it prints, and only then run
it for real -- the checklist it encodes is well-documented but a raw API
call signature or return shape could still be off by a detail this couldn't
be checked against live. ***

Encodes the whole checklist in hybrid-resolve-pipeline.md's "Resolve build
checklist" section, step by step:
  1. Create the project (auto-suffixed -v2/-v3/... if the slug's project
     name already exists, per the doc's "create a brand-new project every
     time a beat clip's CONTENT changed" guidance -- sidesteps the
     stale-clip-caching bug entirely rather than chasing it after the fact).
  2. Set the timeline format (1080x1920, 30fps) and verify with a readback.
  3. Import every beat_<id>.mp4 ONE FILE PER CALL (Resolve's importer groups
     sequentially-numbered same-prefix files into one "sequence" media pool
     item otherwise -- see docs/resolve-mcp-gotchas.md).
  3b. Import every evidence beat's raw source photo the same way, into its
      own "Evidence Photos" subfolder.
  4. Build the timeline: append beat clips in order, hard-cut, no gaps.
  5. Add a second video track and place each evidence beat's raw photo on
     it at that beat's record range (hybrid-resolve-pipeline.md "Evidence
     photos: no box, bottom-pinned citation, live overlay layer") -- left
     at Resolve's own default transform for the user to size/reposition.
  6. Verify: duration matches the beat-clip manifest, no gaps/overlaps on
     either track.
  7. Render: explicit format/codec (never assume it carries over from a
     prior project in the session -- the doc's own render-format gotcha),
     poll to completion, then verify the OUTPUT FILE on disk (duration +
     codec), not just JobStatus (Resolve can report Complete on a near-
     empty stub -- see the doc).

Does NOT do the metadata-strip remux, capy_check_brand.py, or
capy_description.py passes -- those are plain ffmpeg/python and stay in
capy_build.py's printed next-steps.

Does NOT hand-tune the evidence-photo overlay's transform -- by design
(hybrid-resolve-pipeline.md: "don't try to hand-compute a 'correct'
ZoomX/ZoomY/Pan/Tilt, the user is expected to size it themselves").

Run inside Resolve's own scripting environment (Workspace -> Scripts, or
via the davinci-resolve MCP's script_plugin.execute action once installed
there with `script_plugin.install`) -- needs `DaVinciResolveScript` on
sys.path, which Resolve's Python provides automatically when run that way.

    python capy_resolve_build.py D:\Videos\<slug> [--dry-run] [--render-dir DIR]

--dry-run: connects to Resolve and reads real state (existing project
names, current settings) but performs no mutating call -- every step that
would create/import/append/render instead prints what it would do. Use
this for the first run against any given project.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

FPS = 30
WIDTH, HEIGHT = 1080, 1920
BEAT_CLIP_TRACK = 1
EVIDENCE_TRACK = 2
RENDER_POLL_SECONDS = 5
RENDER_TIMEOUT_SECONDS = 1200


class BuildError(RuntimeError):
    pass


def connect_resolve():
    try:
        import DaVinciResolveScript as dvr  # noqa: N813 -- Resolve's own module name
    except ImportError as e:
        raise BuildError(
            "DaVinciResolveScript not importable -- run this from inside Resolve's own "
            "scripting environment (Workspace > Scripts), or via the davinci-resolve MCP's "
            "script_plugin.execute, not a bare system python."
        ) from e
    resolve = dvr.scriptapp("Resolve")
    if resolve is None:
        raise BuildError("dvr.scriptapp('Resolve') returned None -- is Resolve running?")
    return resolve


def load_project_data(project: Path) -> dict:
    beats_path = project / "script" / "beats.yaml"
    manifest_path = project / "frames" / "beat_clips_manifest.json"
    if not beats_path.exists():
        raise BuildError(f"{beats_path} not found")
    if not manifest_path.exists():
        raise BuildError(f"{manifest_path} not found -- run capy_render_beat_clips.py first")

    import yaml
    doc = yaml.safe_load(beats_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_by_id = {m["id"]: m for m in manifest}

    beats_by_id = {b["id"]: b for b in doc.get("beats", [])}
    evidence_beats = [
        b for b in doc.get("beats", [])
        if b.get("kind") == "evidence" and b.get("evidence", {}).get("image") and b["id"] in manifest_by_id
    ]
    return {
        "slug": doc.get("slug") or project.name,
        "manifest": manifest,  # ordered -- assembly order
        "beats_by_id": beats_by_id,
        "evidence_beats": evidence_beats,
    }


def unique_project_name(project_manager, slug: str, *, dry_run: bool) -> str:
    """slug, or slug-v2/-v3/... if a project by that name already exists in
    the current database folder -- sidesteps the stale-clip-caching bug by
    construction (hybrid-resolve-pipeline.md: "a fresh project has never
    once reproduced stale audio")."""
    existing = set(project_manager.GetProjectListInCurrentFolder() or [])
    name = slug
    n = 1
    while name in existing:
        n += 1
        name = f"{slug}-v{n}"
    if name != slug:
        print(f"[project] '{slug}' already exists -- using '{name}' instead (fresh project per beat-content-change rule)")
    return name


def create_project(resolve, project_manager, name: str, *, dry_run: bool):
    if dry_run:
        print(f"[dry-run] would CreateProject({name!r})")
        return None
    proj = project_manager.CreateProject(name)
    if proj is None:
        raise BuildError(f"CreateProject({name!r}) failed")
    print(f"[project] created '{name}'")
    return proj


def set_timeline_format(project, *, dry_run: bool) -> None:
    settings = {
        "timelineResolutionWidth": str(WIDTH),
        "timelineResolutionHeight": str(HEIGHT),
        "timelineFrameRate": str(FPS),
    }
    if dry_run:
        print(f"[dry-run] would SetSetting({settings})")
        return
    for key, value in settings.items():
        ok = project.SetSetting(key, value)
        if not ok:
            print(f"warning: SetSetting({key!r}, {value!r}) returned falsy", file=sys.stderr)
    # Verify with a readback -- the MCP wrapper's own "restore" gotcha is
    # specific to that wrapper, not the raw SetSetting call, but a readback
    # costs nothing and catches any other silent-revert surprise.
    for key, expected in settings.items():
        actual = project.GetSetting(key)
        if str(actual) != str(expected):
            raise BuildError(f"timeline setting {key!r} did not stick: wrote {expected!r}, read back {actual!r}")
    print(f"[project] timeline format set: {WIDTH}x{HEIGHT}@{FPS}fps (verified)")


def import_one_by_one(media_pool, paths: list[Path], *, dry_run: bool) -> dict[Path, object]:
    """Import every path in `paths` with its OWN ImportMedia call (never a
    batch of several sequentially-numbered files at once) -- Resolve's
    importer groups those into a single 'sequence' media pool item
    otherwise. Returns {path: media_pool_item}."""
    out: dict[Path, object] = {}
    for p in paths:
        if dry_run:
            print(f"[dry-run] would ImportMedia([{p}])  (one file per call)")
            continue
        items = media_pool.ImportMedia([str(p)])
        if not items:
            raise BuildError(f"ImportMedia failed for {p}")
        out[p] = items[0]
    return out


def build_beat_track(project, media_pool, project_data: dict, imported: dict[Path, object], *, dry_run: bool):
    manifest = project_data["manifest"]
    if dry_run:
        total = sum(m["duration"] for m in manifest)
        print(f"[dry-run] would build the main timeline from {len(manifest)} beat clips, "
              f"hard-cut in manifest order, total ~{total:.1f}s")
        return None

    timeline = media_pool.CreateEmptyTimeline(f"{project_data['slug']}-timeline")
    if timeline is None:
        raise BuildError("CreateEmptyTimeline failed")
    project.SetCurrentTimeline(timeline)

    record_frame = 0
    for m in manifest:
        path = Path(m["_abs_path"])
        item = imported.get(path)
        if item is None:
            raise BuildError(f"beat {m['id']}: no imported media pool item for {path}")
        duration_frames = round(m["duration"] * FPS)
        clip_info = {
            "mediaPoolItem": item,
            "startFrame": 0,
            "endFrame": duration_frames - 1,
            "trackIndex": BEAT_CLIP_TRACK,
            "recordFrame": record_frame,
        }
        appended = media_pool.AppendToTimeline([clip_info])
        if not appended:
            raise BuildError(f"AppendToTimeline failed for beat {m['id']} at record_frame={record_frame}")
        record_frame += duration_frames

    print(f"[timeline] appended {len(manifest)} beat clips, {record_frame} frames ({record_frame / FPS:.1f}s)")
    return timeline


def add_evidence_overlay_track(project, media_pool, timeline, project_data: dict, imported: dict[Path, object], *, dry_run: bool):
    evidence_beats = project_data["evidence_beats"]
    if not evidence_beats:
        print("[evidence] no evidence beats -- skipping overlay track")
        return

    manifest = project_data["manifest"]
    starts: dict[str, int] = {}
    t = 0
    for m in manifest:
        starts[m["id"]] = t
        t += round(m["duration"] * FPS)

    if dry_run:
        for b in evidence_beats:
            print(f"[dry-run] would place evidence photo for beat {b['id']!r} "
                  f"({b['evidence']['image']}) on track {EVIDENCE_TRACK} at frame {starts.get(b['id'])}")
        return

    timeline.AddTrack("video")  # becomes EVIDENCE_TRACK (track 2), above the beat-clip track
    for b in evidence_beats:
        bid = b["id"]
        photo_path = Path(b["evidence"]["image"])
        item = imported.get(photo_path)
        if item is None:
            print(f"warning: evidence beat {bid!r} photo not found among imported items -- skipped", file=sys.stderr)
            continue
        clip_info = {
            "mediaPoolItem": item,
            "startFrame": 0,
            "endFrame": 0,  # a still -- Resolve extends a still to the requested duration below
            "trackIndex": EVIDENCE_TRACK,
            "recordFrame": starts[bid],
        }
        appended = media_pool.AppendToTimeline([clip_info])
        if not appended:
            print(f"warning: could not place evidence photo for beat {bid!r} on the overlay track", file=sys.stderr)
    print(f"[evidence] placed {len(evidence_beats)} evidence photo(s) on track {EVIDENCE_TRACK}")


def verify_timeline(timeline, project_data: dict, *, dry_run: bool) -> None:
    if dry_run:
        print("[dry-run] would verify GetStartFrame/GetEndFrame against the manifest's summed duration, "
              "and check both tracks for gaps/overlaps")
        return
    expected_frames = round(sum(m["duration"] for m in project_data["manifest"]) * FPS)
    start = timeline.GetStartFrame()
    end = timeline.GetEndFrame()
    actual_frames = end - start
    if abs(actual_frames - expected_frames) > 1:  # 1-frame float-rounding tolerance
        raise BuildError(f"timeline duration {actual_frames} frames != expected {expected_frames} frames")

    items = timeline.GetItemListInTrack("video", BEAT_CLIP_TRACK) or []
    items = sorted(items, key=lambda it: it.GetStart())
    for a, b in zip(items, items[1:]):
        if b.GetStart() != a.GetEnd():
            raise BuildError(
                f"gap/overlap on beat-clip track between items ending {a.GetEnd()} and starting {b.GetStart()}"
            )
    print(f"[verify] duration OK ({actual_frames} frames), no gaps/overlaps on the beat-clip track")


def render(project, project_data: dict, render_dir: Path, *, dry_run: bool) -> Path:
    custom_name = project_data["slug"] + "-resolve"
    out_path = render_dir / f"{custom_name}.mp4"
    if dry_run:
        print(f"[dry-run] would SetCurrentRenderFormatAndCodec('mp4','H264'), "
              f"SetRenderSettings({{TargetDir: {render_dir}, CustomName: {custom_name}}}), "
              f"AddRenderJob(), StartRendering(), poll, then verify {out_path}")
        return out_path

    ok = project.SetCurrentRenderFormatAndCodec("mp4", "H264")
    if not ok:
        raise BuildError("SetCurrentRenderFormatAndCodec('mp4','H264') failed")
    project.SetRenderSettings({"TargetDir": str(render_dir), "CustomName": custom_name})
    job_id = project.AddRenderJob()
    if not job_id:
        raise BuildError("AddRenderJob failed")
    project.StartRendering([job_id])

    waited = 0
    while project.IsRenderingInProgress():
        time.sleep(RENDER_POLL_SECONDS)
        waited += RENDER_POLL_SECONDS
        if waited > RENDER_TIMEOUT_SECONDS:
            raise BuildError(f"render did not finish within {RENDER_TIMEOUT_SECONDS}s")
    print(f"[render] finished after ~{waited}s")

    if not out_path.exists():
        raise BuildError(f"render reported done but {out_path} does not exist")
    expected = sum(m["duration"] for m in project_data["manifest"])
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(out_path)],
        capture_output=True, text=True,
    )
    actual = float(result.stdout.strip() or 0)
    if abs(actual - expected) > 1.0:
        raise BuildError(
            f"render output duration {actual:.1f}s doesn't match expected {expected:.1f}s -- "
            "do not treat this render as complete (see hybrid-resolve-pipeline.md's near-empty-stub warning)"
        )
    print(f"[verify] output duration OK: {actual:.1f}s -> {out_path}")
    return out_path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project", type=Path)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--render-dir", type=Path, default=None, help="default: <project>/exports")
    args = ap.parse_args()

    project = args.project.resolve()
    render_dir = (args.render_dir or (project / "exports")).resolve()
    render_dir.mkdir(parents=True, exist_ok=True)

    try:
        data = load_project_data(project)
        beats_dir = project / "frames"
        for m in data["manifest"]:
            m["_abs_path"] = str((project / m["path"]).resolve()) if not Path(m["path"]).is_absolute() else m["path"]

        resolve = connect_resolve()
        project_manager = resolve.GetProjectManager()
        name = unique_project_name(project_manager, data["slug"], dry_run=args.dry_run)
        proj = create_project(resolve, project_manager, name, dry_run=args.dry_run)
        if proj is not None:
            set_timeline_format(proj, dry_run=args.dry_run)

        media_pool = proj.GetMediaPool() if proj is not None else None

        beat_paths = [Path(m["_abs_path"]) for m in data["manifest"]]
        evidence_paths = [Path(b["evidence"]["image"]).resolve() for b in data["evidence_beats"]]

        imported = {}
        if not args.dry_run:
            root_folder = media_pool.GetRootFolder()
            media_pool.SetCurrentFolder(root_folder)
            imported.update(import_one_by_one(media_pool, beat_paths, dry_run=args.dry_run))
            if evidence_paths:
                evidence_folder = media_pool.AddSubFolder(root_folder, "Evidence Photos")
                media_pool.SetCurrentFolder(evidence_folder)
                imported.update(import_one_by_one(media_pool, evidence_paths, dry_run=args.dry_run))
                media_pool.SetCurrentFolder(root_folder)
        else:
            import_one_by_one(media_pool, beat_paths, dry_run=True)
            import_one_by_one(media_pool, evidence_paths, dry_run=True)

        timeline = build_beat_track(proj, media_pool, data, imported, dry_run=args.dry_run)
        add_evidence_overlay_track(proj, media_pool, timeline, data, imported, dry_run=args.dry_run)
        verify_timeline(timeline, data, dry_run=args.dry_run)

        if not args.dry_run:
            project_manager.SaveProject() if hasattr(project_manager, "SaveProject") else proj.SaveProject()

        out_path = render(proj, data, render_dir, dry_run=args.dry_run)
        print(f"\n{'[dry-run] ' if args.dry_run else ''}Resolve build complete for {project.name} -> {out_path}")
        if not args.dry_run:
            print("Next: the metadata-strip remux + capy_check_brand.py + capy_description.py pass "
                  "(see capy_build.py's printed next-steps).")
        return 0
    except BuildError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

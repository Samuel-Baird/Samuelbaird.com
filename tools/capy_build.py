#!/usr/bin/env python3
"""Run the whole post-Gate-A build chain for one Saint Capybara project in
one command, instead of four separate tool invocations run by hand.

    python tools/capy_build.py --project D:\\Videos\\<slug>
    python tools/capy_build.py --project D:\\Videos\\<slug> --only n03,n04
    python tools/capy_build.py --project D:\\Videos\\<slug> --force --clean-plates

Runs, in order, stopping at the first failure:
    1. capy_tts.py            -- narration audio (skips already-rendered beats
                                  whose resolved voice spec hasn't changed --
                                  see capy_tts.py's own audio/<id>.meta.json check)
    2. capy_beat_plates.py    -- one chrome plate PNG per beat
    3. capy_caption_cards.py  -- one caption phrase PNG per caption window
    4. capy_render_beat_clips.py -- one self-contained MP4 per beat

Each step is a real subprocess call to the existing tool (not an in-process
import) -- this script is a thin sequencer, not a reimplementation, so a
change to any one tool's behavior doesn't need a matching change here.

After all four succeed, prints the exact commands still needed for the two
manual stages this script does NOT do (docs/saint-capybara/
hybrid-resolve-pipeline.md has the full checklist for both):
    - The Resolve build + render (via the davinci-resolve MCP, or
      tools/capy_resolve_build.py -- see that script's own docstring for
      what it automates and what it still can't).
    - The metadata-strip remux + capy_check_brand.py --mp4 + capy_description.py
      pass, once the Resolve render is on disk.

`--only id,id`: forwarded to every step that supports it (all four).
`--force`: forwarded to capy_tts.py only (re-render every beat's audio
  even if unchanged) -- the other three tools always regenerate everything
  they touch since they're cheap PNG/ffmpeg passes, not model inference.
`--clean-plates`: forwarded to capy_beat_plates.py's --clean (delete stale
  frames/plate_*.png and frames/beat_*.mp4 before re-rendering) -- use this
  after a layout/theme change so no stale plate survives under an
  unchanged filename.
`--skip {tts,plates,captions,clips}` (repeatable): skip a step, e.g. to
  resume a build that already got partway through, or to re-run only the
  caption/clip steps after a caption-layout tweak that doesn't need new
  audio or plates.
`--dry-run`: print the commands that would run, without running them.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
STEPS = ["tts", "plates", "captions", "clips"]


def build_commands(project: Path, *, only: str | None, force: bool, clean_plates: bool) -> dict[str, list[str]]:
    py = sys.executable
    cmds: dict[str, list[str]] = {}

    tts_cmd = [py, str(TOOLS_DIR / "capy_tts.py"), "--project", str(project)]
    if only:
        tts_cmd += ["--only", only]
    if force:
        tts_cmd += ["--force"]
    cmds["tts"] = tts_cmd

    plates_cmd = [py, str(TOOLS_DIR / "capy_beat_plates.py"), "--project", str(project)]
    if only:
        plates_cmd += ["--only", only]
    if clean_plates:
        plates_cmd += ["--clean"]
    cmds["plates"] = plates_cmd

    captions_cmd = [py, str(TOOLS_DIR / "capy_caption_cards.py"), "--project", str(project)]
    if only:
        captions_cmd += ["--only", only]
    cmds["captions"] = captions_cmd

    clips_cmd = [py, str(TOOLS_DIR / "capy_render_beat_clips.py"), "--project", str(project)]
    if only:
        clips_cmd += ["--only", only]
    cmds["clips"] = clips_cmd

    return cmds


def run_step(name: str, cmd: list[str]) -> tuple[bool, float]:
    print(f"\n{'=' * 70}\n[{name}] {' '.join(str(c) for c in cmd)}\n{'=' * 70}", flush=True)
    t0 = time.monotonic()
    result = subprocess.run(cmd)
    dt = time.monotonic() - t0
    ok = result.returncode == 0
    status = "OK" if ok else f"FAILED (exit {result.returncode})"
    print(f"[{name}] {status} in {dt:.1f}s")
    return ok, dt


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--only", type=str, default=None, help="comma-separated beat ids, forwarded to every step")
    ap.add_argument("--force", action="store_true", help="forwarded to capy_tts.py: re-render every beat's audio")
    ap.add_argument("--clean-plates", action="store_true", help="forwarded to capy_beat_plates.py --clean")
    ap.add_argument("--skip", action="append", choices=STEPS, default=[], help="skip a step (repeatable)")
    ap.add_argument("--dry-run", action="store_true", help="print commands without running them")
    args = ap.parse_args()

    project = args.project.resolve()
    if not (project / "script" / "beats.yaml").exists():
        print(f"error: {project} has no script/beats.yaml -- is this a Saint Capybara project directory?", file=sys.stderr)
        return 2

    cmds = build_commands(project, only=args.only, force=args.force, clean_plates=args.clean_plates)
    skip = set(args.skip)
    to_run = [s for s in STEPS if s not in skip]

    if args.dry_run:
        print(f"Would run {len(to_run)} step(s) for {project}:")
        for s in to_run:
            print(f"  [{s}] {' '.join(str(c) for c in cmds[s])}")
        return 0

    print(f"Building {project.name} -- {len(to_run)} step(s): {', '.join(to_run)}")
    t_start = time.monotonic()
    durations: dict[str, float] = {}
    for step in to_run:
        ok, dt = run_step(step, cmds[step])
        durations[step] = dt
        if not ok:
            print(f"\nBuild stopped at [{step}] after {time.monotonic() - t_start:.1f}s total. "
                  f"Fix the error above, then re-run with --skip for the steps that already "
                  f"succeeded ({', '.join(s for s in to_run if s != step and durations.get(s) is not None)}).",
                  file=sys.stderr)
            return 1

    total = time.monotonic() - t_start
    print(f"\n{'=' * 70}\nAll {len(to_run)} step(s) complete in {total:.1f}s.")
    for s in to_run:
        print(f"  {s:10s} {durations[s]:.1f}s")

    print(f"""
Next (not automated by this script -- see docs/saint-capybara/hybrid-resolve-pipeline.md):

1. Resolve build + render. Either drive the davinci-resolve MCP by hand
   following the checklist in hybrid-resolve-pipeline.md, or run:
       python tools/capy_resolve_build.py --project "{project}"
   (see that script's docstring -- it still needs a human to confirm the
   render and to size/position the evidence-photo overlay track, if any).

2. Metadata-strip remux, once Resolve's own render is on disk:
       ffmpeg -i "{project / 'exports' / (project.name + '-resolve.mp4')}" -c copy -map_metadata -1 -fflags +bitexact -metadata title="<video title>" "{project / 'exports' / (project.name + '.mp4')}"

3. Brand + QC:
       python tools/capy_check_brand.py --project "{project}" --mp4 "{project / 'exports' / (project.name + '.mp4')}"
       python tools/capy_description.py --project "{project}"
       python tools/capy_qc.py --project "{project}"
""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

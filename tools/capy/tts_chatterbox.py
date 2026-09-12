"""Chatterbox TTS engine wrapper -- invokes tools/.venv-chatterbox as a
SUBPROCESS running tools/capy/_chatterbox_worker.py. Never imports
chatterbox in this (the caller's) process: chatterbox-tts's dependency
stack conflicts with the pinned Kokoro/Whisper versions the rest of this
repo's tools run against (see tools/requirements-chatterbox.txt for the
full story). This mirrors the existing pattern in tools/transcribe.py,
which already shells out to a separate `whisper` CLI process rather than
importing it in-process, for the same process-isolation reason.

    from capy.tts_chatterbox import render_batch

    results = render_batch([
        {"id": "n01", "text": "...", "ref": Path(...), "out_path": Path(...),
         "exaggeration": 0.5, "cfg_weight": 0.5},
        ...
    ])
    # -> {"n01": {"ok": True, "duration": 4.23, "sample_rate": 24000}, ...}

One subprocess call renders every job in the batch (the model loads
once inside the worker and is reused for all of them), so callers
should collect every beat needing Chatterbox in one project run and
call this once, not once per beat.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
VENV_PYTHON = REPO_ROOT / "tools" / ".venv-chatterbox" / "Scripts" / "python.exe"
WORKER_SCRIPT = Path(__file__).resolve().parent / "_chatterbox_worker.py"

SETUP_HINT = (
    "Chatterbox's isolated virtualenv wasn't found at "
    f"{VENV_PYTHON}. Set it up with:\n"
    "  cd tools\n"
    "  python -m venv .venv-chatterbox\n"
    "  .venv-chatterbox\\Scripts\\python.exe -m pip install --upgrade pip\n"
    "  .venv-chatterbox\\Scripts\\python.exe -m pip install -r requirements-chatterbox.txt\n"
    "See tools/requirements-chatterbox.txt for why this needs its own venv."
)


class ChatterboxUnavailable(RuntimeError):
    pass


def render_batch(jobs: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Render every job in one Chatterbox worker subprocess invocation.
    Each job dict needs: id, text, ref (Path or str), out_path (Path or
    str), and optionally exaggeration/cfg_weight (default 0.5/0.5).
    Returns {job_id: {"ok": bool, "duration": float, ...} | {"ok": False, "error": str}}.
    Raises ChatterboxUnavailable if the venv/worker script are missing, or
    if the worker process itself fails to run at all (as opposed to an
    individual job failing, which is reported per-job in the return
    value, not raised)."""
    if not jobs:
        return {}
    if not VENV_PYTHON.exists():
        raise ChatterboxUnavailable(SETUP_HINT)
    if not WORKER_SCRIPT.exists():
        raise ChatterboxUnavailable(f"worker script missing: {WORKER_SCRIPT}")

    job_payload = [
        {
            "id": j["id"],
            "text": j["text"],
            "ref": str(Path(j["ref"]).resolve()),
            "out_path": str(Path(j["out_path"]).resolve()),
            "exaggeration": j.get("exaggeration", 0.5),
            "cfg_weight": j.get("cfg_weight", 0.5),
        }
        for j in jobs
    ]

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(job_payload, f)
        job_file = Path(f.name)

    try:
        proc = subprocess.run(
            [str(VENV_PYTHON), str(WORKER_SCRIPT), str(job_file)],
            capture_output=True, text=True,
        )
        # The worker prints human-readable progress to stderr as it goes
        # (useful in a long batch) and the JSON result as the LAST stdout
        # line -- surface the progress either way, even on failure.
        if proc.stderr:
            print(proc.stderr, file=sys.stderr, end="" if proc.stderr.endswith("\n") else "\n")

        if proc.returncode != 0:
            raise ChatterboxUnavailable(
                f"chatterbox worker process exited with code {proc.returncode} "
                f"(fatal -- likely a model-load failure, see stderr above; "
                f"none of this batch's {len(jobs)} job(s) were rendered)"
            )

        last_line = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else ""
        try:
            results = json.loads(last_line)
        except json.JSONDecodeError as e:
            raise ChatterboxUnavailable(f"could not parse chatterbox worker output as JSON: {e}\nstdout was:\n{proc.stdout}") from e

        return {r["id"]: r for r in results}
    finally:
        job_file.unlink(missing_ok=True)

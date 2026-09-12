#!/usr/bin/env python3
"""Chatterbox TTS batch worker -- runs INSIDE tools/.venv-chatterbox.

Never imported by the main tool process (capy_tts.py runs in the
repo's shared/global Python, where chatterbox-tts's dependency stack
would conflict with the pinned Kokoro/Whisper versions -- see
tools/requirements-chatterbox.txt). capy_tts.py instead invokes this
script as a subprocess with `.venv-chatterbox`'s python, passing one
job-batch JSON file and getting one result JSON back on stdout. The
model is loaded exactly once per invocation and reused for every job in
the batch, however many beats need it.

Job file schema (a JSON list, read from argv[1]):
    [
      {"id": "n01", "text": "...", "ref": "C:\\...\\host_andrew_kennedy.wav",
       "out_path": "C:\\...\\audio\\n01.wav",
       "exaggeration": 0.5, "cfg_weight": 0.5},
      ...
    ]

Result (a JSON list, written to stdout as the LAST line -- everything
before it is human-readable progress logging to stderr):
    [
      {"id": "n01", "ok": true, "duration": 4.23},
      {"id": "n02", "ok": false, "error": "..."},
      ...
    ]

Exit code is 0 even if individual jobs fail (failures are reported per
job in the result list) -- a non-zero exit means the whole batch could
not run at all (e.g. model failed to load), which the caller should
treat as fatal for every job in the batch.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: _chatterbox_worker.py <job_batch.json>", file=sys.stderr)
        return 2

    job_path = Path(sys.argv[1])
    jobs = json.loads(job_path.read_text(encoding="utf-8"))

    print(f"[chatterbox_worker] loading model (CPU)...", file=sys.stderr)
    t0 = time.time()
    try:
        import torchaudio as ta
        from chatterbox.tts import ChatterboxTTS
        model = ChatterboxTTS.from_pretrained(device="cpu")
    except Exception as e:  # model failed to load -- fatal for the whole batch
        print(f"[chatterbox_worker] FATAL: model load failed: {e}", file=sys.stderr)
        return 1
    print(f"[chatterbox_worker] model loaded in {time.time()-t0:.1f}s, {len(jobs)} job(s) to render", file=sys.stderr)

    results = []
    for job in jobs:
        jid = job["id"]
        t0 = time.time()
        try:
            wav = model.generate(
                job["text"],
                audio_prompt_path=job["ref"],
                exaggeration=job.get("exaggeration", 0.5),
                cfg_weight=job.get("cfg_weight", 0.5),
            )
            out_path = Path(job["out_path"])
            out_path.parent.mkdir(parents=True, exist_ok=True)
            ta.save(str(out_path), wav, model.sr)
            duration = wav.shape[-1] / model.sr
            dt = time.time() - t0
            print(f"[chatterbox_worker] {jid}: {duration:.2f}s audio, rendered in {dt:.1f}s -> {out_path}", file=sys.stderr)
            results.append({"id": jid, "ok": True, "duration": duration, "sample_rate": model.sr})
        except Exception as e:
            print(f"[chatterbox_worker] {jid}: FAILED: {e}", file=sys.stderr)
            results.append({"id": jid, "ok": False, "error": str(e)})

    print(json.dumps(results))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

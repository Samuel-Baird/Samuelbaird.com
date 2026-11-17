"""Transcribe each take's mic with faster-whisper (word timestamps), twice:

1. a clean pass (VAD on) -> work/transcripts/take<k>.json + .txt: what was said, used for
   slide cues, highlight picking and captions;
2. a "disfluent" pass over the same audio with a prompt full of ums, so Whisper writes the
   fillers out -> work/transcripts/take<k>.fillers.json. Whisper drops ums by default; this pass
   is only a list of *candidates* -- shorts.py confirms each one in the audio before cutting.

Also writes the 16 kHz mono copy (work/audio/take<k>_16k.wav) the cut logic reads levels from.

    python tools/presentation/transcribe.py D:\\Videos\\<slug> [--model medium.en] [--takes 1,2]

CPU only on this machine: medium.en runs at roughly 1x real time per pass. small.en is faster
but mis-hears more names; the captions get a fix-up list either way (project.json
"caption_fixes").
"""
from __future__ import annotations

import argparse
import json
import subprocess

from faster_whisper import WhisperModel

from common import FF, Project

DISFLUENT_PROMPT = "Umm, so, uh, I think, um, you know, like... uh, the, um, data here is, uh, pretty interesting."


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('project')
    ap.add_argument('--model', default='medium.en')
    ap.add_argument('--takes', default='')
    a = ap.parse_args()
    pr = Project(a.project)
    m = WhisperModel(a.model, device='cpu', compute_type='int8', cpu_threads=16)
    takes = a.takes.split(',') if a.takes else list(pr.cfg['takes'])
    (pr.work / 'transcripts').mkdir(parents=True, exist_ok=True)
    for k in takes:
        wav = pr.wav16k(k)
        wav.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([FF, '-v', 'error', '-y', '-i', pr.mic(k), '-ac', '1', '-ar', '16000', '-c:a', 'pcm_s16le', wav],
                       check=True)
        segs, _ = m.transcribe(str(wav), language='en', word_timestamps=True, vad_filter=True, beam_size=5)
        out = [{'start': s.start, 'end': s.end, 'text': s.text,
                'words': [(w.start, w.end, w.word) for w in s.words]} for s in segs]
        (pr.work / f'transcripts/take{k}.json').write_text(json.dumps(out), encoding='utf-8')
        (pr.work / f'transcripts/take{k}.txt').write_text(
            ''.join(f"[{s['start']:7.2f}-{s['end']:7.2f}] {s['text'].strip()}\n" for s in out), encoding='utf-8')
        print(f'take {k}: {len(out)} segments', flush=True)
        segs, _ = m.transcribe(str(wav), language='en', word_timestamps=True, initial_prompt=DISFLUENT_PROMPT,
                               vad_filter=False, beam_size=5, condition_on_previous_text=False)
        words = [(w.start, w.end, w.word.strip()) for s in segs for w in s.words]
        (pr.work / f'transcripts/take{k}.fillers.json').write_text(json.dumps(words), encoding='utf-8')
        print(f'take {k}: disfluent pass, {sum(1 for *_, w in words if w.lower().strip(",.?!") in ("um", "uh"))} '
              f'um/uh candidates', flush=True)


if __name__ == '__main__':
    main()

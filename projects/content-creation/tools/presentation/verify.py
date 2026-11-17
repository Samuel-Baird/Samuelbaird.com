"""Word-loss check for built shorts: re-transcribe each output and diff it against the take's
own transcript over the kept ranges (fillers excluded). Every reported gap needs a listen:
most are the checker mis-hearing ("1870" vs "1870s", "U S" vs "US"), but a real one means a
trim clipped a word -- fix the cut rule or the range and rebuild.

    python tools/presentation/verify.py D:\\Videos\\<slug> [names|all]
"""
from __future__ import annotations

import difflib
import re
import subprocess
import sys

from faster_whisper import WhisperModel

from common import FF, FILLERS, Project
from shorts import Short, norm


def main() -> None:
    pr = Project(sys.argv[1])
    names = list(pr.cfg['shorts']) if len(sys.argv) < 3 or sys.argv[2] == 'all' else sys.argv[2].split(',')
    m = WhisperModel('small.en', device='cpu', compute_type='int8', cpu_threads=16)
    for name in names:
        sh = Short(pr, name)
        out = pr.p(pr.cfg.get('shorts_dir', 'exports/shorts')) / (re.sub(r'[\\/:*?"<>|]', '', sh.cfg['title']) + '.mp4')
        wav = pr.work / 'shorts' / name / 'check.wav'
        subprocess.run([FF, '-v', 'error', '-y', '-i', out, '-ac', '1', '-ar', '16000', wav], check=True)
        got = [norm(w.word) for s in m.transcribe(str(wav), language='en', word_timestamps=True)[0] for w in s.words]
        exp = [norm(w) for g in pr.words(sh.take) for (s, e, w) in g['words']
               if any(a <= (s + e) / 2 <= b for a, b in sh.rng)]
        exp = [w for w in exp if w and w not in FILLERS]
        got = [w for w in got if w and w not in FILLERS]
        sm = difflib.SequenceMatcher(a=exp, b=got, autojunk=False)
        print(f'## {name}: {len(exp)} words expected, match {sm.ratio():.3f}')
        for op, a0, a1, b0, b1 in sm.get_opcodes():
            if op in ('delete', 'replace'):
                print(f"   ...{' '.join(exp[max(0, a0 - 3):a0])} [{' '.join(exp[a0:a1])}] -> [{' '.join(got[b0:b1])}]")


if __name__ == '__main__':
    main()

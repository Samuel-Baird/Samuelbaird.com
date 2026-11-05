"""Vertical shorts from a multicam interview: the presentation shorts engine
(tools/presentation/shorts.py -- tight trims, um removal, brand captions, hook card, photo plates)
with the camera chosen by who is talking instead of alternating two angles.

    python tools/interview/interview_shorts.py D:\\Videos\\<slug> <name>|all [--plan] [--force]

Same project.json "shorts" entries as the presentation type. Needs, besides the interview keys
build.py uses, two virtual cameras for the wide shot framed on each person (same file and offset
as the wide camera, own face position):

    takes.<k>.cameras.Bh / Bg: {"file": <wide>, "offset": <wide offset>, "face": [x, y]}
    interview.short_cams: {"host": ["A", "Bh"], "guest": ["C", "Bg"]}   (close, side), optional

Each angle change goes to the talker: alternately their close camera and the wide camera cropped
on them (zoomed ~1.6x, so it reads as a second angle). A shot that runs across a change of talker
is split there when both sides last >= 2 s, otherwise it goes to whoever talks most in it.
Audio is the interview auto-mix (build.py), not the recorder's stereo mix.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'presentation'))
sys.path.insert(0, str(HERE))
import shorts as S  # noqa: E402  (presentation engine)
import build  # noqa: E402
from common import FPF, Project  # noqa: E402

CLOSE_LOOKS = [(1.00, 1.08), (1.10, 1.02)]
SIDE_LOOKS = [(1.55, 1.66), (1.70, 1.60)]
MIN_SIDE = round(2.0 / FPF)


class InterviewShort(S.Short):
    def __init__(self, pr: Project, name: str, edit: build.Edit):
        self.edit = edit
        super().__init__(pr, name)

    def plan(self):
        super().plan()
        e = self.edit
        cams = self.pr.cfg['interview'].get('short_cams', {'host': ['A', 'Bh'], 'guest': ['C', 'Bg']})

        def talker(m0, n):
            lab = list(e.lab[int(m0 / build.HOP):int((m0 + n * FPF) / build.HOP) + 1])
            return max(('host', 'guest'), key=lab.count)

        # 1. split camera shots where the talker changes
        out = []
        for s in self.shots:
            if s['gfx'] is not None:
                out.append(s)
                continue
            cuts = []
            for t0, t1, w in e.turns:
                b = t0 - 0.15
                if s['m0'] < b < s['m0'] + s['n'] * FPF:
                    k = round((b - s['m0']) / FPF)
                    if MIN_SIDE <= k <= s['n'] - MIN_SIDE and (not cuts or k - cuts[-1] >= MIN_SIDE):
                        cuts.append(k)
            prev = 0
            for k in cuts + [s['n']]:
                out.append(dict(s, m0=s['m0'] + prev * FPF, n=k - prev, f0=s['f0'] + prev, soft=s['soft'] and prev == 0))
                prev = k
        # 2. cameras: each new angle goes to the talker, alternating close / side crop
        turn = {'host': 0, 'guest': 0}
        last = None
        for s in out:
            if s['gfx'] is not None:
                last = None
                continue
            if s['soft'] and last is not None:
                s['cam'], s['look'] = last['cam'], last['look']
            else:
                who = talker(s['m0'], s['n'])
                i = turn[who]
                if last is not None and last['who'] == who and i % 2 == 0 and last['cam'] == cams[who][0]:
                    i += 1   # never the same angle twice in a row
                s['cam'] = cams[who][i % 2]
                s['look'] = (CLOSE_LOOKS if i % 2 == 0 else SIDE_LOOKS)[(i // 2) % 2]
                turn[who] = i + 1
                s['who'] = who
            s.setdefault('who', last['who'] if last else 'guest')
            last = s
        # 3. zoom runs (a soft-joined run keeps one continuous move) and dissolve sources
        run_ = []
        for s in out + [dict(gfx='END', soft=False)]:
            if s['gfx'] is None and s['soft'] and run_:
                run_.append(s)
                continue
            o, L = 0, sum(r['n'] for r in run_)
            for r in run_:
                r['zo'], r['zL'] = o, L
                o += r['n']
            run_ = [s] if s['gfx'] is None else []
        for i, s in enumerate(out):
            s['prev'] = out[i - 1] if s.get('soft') and i else None
        self.shots = out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('project')
    ap.add_argument('names')
    ap.add_argument('--plan', action='store_true')
    ap.add_argument('--force', action='store_true')
    a = ap.parse_args()
    pr = Project(a.project)
    edit = build.Edit(pr)
    mix = edit.automix()
    pr.mic = lambda k: mix   # trims, silences and the voice master all read the auto-mix
    names = list(pr.cfg['shorts']) if a.names == 'all' else a.names.split(',')
    for n in names:
        sh = InterviewShort(pr, n, edit)
        print(f"{n}: {sh.nf * FPF:.1f}s, {len(sh.shots)} shots, trims {len(sh.taken)} "
              f"(ums {sum(1 for t in sh.taken if t[2] == 'um')})", flush=True)
        if a.plan:
            for i, s in enumerate(sh.shots):
                what = (s['gfx'].get('label') or Path(str(s['gfx']['image'])).name) if s['gfx'] else \
                    f"{s['cam']} {s['look']}{' (dissolve in)' if s['soft'] else ''}"
                print(f'  {i:2d} {s["f0"] * FPF:6.1f}s {s["n"] * FPF:5.1f}s  {what}')
            print('  captions:', ' '.join(w for *_, w in sh.caption_words()))
            continue
        print('done', sh.build(a.force), flush=True)


if __name__ == '__main__':
    main()

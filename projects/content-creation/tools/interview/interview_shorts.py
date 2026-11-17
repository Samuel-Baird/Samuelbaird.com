"""Vertical shorts from a multicam interview: the presentation shorts engine
(tools/presentation/shorts.py -- tight trims, um removal, brand captions, hook card, photo plates)
with the camera chosen by who is talking instead of alternating two angles.

    python tools/interview/interview_shorts.py D:\\Videos\\<slug> <name>|all [--plan] [--force]

Same project.json "shorts" entries as the presentation type. Needs, besides the interview keys
build.py uses, two virtual cameras for the wide shot framed on each person (same file and offset
as the wide camera, own face position):

    takes.<k>.cameras.Bh / Bg: {"file": <wide>, "offset": <wide offset>, "face": [x, y]}
    interview.short_cams: {"host": ["A", "Bh"], "guest": ["C", "Bg"]}   (close, side), optional

Angles change slowly: every angle holds at least HOLD (15 s) with one slow zoom across it, and
ums / long pauses inside a hold are removed behind a short dissolve on the same angle. A change goes
to whoever holds the floor for the next ~12 s (their close camera and the wide camera cropped on
them, alternately); a talker who runs past ~40 s gets their other angle once, cut on a trim. A
question shorter than the hold plays over the listener. Coming back from a graphic keeps the angle.
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

CLOSE_LOOKS = [(1.00, 1.08), (1.08, 1.00)]   # one slow push in / pull out over the whole hold
SIDE_LOOKS = [(1.55, 1.66), (1.66, 1.55)]
HOLD = 15.0        # s an angle holds before any change of angle (user rule)
VARIETY = 40.0     # one talker longer than this gets a change to their other angle
LOOKAHEAD = 12.0   # s after a cut whose main talker the new angle goes to


class InterviewShort(S.Short):
    MIN_SHOT = MAX_SHOT = 1e9   # base plan: every trim is a soft dissolve, no forced splits

    def __init__(self, pr: Project, name: str, edit: build.Edit):
        self.edit = edit
        super().__init__(pr, name)

    def plan(self):
        super().plan()
        e = self.edit
        cams = self.pr.cfg['interview'].get('short_cams', {'host': ['A', 'Bh'], 'guest': ['C', 'Bg']})
        H, V, LA = (round(x / FPF) for x in (HOLD, VARIETY, LOOKAHEAD))
        shots = self.shots
        # who talks at each output frame (from the source time it shows)
        who = []
        for s in shots:
            for k in range(s['n']):
                i = int((s['m0'] + k * FPF) / build.HOP)
                who.append(e.lab[min(i, len(e.lab) - 1)])

        def main_talker(f0, f1):
            seg = who[f0:max(f1, f0 + 1)]
            return max(('host', 'guest'), key=seg.count)

        def out_frame(t):
            for s in shots:
                if s['gfx'] is None and s['m0'] <= t < s['m0'] + s['n'] * FPF:
                    return s['f0'] + round((t - s['m0']) / FPF)
            return None
        turn_f = {f for f in (out_frame(t0 - 0.15) for t0, _, _ in e.turns) if f is not None}
        pause_f = {f for f in (out_frame((a + b) / 2) for a, b in self.pr.silences(self.take) if b - a > 0.25)
                   if f is not None}
        # holds: runs of camera pieces between graphics (and the start / end)
        holds, cur = [], []
        for s in shots:
            if s['gfx'] is None:
                cur.append(s)
            else:
                if cur:
                    holds.append(cur)
                holds.append([s])
                cur = []
        if cur:
            holds.append(cur)
        out, last = [], None
        turn = {'host': 0, 'guest': 0}
        for h in holds:
            if h[0]['gfx'] is not None:
                out.append(h[0])
                continue
            F0, F1 = h[0]['f0'], h[-1]['f0'] + h[-1]['n']
            edges = {p['f0'] for p in h}
            joins = {p['f0'] for p in h if not p['soft']} - {F0}   # one range ends, the next begins
            # 1. cut points: an angle holds >= HOLD on both sides of every cut; cut where the
            #    floor changes hands (lands on a trim or a turn), else after VARIETY on one talker
            cuts, c = [], F0
            p_who = main_talker(F0, min(F1, F0 + 2 * LA))
            while F1 - c >= 2 * H:
                lo, hi = c + H, F1 - H
                cand = sorted(x for x in turn_f | edges | pause_f if lo <= x <= hi)
                nxt = next((x for x in cand if x in turn_f and main_talker(x, min(F1, x + LA)) != p_who), None)
                if nxt is None:   # a jump to another part of the conversation is a natural cut
                    nxt = next((x for x in cand if x in joins and x - c <= V), None)
                if nxt is None and F1 - c > V + H:   # long monologue: other angle, on a trim or pause
                    near = [x for x in cand if x in edges or x in pause_f]
                    target = c + min(V, (F1 - c) // 2)
                    nxt = min(near, key=lambda x: abs(x - target)) if near else None
                if nxt is None:
                    break
                cuts.append(nxt)
                c = nxt
                p_who = main_talker(c, min(F1, c + 2 * LA))
            bounds = [F0] + cuts + [F1]
            # 2. split the pieces at the cuts; a piece edge that is not a cut is a soft dissolve
            for a, b in zip(bounds, bounds[1:]):
                w = main_talker(a, b)
                if last is not None and last['who'] == w and a == F0 and out and out[-1]['gfx'] is not None:
                    cam, look = last['cam'], last['look']   # back from a graphic: same angle
                else:
                    i = turn[w]
                    if last is not None and last['who'] == w and cams[w][i % 2] == last['cam']:
                        i += 1
                    cam = cams[w][i % 2]
                    look = (CLOSE_LOOKS if i % 2 == 0 else SIDE_LOOKS)[(i // 2) % 2]
                    turn[w] = i + 1
                seg = []
                for p in h:
                    x0, x1 = max(a, p['f0']), min(b, p['f0'] + p['n'])
                    if x0 >= x1:
                        continue
                    seg.append(dict(p, m0=p['m0'] + (x0 - p['f0']) * FPF, n=x1 - x0, f0=x0,
                                    soft=bool(seg), cam=cam, look=look, who=w))
                L, o = sum(r['n'] for r in seg), 0
                for r in seg:
                    r['zo'], r['zL'] = o, L
                    o += r['n']
                out.extend(seg)
                last = seg[-1]
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

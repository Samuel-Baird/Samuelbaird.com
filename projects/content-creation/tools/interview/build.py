"""Long-form 1920x1080 edit of a multicam interview with ffmpeg (docs/types/interview.md):
speaker-follow camera cuts from the isolated mics, angle variety inside long answers, website /
image "slides" in the brand split layout (optionally scrolling), and an auto-mixed voice track.

    python tools/interview/build.py D:\\Videos\\<slug> --plan        # print the shot list
    python tools/interview/build.py D:\\Videos\\<slug> [--jobs 3]     # render

Uses the presentation pipeline's project.json, sync.py and transcribe output (camera_time =
mic_time + offset). Extra keys:

    takes.<k>.iso:       [host_mic, guest_mic]  isolated tracks (speaker detection + audio mix)
    interview.cams:      {"host": "A", "guest": "C", "wide": "B"}
    interview.wide_faces {"host": [x, y], "guest": [x, y]}   faces in the wide shot (4K fractions)
    longform.web:        [[from, to, "<slide stem>" | "scroll:<image stem>"], ...]  mic seconds
    longform.cuts:       [{start, end, why}]  spans removed (an angle change hides each one)
    longform.overrides:  [[from, to, "host"|"guest"|"wide"]]  force an angle

Speaker detection: 100 ms RMS of each iso mic; the louder mic (with a margin for bleed) is the
talker. Turns under ~1.5 s (backchannels) are absorbed. Pauses where both mics are quiet for
more than 1.5 s are shortened to ~0.6 s (style guide long-form pacing) and always land on an
angle change, so the trim is never a jump cut.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import wave
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'presentation'))
import brand  # noqa: E402
from common import FF, FPF, FPS, GRADE, SAMPLES_PER_FRAME, Project, blend_in, master_voice, run, x264, zoom  # noqa: E402
from longform import make_cards  # noqa: E402

TR = 10            # slide crossfade frames
HOP = 0.1          # speaker-detection resolution (s)
MIN_TURN = 2.5     # shorter turns are backchannels, absorbed
QUICK = 5.0        # turns shorter than this hold the two-shot
LONG_PAUSE = 1.5   # trim pauses longer than this ...
KEEP_PAUSE = 0.6   # ... down to this


# ---------------------------------------------------------------- analysis
def env100(path: Path, cache: Path) -> np.ndarray:
    if cache.exists():
        return np.load(cache)
    r = subprocess.run([FF, '-v', 'error', '-i', str(path), '-ac', '1', '-ar', '16000', '-f', 's16le', '-'],
                       capture_output=True, check=True)
    x = np.frombuffer(r.stdout, np.int16).astype(np.float32)
    n = len(x) // 1600
    e = 20 * np.log10(np.sqrt((x[:n * 1600].reshape(n, 1600) ** 2).mean(1)) + 1)
    np.save(cache, e)
    return e


def smooth(x, k):
    return np.convolve(x, np.ones(k) / k, mode='same')


def speakers(pr: Project, k: str):
    """per-100ms labels: 'host', 'guest' or '' (both quiet)"""
    iso = pr.take(k)['iso']
    a = env100(pr.p(iso[0]), pr.work / 'audio/env_host.npy')
    b = env100(pr.p(iso[1]), pr.work / 'audio/env_guest.npy')
    n = min(len(a), len(b))
    raw = np.maximum(a[:n], b[:n])
    a, b = smooth(a[:n], 5), smooth(b[:n], 5)
    act = np.maximum(a, b) > pr.cfg['interview'].get('active_db', 52)
    d = a - b
    lab = np.where(~act, '', np.where(d > pr.cfg['interview'].get('host_margin_db', -3), 'host', 'guest'))
    return lab, a, b, raw


def turns(lab, T0, T1):
    """[(t0, t1, who)] covering T0..T1, silences carried by the previous talker"""
    i0, i1 = int(T0 / HOP), int(T1 / HOP)
    cur, runs = None, []
    for i in range(i0, i1):
        w = lab[i] or cur or 'guest'
        if runs and runs[-1][2] == w:
            runs[-1][1] = (i + 1) * HOP
        else:
            runs.append([i * HOP, (i + 1) * HOP, w])
        cur = w
    changed = True
    while changed:   # absorb short runs into the previous (or next) talker
        changed = False
        for j, r in enumerate(runs):
            if r[1] - r[0] < MIN_TURN and len(runs) > 1:
                if j:
                    runs[j - 1][1] = r[1]
                else:
                    runs[1][0] = r[0]
                del runs[j]
                changed = True
                break
        m = []
        for r in runs:
            if m and m[-1][2] == r[2]:
                m[-1][1] = r[1]
            else:
                m.append(r)
        runs = m
    runs[0][0], runs[-1][1] = T0, T1
    return [tuple(r) for r in runs]


def long_pauses(a, b, T0, T1, thr_db):
    """spans where both mics are quiet > LONG_PAUSE s -> cuts that leave KEEP_PAUSE s"""
    q = np.maximum(a, b) < thr_db
    out, i, i1 = [], int(T0 / HOP), int(T1 / HOP)
    while i < i1:
        if q[i]:
            j = i
            while j < i1 and q[j]:
                j += 1
            if (j - i) * HOP > LONG_PAUSE and i * HOP > T0 + 1 and j * HOP < T1 - 1:
                mid = (i + j) / 2 * HOP
                out.append({'start': mid - ((j - i) * HOP - KEEP_PAUSE) / 2,
                            'end': mid + ((j - i) * HOP - KEEP_PAUSE) / 2, 'why': 'long pause', 'auto': True})
            i = j
        else:
            i += 1
    return out


# ---------------------------------------------------------------- edit
class Edit:
    def __init__(self, pr: Project):
        self.pr = pr
        L = pr.cfg['longform']
        I = pr.cfg['interview']
        self.L, self.I = L, I
        self.take = str(L['take'])
        self.T0, self.T1 = float(L['start']), float(L['end'])
        self.cam = I['cams']
        lab, a, b, raw = speakers(pr, self.take)
        self.raw = raw
        self.lab = lab
        cuts = [dict(c) for c in L.get('cuts', [])]
        if I.get('trim_pauses', True):
            manual = [(c['start'], c['end']) for c in cuts]
            for c in long_pauses(raw, raw, self.T0, self.T1, I.get('quiet_db', 45)):
                if not any(c['start'] < e and c['end'] > s for s, e in manual):
                    cuts.append(c)
        self.cuts = []
        for c in sorted(cuts, key=lambda c: c['start']):
            c0 = self.T0 + round((c['start'] - self.T0) / FPF) * FPF
            self.cuts.append((c0, round((c['end'] - c0) / FPF), c.get('why', '')))
        self.NF = self.fr(self.T1)
        self.turns = turns(lab, self.T0, self.T1)
        # angle changes inside a turn land in a breath pause (both mics quiet >= 0.3 s), not mid-word
        q = raw < I.get('quiet_db', 45)
        self.seg_starts, i = [], 0
        while i < len(q):
            if q[i]:
                j = i
                while j < len(q) and q[j]:
                    j += 1
                if (j - i) * HOP >= 0.3:
                    self.seg_starts.append(round((i + j) / 2 * HOP, 2))
                i = j
            else:
                i += 1
        self.iv = self.build()

    # mic time -> output frame
    def fr(self, t: float) -> int:
        d = sum(min(max(0.0, t - c0), n * FPF) for c0, n, _ in self.cuts)
        return round((t - self.T0 - d) / FPF)

    def in_cut(self, t):
        return any(c0 <= t < c0 + n * FPF for c0, n, _ in self.cuts)

    def who(self, t):
        for t0, t1, w in self.turns:
            if t0 <= t < t1:
                return w
        return self.turns[-1][2]

    def shot(self, kind, who, t0, t1):
        cam_a = self.cam[who] if who in ('host', 'guest') else self.cam['wide']
        other = 'guest' if who == 'host' else 'host'
        if kind == 'close':
            return dict(cam=self.cam[who], z=(1.12, 1.18), ctr=None, dy=0.14, label=f'{who} close')
        if kind == 'tight':
            return dict(cam=self.cam[who], z=(1.32, 1.42), ctr=None, dy=0.10, label=f'{who} tight')
        if kind == 'wide':
            return dict(cam=self.cam['wide'], z=(1.16, 1.22), ctr=(0.5, 0.40), dy=0, label='wide')
        if kind == 'side':
            fx, fy = self.I['wide_faces'][who]
            return dict(cam=self.cam['wide'], z=(1.70, 1.80), ctr=(fx, fy + 0.10), dy=0, label=f'{who} side')
        if kind == 'react':
            return dict(cam=self.cam[other], z=(1.14, 1.20), ctr=None, dy=0.14, label=f'{other} listening')
        raise ValueError(kind)

    def main_talker(self, a, b):
        """who talks most in a..b (the person shown in a slide's camera window)"""
        seg = list(self.lab[int(a / HOP):int(b / HOP)])
        return max(('host', 'guest'), key=seg.count)

    def quietest(self, a, b):
        """fallback cut point when no breath pause is long enough: the quietest 100 ms in a..b"""
        if b - a < 2:
            return None
        i0, i1 = int(a / HOP), int(b / HOP)
        return round((i0 + int(np.argmin(self.raw[i0:i1]))) * HOP + HOP / 2, 2)

    def next_split(self, cur, te, lo, hi, target):
        c = [s for s in self.seg_starts if cur + lo <= s <= cur + hi and te - s >= 8 and not self.in_cut(s)]
        return min(c, key=lambda s: abs(s - (cur + target))) if c else None

    def build(self):
        # 1. boundaries: speaker turns, cut ends (every trim lands on a new angle), web slides, overrides
        web = [tuple(w) for w in self.L.get('web', [])]
        ovr = [tuple(o) for o in self.L.get('overrides', [])]
        marks = []   # (time, reason)
        for t0, t1, w in self.turns:
            lead = 0.15 if t0 > self.T0 else 0
            marks.append((max(self.T0, t0 - lead), 'turn'))
        for c0, n, _ in self.cuts:
            marks.append((c0 + n * FPF, 'cut'))
        for w0, w1, _ in web:
            marks += [(w0, 'web'), (w1, 'web')]
        for o0, o1, _ in ovr:
            marks += [(o0, 'ovr'), (o1, 'ovr')]
        marks = sorted({round(t, 3): r for t, r in marks if self.T0 <= t < self.T1}.items())
        bounds = [(t, r) for t, r in marks if not self.in_cut(t)] + [(self.T1, 'end')]
        iv = []
        for (t, r), (te, _) in zip(bounds, bounds[1:]):
            if te - t <= 0:
                continue
            ws = [w for w in web if w[0] <= t < w[1]]
            if ws:
                iv.append(dict(kind='slide', slide=ws[0][2], m0=t, m1=te, who=self.main_talker(t, te)))
                continue
            os_ = [o for o in ovr if o[0] <= t < o[1]]
            who = self.who(t + 0.3)
            if os_:
                kind = 'wide' if os_[0][2] == 'wide' else 'close'
                who = who if kind == 'wide' else os_[0][2]
                iv.append(dict(kind='cam', m0=t, m1=te, **self.shot(kind, who, t, te)))
                continue
            prev = iv[-1] if iv and iv[-1]['kind'] == 'cam' else None
            wide_cam = self.cam['wide']
            if te - t < QUICK:   # quick exchange: hold the two-shot (never punch out of a side crop)
                if prev and prev['label'] == 'wide':
                    prev['m1'] = te
                    continue
                kind = 'close' if prev and prev['cam'] == wide_cam else 'wide'
                iv.append(dict(kind='cam', m0=t, m1=te, **self.shot(kind, who, t, te)))
                continue
            # a turn: the talker's camera first, then alternate between the wide camera (wide / side
            # crop) and the talker's camera (close / tight) every 20-40 s. Two framings of one camera
            # are never cut together: if the talker's camera is already on screen, that shot simply
            # continues (same framing, so it merges into one continuous move).
            bi, ti = int(t) % 2, 0
            if prev and prev['cam'] == self.cam[who]:
                kind = prev['label'].split()[-1]   # 'close' / 'tight' / 'listening' -> continue it
                kind = kind if kind in ('close', 'tight') else 'wide'
            else:
                kind = 'close'
            cur = t
            while True:
                nxt = (self.next_split(cur, te, 20, 40, 28 if kind == 'close' else 24)
                       or self.next_split(cur, te, 14, 48, 30) or self.quietest(cur + 22, min(cur + 38, te - 8)))
                if nxt is None:
                    nxt = te
                iv.append(dict(kind='cam', m0=cur, m1=nxt, **self.shot(kind, who, cur, nxt)))
                if nxt >= te:
                    break
                cur = nxt
                if self.shot(kind, who, 0, 0)['cam'] == wide_cam:
                    kind = ('close', 'tight')[ti % 2]
                    ti += 1
                else:
                    kind = ('wide', 'side')[bi % 2]
                    bi += 1
        for v in iv:
            v['f0'], v['f1'] = self.fr(v['m0']), self.fr(v['m1'])
        iv = [v for v in iv if v['f1'] > v['f0']]
        # a sliver under 2.5 s (a turn mark just before or after a slide, say) joins the shot before it
        j = 1
        while j < len(iv):
            if iv[j]['f1'] - iv[j]['f0'] < 60 and iv[j]['kind'] == 'cam' and                     not any(abs(iv[j]['m0'] - (c0 + n * FPF)) < 1e-3 for c0, n, _ in self.cuts):
                iv[j - 1]['m1'], iv[j - 1]['f1'] = iv[j]['m1'], iv[j]['f1']
                del iv[j]
            else:
                j += 1
        # merge consecutive identical shots (e.g. two quick exchanges both wide)
        out = []
        for v in iv:
            if out and v['kind'] == out[-1]['kind'] == 'cam' and v['label'] == out[-1]['label'] \
                    and not any(abs(out[-1]['m1'] - (c0 + n * FPF)) < 1e-3 for c0, n, _ in self.cuts):
                out[-1]['m1'], out[-1]['f1'] = v['m1'], v['f1']
            elif out and v['kind'] == out[-1]['kind'] == 'slide' and v['slide'] == out[-1]['slide']:
                out[-1]['m1'], out[-1]['f1'] = v['m1'], v['f1']
            else:
                out.append(v)
        for v in out:   # after merging: a slide's window shows whoever talks most during it
            if v['kind'] == 'slide':
                v['who'] = self.main_talker(v['m0'], v['m1'])
        for x, y in zip(out, out[1:]):
            assert x['f1'] == y['f0'], (x, y)
        return out

    # ------------------------------------------------------------ render
    def cam_in(self, cam, v, f0):
        path, off, _, _ = self.pr.camera(self.take, cam)
        # mic time of output frame f0 inside v (the interval never spans a cut)
        return ['-ss', f"{v['m0'] + (f0 - v['f0']) * FPF + off:.4f}", '-i', path]

    def window_cam(self, who, idx, lab):
        """the talker's close camera cropped into the split-layout window"""
        cam = self.cam[who]
        px, py, pw, ph = brand.SPLIT['window']
        ch = 1500
        cw = round(ch * pw / ph / 2) * 2
        _, _, fx, fy = self.pr.camera(self.take, cam)
        x = min(3840 - cw, max(0, round(3840 * fx - cw / 2)))
        y = min(2160 - ch, max(0, round(2160 * fy - 0.30 * ch)))
        return cam, (f"[{idx}:v]setpts=PTS-STARTPTS,crop={cw}:{ch}:{x}:{y},scale={pw}:{ph}:flags=lanczos,{GRADE},"
                     f"pad=1920:1080:{px}:{py}:black[{lab}c]")

    def spec(self, v, f0, idx, lab, cards: Path):
        if v['kind'] == 'cam':
            fx, fy = self.pr.camera(self.take, v['cam'])[2:]
            cx, cy = v['ctr'] or (fx, fy + v['dy'])
            flt = (f"[{idx}:v]setpts=PTS-STARTPTS,"
                   f"{zoom(v['z'][0], v['z'][1], v['f1'] - v['f0'], cx, cy, f0 - v['f0'], center_y=True)},"
                   f"scale=1920:1080:flags=lanczos,{GRADE},vignette=angle=PI/7,format=yuv420p[{lab}]")
            return self.cam_in(v['cam'], v, f0), flt, 1
        cam, wflt = self.window_cam(v['who'], idx, lab)
        ins = self.cam_in(cam, v, f0)
        sx, sy, sw, sh = brand.SPLIT['slide']
        if v['slide'].startswith('scroll:'):
            stem = v['slide'][7:]
            img = self.pr.p(self.L.get('slides_dir', 'images')) / f'{stem}.png'
            W, H = Image.open(img).size
            ch = round(W * sh / sw)
            travel = H - ch
            n = v['f1'] - v['f0']
            hold = min(48, n // 5)
            # eased scroll from top to bottom, holding ~2 s at each end; p = 0..1 over the move
            p = f"min(1,max(0,(n+{f0 - v['f0']}-{hold})/{max(1, n - 2 * hold)}))"
            yexp = f"{travel}*(3*pow({p},2)-2*pow({p},3))"
            extra, k = [], idx + 2
            flt = (f"{wflt};[{idx + 1}:v]crop={W}:{ch}:0:'{yexp}',scale={sw}:{sh}:flags=lanczos,setsar=1[{lab}s];"
                   f"[{lab}c][{lab}s]overlay={sx}:{sy}[{lab}m];")
            barf = img.with_suffix('.bar.png')   # browser bar (browser_frame.py --bar) fixed over the page
            if barf.exists():
                extra = ['-framerate', FPS, '-loop', '1', '-i', barf]
                flt += f"[{lab}m][{k}:v]overlay={sx}:{sy}[{lab}n];"
                k += 1
            else:
                flt += f"[{lab}m]null[{lab}n];"
            flt += (f"[{k}:v]scale=out_color_matrix=bt709:out_range=tv,format=yuva420p[{lab}f];"
                    f"[{lab}n][{lab}f]overlay=0:0:format=yuv420,format=yuv420p[{lab}]")
            return ins + ['-framerate', FPS, '-loop', '1', '-i', img, *extra,
                          '-framerate', FPS, '-loop', '1', '-i', cards / '_frame_scroll.png'], flt, k + 1 - idx
        flt = (f"{wflt};[{idx + 1}:v]scale=out_color_matrix=bt709:out_range=tv,format=yuva420p[{lab}p];"
               f"[{lab}c][{lab}p]overlay=0:0:format=yuv420,format=yuv420p[{lab}]")
        return ins + ['-framerate', FPS, '-loop', '1', '-i', cards / f"{v['slide']}.png"], flt, 2

    def units(self):
        u = []
        for i, v in enumerate(self.iv):
            f0 = v['f0']
            prev = self.iv[i - 1] if i else None
            if prev is not None and (prev['kind'] == 'slide' or v['kind'] == 'slide'):
                u.append(('trans', prev, v, f0, min(TR, v['f1'] - f0)))
                f0 += TR
            if v['f1'] > f0:
                u.append(('one', v, None, f0, v['f1'] - f0))
        return u

    def render_unit(self, j, u, cards: Path, force: bool):
        typ, a, b, f0, n = u
        if typ == 'one':
            ins, flt, _ = self.spec(a, f0, 0, 'v', cards)
        else:
            # the outgoing interval is read past its end for the TR-frame overlap
            i1, f1, k1 = self.spec(a, f0, 0, 'a', cards)
            i2, f2, _ = self.spec(b, f0, k1, 'b', cards)
            ins, flt = i1 + i2, f"{f1};{f2};[a][b]blend=all_expr='{blend_in(n)}'[v]"
        post = (['fade=t=in:s=0:n=18'] if f0 == 0 else []) + \
               ([f'fade=t=out:s={n - 30}:n=30'] if f0 + n == self.NF else [])
        if post:
            flt = flt[:-3] + '[w];[w]' + ','.join(post) + '[v]'
        args = [*ins, '-filter_complex', flt, '-map', '[v]', '-frames:v', str(n), '-an',
                '-x264-params', 'keyint=48:min-keyint=1']
        key = hashlib.sha1(json.dumps([str(x) for x in args]).encode()).hexdigest()[:12]
        out = self.pr.work / 'units' / f'u{j:04d}_{key}.mp4'
        if out.exists() and not force:
            return out
        tmp = out.with_suffix('.tmp.mp4')
        if not run([FF, '-v', 'error', '-y', *args, *x264(tmp)], f'unit {j}'):
            return None
        tmp.replace(out)
        print(f'unit {j} done', flush=True)
        return out

    # ------------------------------------------------------------ audio
    def automix(self) -> Path:
        """Sum of the two iso mics with the idle mic ducked 10 dB (kills the bleed comb), each
        talker levelled to the same speech median first."""
        out = self.pr.work / 'audio' / 'automix.wav'
        if out.exists():
            return out
        iso = self.pr.take(self.take)['iso']
        sig = []
        for f in iso:
            r = subprocess.run([FF, '-v', 'error', '-i', str(self.pr.p(f)), '-ac', '1', '-ar', '48000',
                                '-f', 'f32le', '-'], capture_output=True, check=True)
            sig.append(np.frombuffer(r.stdout, np.float32))
        n = min(len(s) for s in sig)
        lab = self.lab
        assert lab is not None
        hops = n // 4800
        e = [env100(self.pr.p(iso[0]), self.pr.work / 'audio/env_host.npy'),
             env100(self.pr.p(iso[1]), self.pr.work / 'audio/env_guest.npy')]
        lv = [np.median(e[0][:hops][lab[:hops] == 'host']), np.median(e[1][:hops][lab[:hops] == 'guest'])]
        ref = max(lv)
        mix = np.zeros(n, np.float32)
        for k, (s, who) in enumerate(zip(sig, ('host', 'guest'))):
            other = 'guest' if who == 'host' else 'host'
            g = np.where(lab[:hops] == other, 10 ** (-10 / 20), 1.0)
            g = smooth(g, 3)   # 300 ms ramps
            gs = np.interp(np.arange(n), np.arange(hops) * 4800 + 2400, g).astype(np.float32)
            mix += s[:n] * gs * 10 ** ((ref - lv[k]) / 20)
            print(f'{who}: speech level {lv[k]:.1f} dB, gain {ref - lv[k]:+.1f} dB')
        peak = np.abs(mix).max()
        if peak > 0.99:
            mix *= 0.99 / peak
        w = wave.open(str(out), 'wb')
        w.setnchannels(1), w.setsampwidth(3), w.setframerate(48000)
        i24 = (np.clip(mix, -1, 1) * 8388607).astype(np.int32)
        w.writeframes(np.stack([(i24 & 255), (i24 >> 8) & 255, (i24 >> 16) & 255], 1).astype(np.uint8).tobytes())
        w.close()
        return out

    def audio(self) -> Path:
        mixf = self.automix()
        pieces, cur = [], self.T0
        for c0, n, _ in self.cuts:
            pieces.append((cur, round((c0 - cur) / FPF)))
            cur = c0 + n * FPF
        pieces.append((cur, self.NF - sum(p[1] for p in pieces)))
        parts = []
        for i, (a, n) in enumerate(pieces):
            s0 = round(a * 48000)
            parts.append(f"[0:a]atrim=start_sample={s0}:end_sample={s0 + n * SAMPLES_PER_FRAME},asetpts=N/SR/TB,"
                         f"afade=t=in:d=0.02,afade=t=out:st={n * FPF - 0.02:.4f}:d=0.02[p{i}]")
        chain = ';'.join(parts) + ';' + ''.join(f'[p{i}]' for i in range(len(pieces))) + \
            f'concat=n={len(pieces)}:v=0:a=1'
        out = self.pr.work / 'audio' / 'longform_master.wav'
        master_voice(mixf, chain, out, lufs_mono=-19, total_s=self.NF * FPF, fade_in=0.75, fade_out=1.25)
        return out


def scroll_frame(cards: Path) -> None:
    """split-layout frame with both the slide area and the camera window transparent"""
    out = cards / '_frame_scroll.png'
    if out.exists():
        return
    any_card = next(f for f in sorted(cards.glob('*.png')) if not f.name.startswith('_'))
    a = np.array(Image.open(any_card).convert('RGBA'))
    sx, sy, sw, sh = brand.SPLIT['slide']
    R = brand.SPLIT['radius']
    m = Image.new('L', (sw * 4, sh * 4), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, sw * 4 - 1, sh * 4 - 1], R * 4, fill=255)
    hole = np.array(m.resize((sw, sh), Image.LANCZOS))
    a[sy:sy + sh, sx:sx + sw, 3] = np.minimum(a[sy:sy + sh, sx:sx + sw, 3], 255 - hole)
    Image.fromarray(a).save(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('project')
    ap.add_argument('--plan', action='store_true')
    ap.add_argument('--force', action='store_true')
    ap.add_argument('--jobs', type=int, default=3)
    ap.add_argument('--only', default='', help='render only units a-b (for checking)')
    a = ap.parse_args()
    pr = Project(a.project)
    e = Edit(pr)
    units = e.units()
    print(f'{len(e.turns)} turns, {len(e.cuts)} cuts, {len(e.iv)} intervals, {len(units)} units, '
          f'{e.NF} frames, {e.NF * FPF / 60:.2f} min')
    if a.plan:
        for v in e.iv:
            o = v['f0'] * FPF
            print(f"out {int(o // 60):2d}:{o % 60:05.2f}  mic {v['m0']:8.2f}-{v['m1']:8.2f} "
                  f"({v['m1'] - v['m0']:5.1f}s)  {v['kind']:5s} {v.get('label') or v.get('slide')}")
        for c0, n, why in e.cuts:
            print(f'cut mic {c0:8.2f} +{n * FPF:5.2f}s  {why}')
        return
    cards = make_cards(pr, pr.p(e.L.get('slides_dir', 'images')))
    if any(v['kind'] == 'slide' and v['slide'].startswith('scroll:') for v in e.iv):
        scroll_frame(cards)
    (pr.work / 'units').mkdir(parents=True, exist_ok=True)
    sel = list(enumerate(units))
    if a.only:
        lo, hi = map(int, a.only.split('-'))
        sel = sel[lo:hi + 1]
    with ThreadPoolExecutor(a.jobs) as ex:
        outs = list(ex.map(lambda ju: e.render_unit(*ju, cards, a.force), sel))
    if not all(outs):
        raise SystemExit('some units failed')
    if a.only:
        print('\n'.join(str(o) for o in outs))
        return
    lst = pr.work / 'units.txt'
    lst.write_text(''.join(f"file '{o.as_posix()}'\n" for o in outs))
    wav = e.audio()
    out = pr.p(e.L.get('output', f"exports/{pr.cfg['slug']}.mp4"))
    out.parent.mkdir(parents=True, exist_ok=True)
    run([FF, '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-i', wav, '-map', '0:v', '-map', '1:a',
         '-c:v', 'copy', '-c:a', 'aac', '-b:a', '320k', '-ar', '48000', '-movflags', '+faststart', out], 'mux')
    print('done', out)


if __name__ == '__main__':
    main()

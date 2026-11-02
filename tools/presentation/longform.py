"""Long-form 1920x1080 edit of a presentation take: two synced cameras, external mic, and the
slide images shown in a split layout (slide card + live camera window) while they are being
talked about.

    python tools/presentation/longform.py D:\\Videos\\<slug> --plan      # print the edit
    python tools/presentation/longform.py D:\\Videos\\<slug> [--jobs 3] [--force]

Reads project.json "longform": take, start/end (mic seconds), cuts (spans to remove, e.g. an
aside the user asked to drop), and plan: [[mic_time, "cam"] | [mic_time, "slide", <slide name>]]
-- each entry runs until the next. Camera stretches are split into 9-19 s shots at sentence
starts, cycling front/side angles and slow zooms; slides and layout changes crossfade over 10
frames; the first unit fades in from black and the last fades out. Units are rendered as
separate H.264 files (cached in work/units; --force re-renders) and joined with the concat
demuxer, so a re-render after a small change only redoes the units that changed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import brand
from common import FF, FPF, FPS, GRADE, SAMPLES_PER_FRAME, Project, blend_in, master_voice, run, x264, zoom

TR = 10   # crossfade frames


def make_cards(pr: Project, slides_dir: Path) -> Path:
    """Split-layout frames: dark backdrop, slide card on the left, transparent rounded window on
    the right where the live camera shows through (brand.SPLIT)."""
    out = pr.work / 'cards'
    out.mkdir(parents=True, exist_ok=True)
    W, H = 1920, 1080
    SX, SY, SW, SH = brand.SPLIT['slide']
    WX, WY, WW, WH = brand.SPLIT['window']
    R = brand.SPLIT['radius']
    y, x = np.mgrid[0:H, 0:W]
    t = np.clip(np.sqrt(((x - W / 2) / (W * 0.75)) ** 2 + ((y - H / 2) / (H * 0.75)) ** 2), 0, 1)[..., None]
    c0, c1 = np.array(brand.SPLIT['backdrop_inner']), np.array(brand.SPLIT['backdrop_outer'])
    noise = np.random.default_rng(1).normal(0, 1.2, (H, W, 1))   # dither: no banding in the gradient
    bg = Image.fromarray(np.clip(c0 * (1 - t) + c1 * t + noise, 0, 255).astype(np.uint8)).convert('RGBA')

    def rmask(w, h, r):
        m = Image.new('L', (w * 4, h * 4), 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, w * 4 - 1, h * 4 - 1], r * 4, fill=255)
        return m.resize((w, h), Image.LANCZOS)
    sh = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(sh)
    for (a, b, w, h) in ((SX, SY, SW, SH), (WX, WY, WW, WH)):
        d.rounded_rectangle([a, b + 10, a + w, b + h + 10], R, fill=170)
    base = Image.composite(Image.new('RGBA', (W, H), (0, 0, 0, 255)), bg, sh.filter(ImageFilter.GaussianBlur(22)))
    win = np.array(rmask(WW, WH, R))
    for f in sorted(slides_dir.glob('*.png')):
        dst = out / f.name
        if dst.exists() and dst.stat().st_mtime > f.stat().st_mtime:
            continue
        im = base.copy()
        im.paste(Image.open(f).convert('RGB').resize((SW, SH), Image.LANCZOS), (SX, SY), rmask(SW, SH, R))
        a = np.array(im)
        a[WY:WY + WH, WX:WX + WW, 3] = 255 - win
        Image.fromarray(a).save(dst)
    return out


class Edit:
    def __init__(self, pr: Project):
        self.pr = pr
        L = pr.cfg['longform']
        self.L = L
        self.take = str(L['take'])
        self.cams = pr.cameras(self.take)
        self.split_cam = L.get('split_camera', self.cams[0])
        self.T0, self.T1 = float(L['start']), float(L['end'])
        # cuts snap to whole frames so audio (2002 samples/frame) and video stay locked
        self.cuts = []
        for c in L.get('cuts', []):
            c0 = self.T0 + round((c['start'] - self.T0) / FPF) * FPF
            self.cuts.append((c0, round((c['end'] - c0) / FPF)))
        plan = [tuple(p) for p in L['plan']]
        for c0, n in self.cuts:   # resume after a cut with the same visual, marked as a jump
            prev = [p for p in plan if p[0] <= c0][-1]
            plan.append((c0 + n * FPF,) + prev[1:])
        self.plan = sorted(plan, key=lambda p: p[0])
        self.NF = self.fr(self.T1)
        starts = [s['start'] for s in pr.words(self.take)]
        a, b = self.cams[0], self.cams[-1]
        # (camera, zoom from, zoom to, framing centre or None = the face)
        SHOTS = [(a, 1.00, 1.07, (0.50, 0.45)), (b, 1.40, 1.50, None), (a, 1.45, 1.30, None),
                 (b, 1.00, 1.07, (0.50, 0.45)), (a, 1.30, 1.42, None), (b, 1.55, 1.38, None)]
        iv, shot_i = [], 0
        for k, p in enumerate(self.plan):
            t, kind = p[0], p[1]
            te = self.plan[k + 1][0] if k + 1 < len(self.plan) else self.T1
            if kind == 'slide':
                iv.append(dict(kind='slide', slide=p[2], f0=self.fr(t), f1=self.fr(te), m0=t, jump=self.is_jump(t)))
                continue
            cur = t
            while True:
                c = [s for s in starts if cur + 9 <= s <= cur + 19 and te - s >= 6]
                nxt = min(c, key=lambda s: abs(s - (cur + 14))) if c else te
                if k == 0:
                    nxt = te   # open on the front camera through to the first slide
                iv.append(dict(kind='cam', shot=SHOTS[shot_i % len(SHOTS)], f0=self.fr(cur), f1=self.fr(nxt),
                               m0=cur, jump=self.is_jump(cur)))
                shot_i += 1
                if nxt >= te:
                    break
                cur = nxt
        iv = [v for v in iv if v['f1'] > v['f0']]
        for x, y in zip(iv, iv[1:]):
            assert x['f1'] == y['f0'], (x, y)
        self.iv = iv
        units = []
        for i, v in enumerate(iv):
            f0 = v['f0']
            prev = iv[i - 1] if i else None
            same = prev and prev['kind'] == v['kind'] == 'slide' and prev['slide'] == v['slide']
            if prev is not None and (v['jump'] or not (prev['kind'] == v['kind'] == 'cam') and not same):
                units.append(('trans', prev, v, f0, TR))
                f0 += TR
            if v['f1'] > f0:
                units.append(('one', v, None, f0, v['f1'] - f0))
        self.units = units

    def fr(self, t: float) -> int:
        d = sum(min(max(0.0, t - c0), n * FPF) for c0, n in self.cuts)
        return round((t - self.T0 - d) / FPF)

    def is_jump(self, t: float) -> bool:
        return any(abs(t - (c0 + n * FPF)) < 1e-6 for c0, n in self.cuts)

    def cam_in(self, cam, v, f0) -> list:
        path, off, _, _ = self.pr.camera(self.take, cam)
        return ['-ss', f"{v['m0'] + (f0 - v['f0']) * FPF + off:.4f}", '-i', path]

    def spec(self, v, f0, idx, lab, cards: Path):
        if v['kind'] == 'cam':
            cam, z0, z1, ctr = v['shot']
            _, _, fx, fy = self.pr.camera(self.take, cam)
            cx, cy = ctr or (fx, fy)
            flt = (f"[{idx}:v]setpts=PTS-STARTPTS,{zoom(z0, z1, v['f1'] - v['f0'], cx, cy, f0 - v['f0'], center_y=True)},"
                   f"scale=1920:1080:flags=lanczos,{GRADE},vignette=angle=PI/7,format=yuv420p[{lab}]")
            return self.cam_in(cam, v, f0), flt
        px, py, pw, ph = brand.SPLIT['window']
        ch = 1400
        cw = round(ch * pw / ph / 2) * 2
        _, _, fx, fy = self.pr.camera(self.take, self.split_cam)
        flt = (f"[{idx}:v]setpts=PTS-STARTPTS,crop={cw}:{ch}:{round(3840 * fx - cw / 2)}:{round(2160 * fy - 0.36 * ch)},"
               f"scale={pw}:{ph}:flags=lanczos,{GRADE},pad=1920:1080:{px}:{py}:black,format=yuv420p[{lab}c];"
               f"[{idx + 1}:v]scale=out_color_matrix=bt709:out_range=tv,format=yuva420p[{lab}p];"
               f"[{lab}c][{lab}p]overlay=0:0:format=yuv420,format=yuv420p[{lab}]")
        return self.cam_in(self.split_cam, v, f0) + ['-framerate', FPS, '-loop', '1', '-i',
                                                     cards / f"{v['slide']}.png"], flt

    def render_unit(self, j, u, cards: Path, force: bool) -> Path | None:
        typ, a, b, f0, n = u
        if typ == 'one':
            ins, flt = self.spec(a, f0, 0, 'v', cards)
        else:
            i1, f1 = self.spec(a, f0, 0, 'a', cards)
            i2, f2 = self.spec(b, f0, 2 if a['kind'] == 'slide' else 1, 'b', cards)
            ins, flt = i1 + i2, f"{f1};{f2};[a][b]blend=all_expr='{blend_in(n)}'[v]"
        post = (['fade=t=in:s=0:n=18'] if f0 == 0 else []) + ([f'fade=t=out:s={n - 30}:n=30'] if f0 + n == self.NF else [])
        if post:
            flt = flt[:-3] + '[w];[w]' + ','.join(post) + '[v]'
        args = [*ins, '-filter_complex', flt, '-map', '[v]', '-frames:v', str(n), '-an', '-x264-params',
                'keyint=48:min-keyint=1']
        key = hashlib.sha1(json.dumps([str(x) for x in args]).encode()).hexdigest()[:12]
        out = self.pr.work / 'units' / f'u{j:04d}_{key}.mp4'
        if out.exists() and not force:
            return out
        tmp = out.with_suffix('.tmp.mp4')
        if not run([FF, '-v', 'error', '-y', *args, *x264(tmp)], f'unit {j}'):
            return None
        tmp.replace(out)
        return out

    def audio(self) -> Path:
        """Mic from start to end with the cuts taken out, each piece a whole number of frames."""
        pieces, cur = [], self.T0
        for c0, n in self.cuts:
            pieces.append((cur, round((c0 - cur) / FPF)))
            cur = c0 + n * FPF
        pieces.append((cur, self.NF - sum(p[1] for p in pieces)))
        parts = []
        for i, (a, n) in enumerate(pieces):
            s0 = round(a * 48000)
            parts.append(f"[0:a]atrim=start_sample={s0}:end_sample={s0 + n * SAMPLES_PER_FRAME},asetpts=N/SR/TB,"
                         f"afade=t=in:d=0.008,afade=t=out:st={n * FPF - 0.008:.4f}:d=0.008[p{i}]")
        chain = ';'.join(parts) + ';' + ''.join(f'[p{i}]' for i in range(len(pieces))) + f'concat=n={len(pieces)}:v=0:a=1'
        out = self.pr.work / 'audio' / 'longform_master.wav'
        master_voice(self.pr.mic(self.take), chain, out, lufs_mono=-19, total_s=self.NF * FPF,
                     fade_in=0.75, fade_out=1.25)
        return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('project')
    ap.add_argument('--plan', action='store_true')
    ap.add_argument('--force', action='store_true')
    ap.add_argument('--jobs', type=int, default=3)
    a = ap.parse_args()
    pr = Project(a.project)
    e = Edit(pr)
    print(f'{len(e.iv)} intervals, {len(e.units)} units, {e.NF} frames, {e.NF * FPF / 60:.2f} min')
    if a.plan:
        for j, u in enumerate(e.units):
            v = u[1] if u[0] == 'one' else u[2]
            print(j, u[0], u[3], u[4], f'out {u[3] * FPF:7.2f}s', v['kind'], v.get('slide') or v['shot'][:3])
        return
    cards = make_cards(pr, pr.p(e.L.get('slides_dir', 'images')))
    (pr.work / 'units').mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(a.jobs) as ex:
        outs = list(ex.map(lambda ju: e.render_unit(*ju, cards, a.force), enumerate(e.units)))
    if not all(outs):
        raise SystemExit('some units failed')
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

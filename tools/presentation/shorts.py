"""Vertical 1080x1920 shorts (YouTube Shorts / Instagram Reels) cut straight from the multicam
takes -- both the 2-3 highlight shorts pulled from a long-form presentation and stand-alone
short stories (like a separately recorded history segment).

    python tools/presentation/shorts.py D:\\Videos\\<slug> <name>|all --plan   # plan + caption text
    python tools/presentation/shorts.py D:\\Videos\\<slug> <name>|all [--force]

project.json "shorts": {name: {take, title, hook, ranges, graphics, fade_out}}:
  ranges    [[from, to], ...] mic seconds; edges snap into the nearest silence so no word is
            clipped. [from, to, "exact_end"] ends exactly at `to` (to drop a closing line);
            "exact_start" / "exact" pin the start / both edges (to drop a stutter with no pause).
  graphics  [{start, end, image, label, crop}] shown full screen with a slow push-in. No label
            = a chart graphic (its paper colour is extended to 9:16); with a label = a photo
            plate (blurred backdrop, rounded photo, label chip). `image` may be a list of two
            images shown side by side; `crop` = [left, top, right, bottom] fractions to trim.
  hook      on-screen hook for the first ~3 s (only when the short opens on camera).
  fade_out  seconds to fade picture and sound to black at the end (default: 0.3 s sound only).

Editing rules (docs/types/presentation.md "Shorts"):
  * Pauses over 0.3 s are tightened to ~0.2 s and ums/uhs are removed. Under a full-screen
    graphic every trim is invisible. On camera, a trim becomes an angle change only if the
    current angle has already held MIN_SHOT; otherwise ums and long pauses are still removed
    behind a 6-frame dissolve on the same angle, and short pauses are left alone.
  * An angle holds 3.6-8 s with a slow zoom; a camera sliver under 2.5-3 s next to a graphic
    is absorbed into the graphic.
  * Burned captions in the brand style (brand.ASS_HEADER), placed per layout.
  * Audio: same voice chain as the long-form, -14 LUFS stereo.
"""
from __future__ import annotations

import argparse
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

import brand
from common import (FF, FILLERS, FPF, FPS, GRADE, SAMPLES_PER_FRAME, Project, blend_in, envelope, master_voice,
                    quiet, run, x264, zoom)

MIN_SHOT = 3.6    # s an angle must hold before an audio trim may cut away to the other angle
MAX_SHOT = 8.0    # longest single camera shot before switching angle
SOFT_FRAMES = 6   # dissolve length for a trim hidden on the same angle


def norm(w: str) -> str:
    return re.sub(r"[^a-z0-9']", '', w.lower())


class Short:
    MIN_SHOT, MAX_SHOT = MIN_SHOT, MAX_SHOT   # a subclass may hold angles longer

    def __init__(self, pr: Project, name: str):
        self.pr, self.name = pr, name
        self.cfg = pr.cfg['shorts'][name]
        self.take = str(self.cfg['take'])
        self.cams = pr.cameras(self.take)
        self.env = envelope(pr.wav16k(self.take))
        self.graphics = [g if isinstance(g, dict) else dict(start=g[0], end=g[1], image=g[2],
                                                             label=g[3] if len(g) > 3 else None)
                         for g in self.cfg.get('graphics', [])]
        self.plan()

    # ---------------------------------------------------------------- cutting
    def cut_candidates(self):
        """Spans worth removing: pauses > 0.3 s, and ums/uhs with the pauses around them."""
        env = self.env
        cands = [[s0 + 0.09, s1 - 0.09, 'pause'] for s0, s1 in self.pr.silences(self.take) if s1 - s0 > 0.30]
        fw = self.pr.fillers(self.take)
        for i, (s, e, w) in enumerate(fw):
            if w.lower().strip(',.?!…') not in FILLERS:
                continue
            # Whisper's word times are loose (an um often "starts" where the last word ends), so
            # find the um in the audio: a voiced burst with quiet on both sides. The disfluent
            # prompt can also invent an um and hand it the next word's timing, so the burst must
            # be a sound of its own -- the previous word's sound ends before it and the next
            # word's starts after it. (A looser rule once deleted a real "with".)
            prev_s, prev_e = (fw[i - 1][0], fw[i - 1][1]) if i else (s - 2, s - 1)
            next_s, next_e = (fw[i + 1][0], fw[i + 1][1]) if i + 1 < len(fw) else (e + 1, e + 2)
            lo, hi = min(prev_s, s - 0.6), max(next_e, e + 0.6) + 0.2
            runs, start = [], None
            for t in np.arange(lo, hi, 0.01):
                loud = not quiet(env, t)
                if loud and start is None:
                    start = t
                if not loud and start is not None:
                    runs.append((start, t))
                    start = None
            ok = [r for r in runs if r[0] > lo + 0.05 and 0.10 <= r[1] - r[0] <= 1.0
                  and r[0] >= prev_e - 0.12 and r[1] <= next_s + 0.05 and min(r[1], e) - max(r[0], s) > 0.03
                  and any(q[1] < r[0] - 0.03 and q[1] > prev_s - 0.1 for q in runs)
                  and any(q[0] > r[1] + 0.03 and q[0] < next_e + 0.15 for q in runs)]
            if not ok:
                continue
            r0, r1 = max(ok, key=lambda r: min(r[1], e) - max(r[0], s))
            q0, q1 = r0, r1
            while q0 - 0.01 > lo and quiet(env, q0 - 0.01):
                q0 -= 0.01
            while q1 + 0.01 < hi and quiet(env, q1 + 0.01):
                q1 += 0.01
            cands.append([min(q0 + 0.09, r0 - 0.04), max(q1 - 0.09, r1 + 0.04), 'um'])
        cands = sorted(c for c in cands if any(a + 0.15 < c[0] and c[1] < b - 0.15 for a, b in self.rng)
                       and c[1] - c[0] > 0.06)
        merged = []
        for c in cands:   # touching, or separated only by quiet: one cut
            gap_quiet = merged and c[0] - merged[-1][1] < 0.3 and all(
                quiet(env, t) for t in np.arange(merged[-1][1], c[0], 0.01))
            if merged and (c[0] <= merged[-1][1] or gap_quiet):
                merged[-1][1] = max(merged[-1][1], c[1])
                merged[-1][2] = 'um' if 'um' in (c[2], merged[-1][2]) else 'pause'
            else:
                merged.append(list(c))
        return merged

    def plan(self):
        sil = self.pr.silences(self.take)
        rng = []
        for r in self.cfg['ranges']:
            a, b = r[:2]
            flag = r[2] if len(r) > 2 else ''
            before = [] if flag in ('exact_start', 'exact') else [s1 for s0, s1 in sil if a - 1.2 < s1 <= a + 0.15]
            after = [] if flag in ('exact_end', 'exact') else [s0 for s0, s1 in sil if b - 0.15 <= s0 < b + 1.2]
            rng.append((before[-1] - 0.06 if before else a, after[0] + 0.10 if after else b))
        self.rng = rng
        G = [(g['start'], g['end']) for g in self.graphics]

        def under_graphic(a, b):
            return any(g0 - 0.05 <= a and b <= g1 + 0.05 for g0, g1 in G)

        def touches_edge(a, b):
            return any(a <= x <= b for g in G for x in g)
        marks = sorted([a for a, _ in rng] + [x for g in G for x in g])   # visual changes so far
        taken = []
        for c in self.cut_candidates():
            a, b, kind = c
            if under_graphic(a, b) or touches_edge(a, b):
                taken.append(c + ['hidden'])
                continue
            last = max([m for m in marks if m <= a] + [rng[0][0]])
            nxt = min([m for m in marks if m >= b] + [x for _, x in rng if x >= b])
            held = (a - last) - sum(min(t[1], a) - max(t[0], last) for t in taken if t[1] > last and t[0] < a)
            if held >= self.MIN_SHOT and nxt - b >= self.MIN_SHOT * 0.6:
                taken.append(c + ['hard'])
                marks = sorted(marks + [b])
            elif kind == 'um' or b - a > 0.45:
                taken.append(c + ['soft'])
        self.taken = taken
        pieces = []
        for a, b in rng:
            cur, how = a, 'start'
            for c0, c1, _, kind in taken:
                if a < c0 and c1 < b:
                    pieces.append((cur, c0, how))
                    cur, how = c1, kind
            pieces.append((cur, b, how))
        clips, f = [], 0
        for a, b, how in pieces:
            n = round((b - a) / FPF)
            if n > 0:
                clips.append(dict(m0=a, n=n, f0=f, how=how))
                f += n
        self.clips, self.nf = clips, f
        soft_edges = {c['f0'] for c in clips if c['how'] == 'soft'}

        def out_frame(t):
            for c in clips:
                if t < c['m0']:
                    return c['f0']
                if t < c['m0'] + c['n'] * FPF:
                    return c['f0'] + round((t - c['m0']) / FPF)
            return f
        gfx = [(out_frame(g['start']), out_frame(g['end']), g) for g in self.graphics]
        edges = sorted({0, f} | {x for g in gfx for x in g[:2]} | {c['f0'] for c in clips})
        segs = []
        for a, b in zip(edges, edges[1:]):
            g = next((g for g in gfx if g[0] <= a < g[1]), None)
            if g and segs and segs[-1]['gfx'] is g[2] and segs[-1]['f0'] + segs[-1]['n'] == a:
                segs[-1]['n'] += b - a
                continue
            c = next(c for c in clips if c['f0'] <= a < c['f0'] + c['n'])
            segs.append(dict(m0=c['m0'] + (a - c['f0']) * FPF, n=b - a, f0=a, gfx=g[2] if g else None))
        # a camera sliver between graphics would flash by: the graphic next to it covers it
        i = 0
        while i < len(segs):
            s = segs[i]
            prev = segs[i - 1] if i else None
            nxt = segs[i + 1] if i + 1 < len(segs) else None
            if s['gfx'] is None and s['n'] < round(3.0 / FPF) and ((prev and prev['gfx']) or (nxt and nxt['gfx'])):
                if prev and prev['gfx']:
                    prev['n'] += s['n']
                else:
                    nxt['n'] += s['n']
                    nxt['f0'] = s['f0']
                segs.pop(i)
                continue
            i += 1
        merged = []
        for s in segs:
            if merged and s['gfx'] and merged[-1]['gfx'] is s['gfx']:
                merged[-1]['n'] += s['n']
            else:
                merged.append(s)
        # angle "holds": camera pieces joined only by soft cuts keep one angle and one continuous
        # zoom; a long hold is split for an angle change at MAX_SHOT, never on a soft cut
        holds = []
        for s in merged:
            if s['gfx'] is None and holds and holds[-1][-1]['gfx'] is None and s['f0'] in soft_edges:
                holds[-1].append(s)
            else:
                holds.append([s])
        i = 0
        while i < len(holds):   # an angle on screen < 2.5 s folds into a neighbour
            h = holds[i]
            if h[0]['gfx'] is None and sum(p['n'] for p in h) < round(2.5 / FPF) and len(holds) > 1:
                prev = holds[i - 1] if i else None
                nxt = holds[i + 1] if i + 1 < len(holds) else None
                if prev and prev[0]['gfx'] is not None:
                    prev[0]['n'] += sum(p['n'] for p in h)
                elif nxt and nxt[0]['gfx'] is not None:
                    nxt[0]['n'] += sum(p['n'] for p in h)
                    nxt[0]['f0'] = h[0]['f0']
                elif prev:
                    soft_edges.add(h[0]['f0'])
                    prev.extend(h)
                else:
                    i += 1
                    continue
                holds.pop(i)
                continue
            i += 1
        K = round(self.MAX_SHOT / FPF)
        shots = []
        for h in holds:
            if h[0]['gfx'] is not None:
                shots.append(dict(h[0], soft=False))
                continue
            h0, L = h[0]['f0'], sum(p['n'] for p in h)
            k = -(-L // K)
            splits = {h0 + L * j // k for j in range(1, k)}
            splits = {min(soft_edges, key=lambda e: abs(e - x)) if soft_edges and
                      abs(min(soft_edges, key=lambda e: abs(e - x)) - x) < 12 else x for x in splits}
            for p in h:
                cuts = sorted({p['f0'], p['f0'] + p['n']} | {x for x in splits if p['f0'] < x < p['f0'] + p['n']})
                for a, b in zip(cuts, cuts[1:]):
                    shots.append(dict(p, m0=p['m0'] + (a - p['f0']) * FPF, n=b - a, f0=a,
                                      soft=(a == p['f0'] and p is not h[0] and a not in splits)))
        looks = [(1.00, 1.08), (1.10, 1.02)]   # slow push in / slow pull out, alternating
        ci, look, first = 0, 0, True
        for s in shots:
            if s['gfx'] is None:
                if not first and not s['soft']:
                    ci ^= 1
                    look ^= 1
                first = False
            s['cam'], s['look'] = self.cams[ci % len(self.cams)], looks[look]
        run_, o = [], 0
        for s in shots + [dict(gfx='END', soft=False)]:
            if s['gfx'] is None and s['soft'] and run_:
                run_.append(s)
                continue
            if run_:
                L, o = sum(r['n'] for r in run_), 0
                for r in run_:
                    r['zo'], r['zL'] = o, L
                    o += r['n']
            run_ = [s] if s['gfx'] is None else []
        for i, s in enumerate(shots):
            s['prev'] = shots[i - 1] if s.get('soft') else None
        self.shots = shots

    # ---------------------------------------------------------------- pictures
    def plate(self, g: dict) -> Path:
        """Full-screen 1350x2400 still (zoomed, then scaled to 1080x1920) for a chart or photo."""
        from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
        imgs = g['image'] if isinstance(g['image'], list) else [g['image']]
        label = g.get('label')
        key = re.sub(r'\W', '_', '_'.join(Path(i).stem for i in imgs) + (label or '') + str(g.get('crop', '')))
        out = self.pr.work / 'plates' / f'{key}.png'
        if out.exists():
            return out
        out.parent.mkdir(parents=True, exist_ok=True)
        PW, PH = 1350, 2400
        if label is None:   # chart: extend its own paper colour to full screen
            c = Image.open(self.pr.p(imgs[0])).convert('RGB')
            im = Image.new('RGB', (PW, PH), c.getpixel((4, 4)))
            w = round(PW * 0.92)
            c = c.resize((w, round(w * c.height / c.width)), Image.LANCZOS)
            im.paste(c, ((PW - w) // 2, round(PH * 0.09)))
            im.save(out)
            return out
        srcs = [Image.open(self.pr.p(i)).convert('RGB') for i in imgs]
        if g.get('crop'):
            l, t, r, b = g['crop']
            srcs = [s.crop((int(s.width * l), int(s.height * t), int(s.width * r), int(s.height * b))) for s in srcs]
        if len(srcs) == 2:   # side by side, same height
            cw = (round(PW * 0.90) - 30) // 2
            ch = round(cw * 1.3)
            tiles = []
            for s in srcs:
                r = max(cw / s.width, ch / s.height)
                s = s.resize((round(s.width * r), round(s.height * r)), Image.LANCZOS)
                x0 = (s.width - cw) // 2
                tiles.append(s.crop((x0, 0, x0 + cw, ch)))
            photo = Image.new('RGB', (cw * 2 + 30, ch), (0, 0, 0))
            photo.paste(tiles[0], (0, 0))
            photo.paste(tiles[1], (cw + 30, 0))
            bg_src = tiles[0]
        else:
            photo = bg_src = srcs[0]
        r = max(PW / bg_src.width, PH / bg_src.height)
        bg = bg_src.resize((round(bg_src.width * r) + 2, round(bg_src.height * r) + 2), Image.LANCZOS)
        bx, by = (bg.width - PW) // 2, (bg.height - PH) // 2
        bg = ImageEnhance.Brightness(bg.crop((bx, by, bx + PW, by + PH)).filter(ImageFilter.GaussianBlur(40))).enhance(0.38)
        maxw, maxh = round(PW * 0.90), round(PH * 0.45)
        r = min(maxw / photo.width, maxh / photo.height)
        photo = photo.resize((round(photo.width * r), round(photo.height * r)), Image.LANCZOS)
        x0, y0 = (PW - photo.width) // 2, round(PH * 0.13) + (maxh - photo.height) // 2
        sh = Image.new('L', (PW, PH), 0)
        ImageDraw.Draw(sh).rounded_rectangle([x0, y0 + 14, x0 + photo.width, y0 + photo.height + 14], 24, fill=200)
        bg = Image.composite(Image.new('RGB', (PW, PH), (0, 0, 0)), bg, sh.filter(ImageFilter.GaussianBlur(28)))
        m = Image.new('L', photo.size, 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, photo.width - 1, photo.height - 1], 24, fill=255)
        bg.paste(photo, (x0, y0), m)
        d = ImageDraw.Draw(bg)
        size = 54
        while True:   # shrink a long label to fit
            f = ImageFont.truetype(brand.FONT_BOLD, size)
            bb = d.textbbox((PW // 2, 0), label, font=f, anchor='mt')
            if bb[2] - bb[0] < PW * 0.86 or size < 30:
                break
            size -= 2
        ly = y0 + photo.height + 48
        bb = d.textbbox((PW // 2, ly), label, font=f, anchor='mt')
        d.rounded_rectangle([bb[0] - 26, bb[1] - 16, bb[2] + 26, bb[3] + 18], 18, fill=(15, 15, 15))
        d.text((PW // 2, ly), label, font=f, fill=brand.WHITE, anchor='mt')
        bg.save(out)
        return out

    def render_shot(self, s, out: Path) -> bool:
        if s['gfx'] is not None:
            ins = ['-framerate', FPS, '-loop', '1', '-i', self.plate(s['gfx'])]
            flt = (f"[0:v]scale=out_color_matrix=bt709:out_range=tv,format=yuv444p,{zoom(1.0, 1.045, s['n'], 0.5, 0.45)},"
                   f"scale=1080:1920:flags=lanczos,format=yuv420p[v]")
        else:
            path, off, fx, fy = self.pr.camera(self.take, s['cam'])
            z0, z1 = s['look']
            cw = 1216   # the full-height 9:16 slice of the 4K frame, centred on the speaker
            x0 = max(0, min(3840 - cw, round(3840 * fx - cw / 2)))

            def chain(idx, lab):
                return (f"[{idx}:v]setpts=PTS-STARTPTS,crop={cw}:2160:{x0}:0,{zoom(z0, z1, s['zL'], 0.5, fy, s['zo'])},"
                        f"scale=1080:1920:flags=lanczos,{GRADE},vignette=angle=PI/7,format=yuv420p[{lab}]")
            ins = ['-ss', f"{s['m0'] + off:.4f}", '-i', path]
            if s['prev'] is None:
                flt = chain(0, 'v')
            else:   # soft cut: the outgoing footage runs on past the cut and dissolves into this piece
                p = s['prev']
                ins += ['-ss', f"{p['m0'] + p['n'] * FPF + off:.4f}", '-i', path]
                flt = (f"{chain(0, 'b')};{chain(1, 'a0')};[a0]trim=end_frame={SOFT_FRAMES}[a];"
                       f"[a][b]blend=all_expr='{blend_in(SOFT_FRAMES)}':shortest=0:repeatlast=1[v]")
        tmp = out.with_suffix('.tmp.mp4')
        if not run([FF, '-v', 'error', '-y', *ins, '-filter_complex', flt, '-map', '[v]', '-frames:v', str(s['n']),
                    '-an', *x264(tmp, crf=14)], str(out)):
            return False
        tmp.replace(out)
        return True

    # ---------------------------------------------------------------- captions
    def caption_words(self):
        W = []
        for g in self.pr.words(self.take):
            for s, e, w in g['words']:
                w = w.strip()
                if W and (w.startswith('-') or w.startswith(',0') or re.match(r'\.\d', w)):   # latter|-day, 85|,000, 7|.8
                    W[-1] = (W[-1][0], e, W[-1][2] + w)
                else:
                    W.append((s, e, w))
        out = []
        for s, e, w in W:
            # Whisper's word spans swallow the pause before a word, so the END time decides
            # whether a word is in a kept range; inside it, it goes to the piece it overlaps most
            if not any(a + 0.03 < e <= b + 0.06 for a, b in self.rng):
                continue
            c = max(self.clips, key=lambda c: (min(e, c['m0'] + c['n'] * FPF) - max(s, c['m0']),
                                               -abs((s + e) / 2 - c['m0'])))
            t0 = c['f0'] * FPF
            out.append([t0 + max(0, s - c['m0']), t0 + min(c['n'] * FPF, e - c['m0']), w])
        return apply_fixes(out, self.pr.cfg.get('caption_fixes', {}))

    def write_ass(self, path: Path):
        W = self.caption_words()
        shots = self.shots

        def layout_at(t):
            fr = int(t / FPF)
            s = next((s for s in shots if s['f0'] <= fr < s['f0'] + s['n']), shots[-1])
            if s['gfx'] is None:
                return brand.CAP_MARGIN['camera']
            return brand.CAP_MARGIN['chart' if s['gfx'].get('label') is None else 'photo']
        chunks, cur = [], []
        for i, w in enumerate(W):
            cur.append(w)
            nxt = W[i + 1] if i + 1 < len(W) else None
            if (nxt is None or len(cur) >= 3 or sum(len(x[2]) + 1 for x in cur) > 14 or re.search(r'[.,?!]$', w[2])
                    or nxt[0] - w[1] > 0.3 or layout_at(nxt[0]) != layout_at(w[0])):
                chunks.append(cur)
                cur = []
        ev = []
        for k, ch in enumerate(chunks):
            end = min(chunks[k + 1][0][0] if k + 1 < len(chunks) else ch[-1][1] + 0.4, ch[-1][1] + 0.6)
            mv = layout_at(ch[0][0])
            for j, (s, e, w) in enumerate(ch):
                t0 = ch[0][0] if j == 0 else s
                t1 = ch[j + 1][0] if j + 1 < len(ch) else end
                text = ' '.join((r'{\c' + brand.CAPTION_HIGHLIGHT + '}' + x[2].upper() + r'{\c&HFFFFFF&}') if jj == j
                                else x[2].upper() for jj, x in enumerate(ch))
                pop = r'{\fscx86\fscy86\t(0,90,\fscx100\fscy100)}' if j == 0 else ''
                ev.append(f"Dialogue: 0,{ass_t(t0)},{ass_t(t1)},Cap,,0,0,{mv},,{pop}{text}")
        if self.cfg.get('hook') and shots[0]['gfx'] is None:
            hook_end = min(3.2, next((s['f0'] * FPF for s in shots if s['gfx']), 99))
            ev.append(f"Dialogue: 1,{ass_t(0)},{ass_t(hook_end)},Hook,,0,0,0,,"
                      r"{\fad(120,250)}" + self.cfg['hook'].replace('\n', r'\N').upper())
        path.write_text(brand.ASS_HEADER + '\n'.join(ev) + '\n', encoding='utf-8')
        return W

    # ---------------------------------------------------------------- build
    def build(self, force: bool) -> Path:
        D = self.pr.work / 'shorts' / self.name
        D.mkdir(parents=True, exist_ok=True)
        self.write_ass(D / 'captions.ass')
        jobs = [(s, D / f's{i:03d}.mp4') for i, s in enumerate(self.shots)]
        with ThreadPoolExecutor(3) as ex:
            ok = list(ex.map(lambda so: so[1].exists() and not force or self.render_shot(*so), jobs))
        if not all(ok):
            raise SystemExit(f'{self.name}: some shots failed')
        parts = []
        for i, c in enumerate(self.clips):
            s0 = round(c['m0'] * 48000)
            parts.append(f"[0:a]atrim=start_sample={s0}:end_sample={s0 + c['n'] * SAMPLES_PER_FRAME},asetpts=N/SR/TB,"
                         f"afade=t=in:d=0.006,afade=t=out:st={c['n'] * FPF - 0.006:.4f}:d=0.006[a{i}]")
        chain = ';'.join(parts) + ';' + ''.join(f'[a{i}]' for i in range(len(self.clips))) + \
            f'concat=n={len(self.clips)}:v=0:a=1'
        fo = self.cfg.get('fade_out')
        master_voice(self.pr.mic(self.take), chain, D / 'audio.wav', lufs_mono=-17, total_s=self.nf * FPF,
                     fade_out=fo or 0.3)
        (D / 'shots.txt').write_text(''.join(f"file 's{i:03d}.mp4'\n" for i in range(len(self.shots))))
        out = self.pr.p(self.pr.cfg.get('shorts_dir', 'exports/shorts')) / (re.sub(r'[\\/:*?"<>|]', '', self.cfg['title']) + '.mp4')
        out.parent.mkdir(parents=True, exist_ok=True)
        vf = "[0:v]subtitles=filename='" + (D / 'captions.ass').as_posix().replace(':', '\\:') + "'"
        if fo:
            vf += f",fade=t=out:st={self.nf * FPF - fo:.3f}:d={fo}"
        run([FF, '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', D / 'shots.txt', '-i', D / 'audio.wav',
             '-filter_complex', vf + '[v]', '-map', '[v]', '-map', '1:a',
             '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-profile:v', 'high', '-pix_fmt', 'yuv420p',
             '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709',
             '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-movflags', '+faststart', out], self.name)
        return out


def apply_fixes(words: list, fixes: dict) -> list:
    """Caption spelling fixes from project.json "caption_fixes":
      words:   {"aryans": "Arians", ...}       one heard word -> correct spelling (lowercase key)
      phrases: [[["you're","asked","to","snow"], ["Erastus","Snow"]], ...]   heard -> said
      insert:  [["themselves", "May", "On"], ...]   add a word Whisper dropped between two words
    Captions are uppercased on screen, so these are about spelling, not case."""
    wmap = {k.lower(): v for k, v in fixes.get('words', {}).items()}
    for wd in words:
        k = wd[2].lower()
        core, tail = re.match(r"^(.*?)([.,?!]*)$", k).groups()
        if k in wmap:
            wd[2] = wmap[k]
        elif core in wmap:
            wd[2] = wmap[core] + ('' if wmap[core].endswith(tail) else tail)
    for said, fixed in fixes.get('phrases', []):
        said = [norm(x) for x in said]
        i = 0
        while i <= len(words) - len(said):
            if [norm(w[2]) for w in words[i:i + len(said)]] == said:
                t0, t1 = words[i][0], words[i + len(said) - 1][1]
                step = (t1 - t0) / len(fixed)
                tail = re.match(r"^.*?([.,?!]*)$", words[i + len(said) - 1][2]).group(1)   # keep "George,"
                fixed_t = fixed[:-1] + [fixed[-1] + ('' if fixed[-1].endswith(tail) else tail)]
                words[i:i + len(said)] = [[t0 + j * step, t0 + (j + 1) * step, w] for j, w in enumerate(fixed_t)]
                i += len(fixed)
            else:
                i += 1
    for before, after, word in fixes.get('insert', []):
        for i in range(1, len(words)):
            if norm(words[i][2]) == norm(after) and norm(words[i - 1][2]) == norm(before):
                words.insert(i, [words[i][0] - 0.16, words[i][0], word])
                break
    return words


def ass_t(t: float) -> str:
    t = max(0.0, t)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('project')
    ap.add_argument('names', help='comma-separated short names from project.json, or "all"')
    ap.add_argument('--plan', action='store_true')
    ap.add_argument('--force', action='store_true')
    a = ap.parse_args()
    pr = Project(a.project)
    names = list(pr.cfg['shorts']) if a.names == 'all' else a.names.split(',')
    for n in names:
        sh = Short(pr, n)
        kinds = [t[3] for t in sh.taken]
        holds = [s['n'] * FPF for s in sh.shots if s['gfx'] is None and not s['soft']]
        print(f"{n}: {sh.nf * FPF:.1f}s, {len(sh.shots)} shots, trims {len(sh.taken)} "
              f"(ums {sum(1 for t in sh.taken if t[2] == 'um')}; hidden {kinds.count('hidden')}, "
              f"angle change {kinds.count('hard')}, dissolve {kinds.count('soft')})", flush=True)
        if a.plan:
            for i, s in enumerate(sh.shots):
                what = (s['gfx'].get('label') or Path(str(s['gfx']['image'])).name) if s['gfx'] else \
                    f"{s['cam']} zoom {s['look']}{' (dissolve in)' if s['soft'] else ''}"
                print(f'  {i:2d} {s["f0"] * FPF:6.1f}s {s["n"] * FPF:5.1f}s  {what}')
            print('  captions:', ' '.join(w for *_, w in sh.caption_words()))
            continue
        print('done', sh.build(a.force), flush=True)


if __name__ == '__main__':
    main()

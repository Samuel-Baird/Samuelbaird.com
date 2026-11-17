"""Cold-open teaser for an interview long-form: a few strong lines flashed one after another to
build tension, then a title card, then (for a test) the opening seconds of the long-form.

    python tools/interview/teaser.py D:\\Videos\\<slug> [--no-tail]

project.json "teaser":
    clips:  [[from, to, "host"|"guest", "close"|"tight"|"side"|"wide"], ...]   mic seconds, in order
    title:  [small line, big line, accent line]
    tail:   seconds of the long-form to play after the title (test only; 0 = none)
    output: default exports/<slug> - teaser test.mp4
    final_output: default exports/<slug>.mp4 (--into-longform; set longform.output elsewhere,
            e.g. work/longform_body.mp4, so build.py doesn't write the same file)

Look: letterboxed 2.39:1, darker/cooler grade, each line opens with a 4-frame white flash and a
fast push-in; black beats between lines. Sound: everything is synthesised here (no library
music) -- a low drone and an accelerating sub pulse that build under the lines, a filtered-noise
riser into the title, an impact on every flash and a bigger one under the title.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build  # noqa: E402
from build import brand, FF, FPF, FPS, Project, x264, zoom  # noqa: E402
from build import run as _run  # noqa: E402


def run(cmd, label=''):
    if not _run(cmd, label):
        raise SystemExit(f'failed: {label}')
    return True

SR = 48000
LEAD, GAP, PRE_TITLE, TITLE = 14, 9, 14, 84   # frames: black open, black between lines, before title, title
FLASH = 4
BARS = 138                                     # 2.39:1 letterbox on 1080
LOOK = 'eq=contrast=1.12:saturation=0.82:brightness=-0.025:gamma=0.97,colorbalance=bs=0.04:bm=0.02'


def title_card(lines, out: Path):
    W, H = 1920, 1080
    im = Image.new('RGB', (W, H), (8, 8, 10))
    d = ImageDraw.Draw(im)
    small, big, accent = lines
    f1 = ImageFont.truetype(brand.FONT_BOLD, 34)
    f2 = ImageFont.truetype(brand.FONT_BLACK, 132)
    f3 = ImageFont.truetype(brand.FONT_BOLD, 40)
    d.text((W // 2, 392), small, font=f1, fill=(200, 200, 200), anchor='mm')
    d.text((W // 2, 520), big, font=f2, fill=brand.WHITE, anchor='mm')
    bb = d.textbbox((W // 2, 520), big, font=f2, anchor='mm')
    d.rectangle([W // 2 - 70, bb[3] + 34, W // 2 + 70, bb[3] + 40], fill=brand.ORANGE)
    d.text((W // 2, bb[3] + 92), accent, font=f3, fill=brand.ORANGE, anchor='mm')
    im.save(out)


# ------------------------------------------------------------------ sound design
def impact(n, big=False):
    t = np.arange(n) / SR
    f = 34 + (95 if big else 80) * np.exp(-t * 7)            # pitch drops fast: a body hit
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * (1.4 if big else 3.2))
    rng = np.random.default_rng(7 if big else 3)
    click = rng.normal(0, 1, n) * np.exp(-t * 60)
    lp = np.zeros(n)
    a = 0.08
    for i in range(1, min(n, SR // 4)):
        lp[i] = lp[i - 1] + a * (click[i] - lp[i - 1])
    return body * 0.9 + lp * 1.6


def score(total_n, hits, title_at, out: Path):
    """stereo float wav: drone + accelerating pulse building to the title, riser, impacts"""
    t = np.arange(total_n) / SR
    T = title_at / SR
    build_env = np.clip(t / T, 0, 1) ** 1.6 * (t < T)
    drone = (np.sin(2 * np.pi * 49 * t) + 0.6 * np.sin(2 * np.pi * 49.4 * t) + 0.35 * np.sin(2 * np.pi * 98.2 * t))
    drone *= (0.25 + 0.75 * build_env) * np.minimum(1, t / 1.2) * (t < T)
    # pulse: sub thumps, interval shrinking from 1.1 s to 0.42 s
    pulse = np.zeros(total_n)
    x = 0.4
    while x < T - 0.2:
        i = int(x * SR)
        k = min(int(0.16 * SR), total_n - i)
        tt = np.arange(k) / SR
        pulse[i:i + k] += np.sin(2 * np.pi * 52 * tt) * np.exp(-tt * 28) * (0.35 + 0.65 * x / T)
        x += 1.1 - 0.68 * (x / T)
    # riser: noise through a lowpass that opens up over the last 6 s before the title
    rng = np.random.default_rng(11)
    noise = rng.normal(0, 1, total_n)
    r0 = max(0, title_at - 6 * SR)
    riser = np.zeros(total_n)
    y = 0.0
    for i in range(r0, title_at):
        p = (i - r0) / (title_at - r0)
        a = 0.004 + 0.25 * p ** 2
        y += a * (noise[i] - y)
        riser[i] = y * (p ** 2.2) * 3.0
    hit = np.zeros(total_n)
    for h in hits:
        n = min(int(1.0 * SR), total_n - h)
        hit[h:h + n] += impact(n)[:n] * 0.8
    n = min(int(3.5 * SR), total_n - title_at)
    hit[title_at:title_at + n] += impact(n, big=True)[:n] * 1.25
    tail = np.zeros(total_n)   # a low ring under the title
    k = min(int(3.5 * SR), total_n - title_at)
    tt = np.arange(k) / SR
    tail[title_at:title_at + k] = (np.sin(2 * np.pi * 41 * tt) + 0.4 * np.sin(2 * np.pi * 82 * tt)) * np.exp(-tt * 0.9) * 0.35
    mono = drone * 0.10 + pulse * 0.45 + hit * 0.55 + tail
    side = riser * 0.22
    L, R = mono + side, mono - side * 0.6
    st = np.stack([L, R], 1)
    st *= 0.5 / max(1e-6, np.abs(st).max())   # peak -6 dBFS
    write_wav(out, st)


def write_wav(path: Path, x: np.ndarray):
    x = np.atleast_2d(x.T).T if x.ndim == 1 else x
    w = wave.open(str(path), 'wb')
    w.setnchannels(x.shape[1]), w.setsampwidth(2), w.setframerate(SR)
    w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
    w.close()


def read_mono(path: Path, a: float, b: float) -> np.ndarray:
    r = subprocess.run([FF, '-v', 'error', '-ss', f'{a:.4f}', '-t', f'{b - a:.4f}', '-i', str(path),
                        '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.float32).copy()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('project')
    ap.add_argument('--no-tail', action='store_true')
    ap.add_argument('--into-longform', action='store_true',
                    help='prepend the teaser to the built long-form (needs a finished build.py run)')
    a = ap.parse_args()
    pr = Project(a.project)
    cfg = pr.cfg['teaser']
    e = build.Edit(pr)
    D = pr.work / 'teaser'
    D.mkdir(parents=True, exist_ok=True)

    # ---- timeline (frames)
    items, f = [], LEAD
    for m0, m1, who, kind in cfg['clips']:
        n = round((m1 - m0) / FPF)
        items.append(dict(m0=m0, n=n, f0=f, who=who, kind=kind))
        f += n + GAP
    title_f = f - GAP + PRE_TITLE
    total_f = title_f + TITLE

    # ---- pictures
    parts = [D / 'black_lead.mp4']
    run([FF, '-v', 'error', '-y', '-f', 'lavfi', '-i', f'color=black:s=1920x1080:r={FPS}', '-frames:v', str(LEAD),
         *x264(parts[0])], 'lead')
    for i, it in enumerate(items):
        s = e.shot(it['kind'], it['who'], 0, 0)
        path, off, fx, fy = pr.camera(pr.cfg['longform']['take'], s['cam'])
        cx, cy = s['ctr'] or (fx, fy + s['dy'])
        z0 = s['z'][0]
        out = D / f'clip{i}.mp4'
        flt = (f"[0:v]setpts=PTS-STARTPTS,{zoom(z0, z0 + 0.09, it['n'], cx, cy, 0, center_y=True)},"
               f"scale=1920:1080:flags=lanczos,{LOOK},vignette=angle=PI/5,"
               f"drawbox=x=0:y=0:w=iw:h={BARS}:color=black:t=fill,drawbox=x=0:y=ih-{BARS}:w=iw:h={BARS}:color=black:t=fill,"
               f"fade=t=in:s=0:n={FLASH}:color=white,format=yuv420p[v]")
        run([FF, '-v', 'error', '-y', '-ss', f"{it['m0'] + off:.4f}", '-i', path, '-filter_complex', flt,
             '-map', '[v]', '-frames:v', str(it['n']), '-an', *x264(out)], f'clip {i}')
        parts.append(out)
        gap = D / f'gap{i}.mp4'
        g = GAP if i + 1 < len(items) else PRE_TITLE
        run([FF, '-v', 'error', '-y', '-f', 'lavfi', '-i', f'color=black:s=1920x1080:r={FPS}', '-frames:v', str(g),
             *x264(gap)], 'gap')
        parts.append(gap)
    card = D / 'title.png'
    title_card(cfg['title'], card)
    tv = D / 'title.mp4'
    run([FF, '-v', 'error', '-y', '-framerate', FPS, '-loop', '1', '-i', card, '-filter_complex',
         f"[0:v]format=yuv444p,{zoom(1.0, 1.04, TITLE, 0.5, 0.48)},scale=1920:1080,"
         f"fade=t=in:s=0:n=6:color=white,fade=t=out:s={TITLE - 20}:n=20,format=yuv420p[v]",
         '-map', '[v]', '-frames:v', str(TITLE), *x264(tv)], 'title')
    parts.append(tv)
    lst = D / 'parts.txt'
    lst.write_text(''.join(f"file '{p.as_posix()}'\n" for p in parts))

    # ---- sound: lines from the auto-mix through the voice chain, over the score
    mix = e.automix()
    total_n = total_f * 2002
    dlg = np.zeros(total_n, np.float32)
    for it in items:
        x = read_mono(mix, it['m0'], it['m0'] + it['n'] * FPF)[:it['n'] * 2002]
        r = min(len(x), int(0.012 * SR))
        x[:r] *= np.linspace(0, 1, r)
        x[-r:] *= np.linspace(1, 0, r)
        i0 = it['f0'] * 2002
        dlg[i0:i0 + len(x)] += x
    write_wav(D / 'dialogue_raw.wav', dlg)
    score(total_n, [it['f0'] * 2002 for it in items], title_f * 2002, D / 'score.wav')
    voice = ('highpass=f=80,equalizer=f=250:t=q:w=1.2:g=-1.5,equalizer=f=4500:t=q:w=1.5:g=1.5,'
             'acompressor=threshold=-24dB:ratio=3:attack=10:release=150:makeup=3,'
             'loudnorm=I=-17:TP=-3:LRA=7,aresample=48000,pan=stereo|c0=c0|c1=c0')
    fc = f"[0:a]{voice}[d];[1:a]volume=0.9[s];[d][s]amix=inputs=2:normalize=0:duration=longest"
    pre = D / 'teaser_mix_pre.wav'
    subprocess.run([FF, '-v', 'error', '-y', '-i', D / 'dialogue_raw.wav', '-i', D / 'score.wav', '-filter_complex', fc,
                    '-c:a', 'pcm_s24le', pre], check=True)
    r = subprocess.run([FF, '-hide_banner', '-i', pre, '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json',
                        '-f', 'null', '-'], capture_output=True, text=True)
    import json
    j = json.loads(r.stderr[r.stderr.rindex('{'):r.stderr.rindex('}') + 1])
    ln = (f"loudnorm=I=-16:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:"
          f"measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    aud = D / 'teaser_mix.wav'
    subprocess.run([FF, '-v', 'error', '-y', '-i', pre, '-af', f'{ln},aresample=48000,atrim=end_sample={total_n}',
                    '-c:a', 'pcm_s24le', aud], check=True)

    if a.into_longform:
        # the teaser's own units + the long-form's units (same x264 settings, so stream copy),
        # with one continuous audio track: teaser mix then the long-form master
        units = (pr.work / 'units.txt').read_text().splitlines()
        full = D / 'with_longform.txt'
        full.write_text(lst.read_text() + '\n'.join(units) + '\n')
        wav = D / 'with_longform.wav'
        subprocess.run([FF, '-v', 'error', '-y', '-i', aud, '-i', pr.work / 'audio' / 'longform_master.wav',
                        '-filter_complex', '[0:a][1:a]concat=n=2:v=0:a=1', '-c:a', 'pcm_s24le', wav], check=True)
        out = pr.p(cfg.get('final_output', f"exports/{pr.cfg['slug']}.mp4"))
        run([FF, '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', full, '-i', wav, '-map', '0:v', '-map', '1:a',
             '-c:v', 'copy', '-c:a', 'aac', '-b:a', '320k', '-ar', '48000', '-movflags', '+faststart', out], 'final')
        print(f'teaser {total_f * FPF:.1f}s + long-form -> {out}  (long-form starts at {total_f * FPF:.2f}s)')
        return

    # ---- assemble (+ the long-form's opening, so the hand-off can be judged)
    out = pr.p(cfg.get('output', f"exports/{pr.cfg['slug']} - teaser test.mp4"))
    tail = 0 if a.no_tail else float(cfg.get('tail', 10))
    lf = pr.p(pr.cfg['longform'].get('output', f"exports/{pr.cfg['slug']}.mp4"))
    ins = ['-f', 'concat', '-safe', '0', '-i', lst, '-i', aud]
    if tail:
        ins += ['-t', f'{tail:.3f}', '-i', lf]
        fc = '[0:v][1:a][2:v][2:a]concat=n=2:v=1:a=1[v][a]'
    else:
        fc = '[0:v]null[v];[1:a]anull[a]'
    run([FF, '-v', 'error', '-y', *ins, '-filter_complex', fc, '-map', '[v]', '-map', '[a]',
         '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-r', FPS,
         '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709',
         '-c:a', 'aac', '-b:a', '320k', '-ar', '48000', '-movflags', '+faststart', out], 'teaser')
    print(f'teaser {total_f * FPF:.1f}s (+{tail:.0f}s of the long-form) -> {out}')


if __name__ == '__main__':
    main()

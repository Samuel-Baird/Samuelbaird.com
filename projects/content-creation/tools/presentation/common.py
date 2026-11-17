"""Shared plumbing for the presentation pipeline (docs/types/presentation.md).

Everything project-specific lives in the project's ``project.json``; paths in it are
relative to the project root (``D:\\Videos\\<slug>``) unless absolute. Times are seconds
on the *mic* clock of a take; ``sync.py`` writes each camera's offset
(camera_time = mic_time + offset).
"""
from __future__ import annotations

import glob
import json
import os
import re
import shutil
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

FPF = 1001 / 24000          # one frame at 23.976 fps (the cameras' rate)
FPS = '24000/1001'
SAMPLES_PER_FRAME = 2002    # 48 kHz audio: exactly 2002 samples per frame at 23.976
GRADE = 'eq=contrast=1.05:saturation=1.08:gamma=0.99'
FILLERS = ('um', 'uh', 'umm', 'uhm', 'uhh', 'ah', 'er', 'hmm', 'mm')


def ffmpeg(tool: str = 'ffmpeg') -> str:
    """ffmpeg/ffprobe: PATH first, then the winget install (Gyan.FFmpeg) location."""
    found = shutil.which(tool)
    if found:
        return found
    hits = glob.glob(os.path.expandvars(
        r'%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg*\ffmpeg-*\bin\\' + tool + '.exe'))
    if hits:
        return hits[0]
    sys.exit(f'{tool} not found: winget install --id Gyan.FFmpeg -e')


FF = ffmpeg()


class Project:
    def __init__(self, path: str | Path):
        path = Path(path)
        self.file = path if path.suffix == '.json' else path / 'project.json'
        self.cfg = json.loads(self.file.read_text(encoding='utf-8'))
        self.root = Path(self.cfg.get('root') or self.file.parent)
        self.work = self.p(self.cfg.get('work_dir', 'work'))
        self.work.mkdir(parents=True, exist_ok=True)

    def p(self, rel: str | Path) -> Path:
        rel = Path(rel)
        return rel if rel.is_absolute() else self.root / rel

    def save(self) -> None:
        self.file.write_text(json.dumps(self.cfg, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    # ---- takes
    def take(self, k) -> dict:
        return self.cfg['takes'][str(k)]

    def mic(self, k) -> Path:
        return self.p(self.take(k)['mic'])

    def camera(self, k, cam) -> tuple[Path, float, float, float]:
        """(file, offset, face_x, face_y) for a camera of a take."""
        c = self.take(k)['cameras'][cam]
        if c.get('offset') is None:
            sys.exit(f'take {k} camera {cam}: no offset yet, run sync.py first')
        return self.p(c['file']), float(c['offset']), c['face'][0], c['face'][1]

    def cameras(self, k) -> list[str]:
        return list(self.take(k)['cameras'])

    # ---- analysis files written by transcribe.py
    def words(self, k) -> list[dict]:
        return json.loads((self.work / f'transcripts/take{k}.json').read_text(encoding='utf-8'))

    def fillers(self, k) -> list[list]:
        f = self.work / f'transcripts/take{k}.fillers.json'
        return json.loads(f.read_text(encoding='utf-8')) if f.exists() else []

    def wav16k(self, k) -> Path:
        return self.work / f'audio/take{k}_16k.wav'

    def silences(self, k, d=0.35) -> list[tuple[float, float]]:
        """silencedetect on the mic (-42 dB, >= d s), cached per take."""
        cache = self.work / f'audio/take{k}_silences_{d}.txt'
        if not cache.exists():
            r = subprocess.run([FF, '-hide_banner', '-i', str(self.mic(k)), '-af',
                                f'highpass=f=100,silencedetect=noise=-42dB:d={d}', '-f', 'null', '-'],
                               capture_output=True, text=True)
            ts = [float(x) for x in re.findall(r'silence_(?:start|end): ([0-9.]+)', r.stderr)]
            cache.parent.mkdir(parents=True, exist_ok=True)
            cache.write_text(''.join(f'{a:.3f} {b:.3f}\n' for a, b in zip(ts[::2], ts[1::2])))
        return [tuple(map(float, l.split())) for l in cache.read_text().splitlines() if l.strip()]


_ENV: dict = {}


def envelope(wav16k: Path) -> np.ndarray:
    """10 ms RMS level (dB, 16-bit scale) of a 16 kHz mono wav: speech ~45-65, room tone ~20."""
    key = str(wav16k)
    if key not in _ENV:
        w = wave.open(key)
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32)
        n = len(x) // 160
        _ENV[key] = 20 * np.log10(np.sqrt((x[:n * 160].reshape(n, 160) ** 2).mean(1)) + 1)
    return _ENV[key]


def quiet(env: np.ndarray, t: float, thr: float = 34) -> bool:
    i = int(t * 100)
    return env[max(0, i - 1):i + 2].max() < thr


def zoom(z0, z1, n, cx, cy, o=0, center_y=False) -> str:
    """Slow push/pull as a perspective warp. The corners land on sub-pixel positions, so the move
    is smooth; ffmpeg's zoompan rounds the crop to whole pixels, which visibly judders on slow
    zooms (measured: ~0.3 px frame-to-frame wobble vs ~0.03 px here). o = frames already into a
    zoom that runs over n frames. cy anchors the face: center_y=False keeps the point at cy fixed
    in place, True centres the crop on it."""
    z = f"min(2,max(1,{z0}+({z1}-{z0})*(in+{o})/{n}))"
    x = f"max(0,min(W-W/{z},W*{cx}-W/{z}/2))"
    y = (f"max(0,min(H-H/{z},H*{cy}-H/{z}/2))" if center_y else
         f"max(0,min(H-H/{z},H*{cy}-H/{z}*{cy}))")
    return (f"perspective=x0='{x}':y0='{y}':x1='{x}+W/{z}':y1='{y}':x2='{x}':y2='{y}+H/{z}':"
            f"x3='{x}+W/{z}':y3='{y}+H/{z}':interpolation=cubic:eval=frame")


def blend_in(n_frames: int) -> str:
    """blend expression: smoothstep from input A to input B over n_frames."""
    p = f"min(1,N/{max(1, n_frames - 1)})"
    return f"A+(B-A)*(3*pow({p},2)-2*pow({p},3))"


def run(cmd: list, label: str = '') -> bool:
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True)
    if r.returncode:
        print('FAIL', label, r.stderr[-1500:], flush=True)
        return False
    return True


def x264(out: Path, crf: int = 17, preset: str = 'medium') -> list:
    return ['-c:v', 'libx264', '-preset', preset, '-crf', str(crf), '-profile:v', 'high', '-pix_fmt', 'yuv420p',
            '-r', FPS, '-video_track_timescale', '24000', '-colorspace', 'bt709', '-color_primaries', 'bt709',
            '-color_trc', 'bt709', '-color_range', 'tv', str(out)]


def master_voice(mic: Path, chain: str, out: Path, lufs_mono: float, total_s: float,
                 fade_in: float = 0.0, fade_out: float = 0.3) -> None:
    """Voice master: rumble cut, slight mud dip and presence lift, gentle compression, then
    two-pass loudnorm. The mic is mono and gets duplicated to both channels, which reads 3 LU
    louder as stereo, so pass the *mono* target: -19 for -16 LUFS long-form, -17 for -14 LUFS
    shorts. `chain` is a filter_complex that ends on the mic signal (no output label)."""
    voice = (',highpass=f=80,equalizer=f=250:t=q:w=1.2:g=-1.5,equalizer=f=4500:t=q:w=1.5:g=1.5,'
             'acompressor=threshold=-24dB:ratio=2.5:attack=15:release=200:makeup=2')
    r = subprocess.run([FF, '-hide_banner', '-i', str(mic), '-filter_complex',
                        chain + voice + f',loudnorm=I={lufs_mono}:TP=-1.5:LRA=8:print_format=json', '-f', 'null', '-'],
                       capture_output=True, text=True)
    j = json.loads(r.stderr[r.stderr.rindex('{'):r.stderr.rindex('}') + 1])
    ln = (f"loudnorm=I={lufs_mono}:TP=-1.5:LRA=8:measured_I={j['input_i']}:measured_TP={j['input_tp']}"
          f":measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    fades = (f',afade=t=in:d={fade_in}' if fade_in else '') + f',afade=t=out:st={total_s - fade_out:.3f}:d={fade_out}'
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([FF, '-v', 'error', '-y', '-i', str(mic), '-filter_complex',
                    chain + voice + f',{ln},aresample=48000{fades},pan=stereo|c0=c0|c1=c0',
                    '-c:a', 'pcm_s24le', str(out)], check=True)

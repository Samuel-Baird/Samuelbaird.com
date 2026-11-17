"""Sync every camera of every take to that take's external mic and write the offsets into
project.json (camera_time = mic_time + offset).

    python tools/presentation/sync.py D:\\Videos\\<slug>

Cross-correlates 8 kHz mono copies of the camera scratch audio against the mic (PHAT-weighted
FFT correlation), then re-measures on a 30 s window near the start and near the end of each
take to check for drift. Expect a peak ratio well above 3 and start/end agreeing within a
couple of milliseconds; anything else gets a warning and needs a look before building.
"""
from __future__ import annotations

import subprocess
import sys
import wave

import numpy as np

from common import FF, Project

SR = 8000


def load(path) -> np.ndarray:
    w = wave.open(str(path))
    x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32)
    return x / (np.abs(x).max() + 1)


def lag(ref: np.ndarray, other: np.ndarray) -> tuple[float, float]:
    """seconds to add to `other`'s clock to get `ref`'s, and a peak-sharpness ratio"""
    n = 1 << int(np.ceil(np.log2(len(ref) + len(other))))
    X = np.fft.rfft(ref, n) * np.conj(np.fft.rfft(other, n))
    c = np.fft.irfft(X / (np.abs(X) + 1e-9), n)
    k = int(np.argmax(c))
    if k > n // 2:
        k -= n
    return k / SR, float(c.max() / (np.sort(c)[-50] + 1e-12))


def main() -> None:
    pr = Project(sys.argv[1])
    tmp = pr.work / 'audio'
    tmp.mkdir(parents=True, exist_ok=True)
    for k in pr.cfg['takes']:
        mic8 = tmp / f'take{k}_mic_8k.wav'
        subprocess.run([FF, '-v', 'error', '-y', '-i', pr.mic(k), '-ac', '1', '-ar', str(SR), '-c:a', 'pcm_s16le', mic8],
                       check=True)
        m = load(mic8)
        for cam, c in pr.take(k)['cameras'].items():
            cam8 = tmp / f'take{k}_{cam}_8k.wav'
            subprocess.run([FF, '-v', 'error', '-y', '-i', pr.p(c['file']), '-map', '0:a:0', '-ac', '1', '-ar', str(SR),
                            '-c:a', 'pcm_s16le', cam8], check=True)
            v = load(cam8)
            off, pk = lag(m, v)          # mic_time = cam_time + off
            checks = []
            for start in (min(60, len(v) / SR / 4), len(v) / SR - 90):
                if start < 0:
                    continue
                cs = v[int(start * SR):int((start + 30) * SR)]
                m0 = max(0, int((start + off - 2) * SR))
                lo, p2 = lag(m[m0:m0 + 34 * SR], cs)
                if p2 > 3:
                    checks.append(m0 / SR + lo - start)
            c['offset'] = round(-off, 4)  # stored as camera_time = mic_time + offset
            drift = (max(checks) - min(checks)) * 1000 if len(checks) > 1 else float('nan')
            warn = '' if pk > 3 and (drift != drift or drift < 5) else '   <-- CHECK THIS'
            print(f'take {k} cam {cam}: offset {c["offset"]:+.4f}s  peak {pk:.1f}  drift {drift:.1f} ms{warn}')
    pr.save()


if __name__ == '__main__':
    main()

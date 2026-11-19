"""Speak each Deseret letter with Kokoro: the letter's name, then its key word.

    python scripts/letter-audio.py            # writes public/audio/letters/00.mp3 ... 39.mp3

Vowel letters are named by their sound, consonants by sound + vowel ("pee", "ef"), as in the
1868 primers. Names are given to Kokoro as phonemes (misaki's [text](/phonemes/) syntax) so the
sound is exact rather than guessed from spelling; the key word is read normally.
Setup (Python 3.12, ffmpeg and espeak-ng): see scripts/requirements-audio.txt. Output is committed;
re-run only to change it, e.g. `python scripts/letter-audio.py 38 39` for just Oi and Ew.
"""
import os, subprocess, sys, tempfile
import numpy as np
import soundfile as sf


def use_system_espeak():
    # The espeak-ng bundled with espeakng-loader points at its build machine's data folder on macOS
    # and fails; use Homebrew's (brew install espeak-ng) when it is there.
    for lib, data in (('/opt/homebrew/lib/libespeak-ng.dylib', '/opt/homebrew/share/espeak-ng-data'),
                      ('/usr/local/lib/libespeak-ng.dylib', '/usr/local/share/espeak-ng-data')):
        if os.path.exists(lib) and os.path.isdir(data):
            from phonemizer.backend.espeak.wrapper import EspeakWrapper
            os.environ.setdefault('ESPEAK_DATA_PATH', data)
            EspeakWrapper.set_library(lib)
            EspeakWrapper.set_data_path(data)
            return


use_system_espeak()
from kokoro import KPipeline  # noqa: E402  (after the espeak fix)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'public', 'audio', 'letters')
VOICE = 'af_heart'
SR = 24000

# (name, phonemes for the name, key word) in Unicode order, U+10400 onward. Keep in step with
# LETTERS in src/pages/index.astro. Phonemes use misaki's US set (A = eɪ, I = aɪ, O = oʊ, W = aʊ, Y = ɔɪ).
LETTERS = [
    ('Long I', 'ˈi', 'eat'), ('Long E', 'ˈA', 'ate'), ('Long A', 'ˈɑ', 'art'), ('Long Ah', 'ˈɔ', 'aught'),
    ('Long O', 'ˈO', 'oat'), ('Long Oo', 'ˈu', 'ooze'), ('Short I', 'ˈɪ', 'it'), ('Short E', 'ˈɛ', 'egg'),
    ('Short A', 'ˈæ', 'at'), ('Short Ah', 'ˈɒ', 'odd'), ('Short O', 'ˈʌ', 'up'), ('Short Oo', 'ˈʊ', 'book'),
    ('Ay', 'ˈI', 'ice'), ('Ow', 'ˈW', 'owl'), ('Wu', 'wˈu', 'woe'), ('Yee', 'jˈi', 'ye'), ('H', 'ˈAʧ', 'hay'),
    ('Pee', 'pˈi', 'pay'), ('Bee', 'bˈi', 'bee'), ('Tee', 'tˈi', 'tea'), ('Dee', 'dˈi', 'day'),
    ('Chee', 'ʧˈi', 'cheese'), ('Jee', 'ʤˈi', 'jay'), ('Kay', 'kˈA', 'key'), ('Gay', 'ɡˈA', 'gay'),
    ('Ef', 'ˈɛf', 'fee'), ('Vee', 'vˈi', 'vie'), ('Eth', 'ˈɛθ', 'thigh'), ('Thee', 'ðˈi', 'thy'),
    ('Es', 'ˈɛs', 'sea'), ('Zee', 'zˈi', 'zeal'), ('Esh', 'ˈɛʃ', 'she'), ('Zhee', 'ʒˈi', 'vision'),
    ('Er', 'ˈɜɹ', 'ray'), ('El', 'ˈɛl', 'lay'), ('Em', 'ˈɛm', 'may'), ('En', 'ˈɛn', 'nay'), ('Eng', 'ˈɛŋ', 'sing'),
    ('Oi', 'ˈY', 'boy'), ('Ew', 'jˈu', 'few'),
]


def speak(pipe, text):
    chunks = [r.audio.numpy() for r in pipe(text, voice=VOICE, speed=0.9) if r.audio is not None]
    return np.concatenate(chunks) if chunks else np.zeros(0, dtype=np.float32)


def trim(a, thresh=0.01, pad=0.04):
    idx = np.where(np.abs(a) > thresh)[0]
    if not len(idx):
        return a
    p = int(pad * SR)
    return a[max(0, idx[0] - p): idx[-1] + p]


def main():
    only = {int(x) for x in sys.argv[1:]}
    os.makedirs(OUT, exist_ok=True)
    pipe = KPipeline(lang_code='a', repo_id='hexgrad/Kokoro-82M')
    gap = np.zeros(int(0.32 * SR), dtype=np.float32)
    for i, (name, ph, word) in enumerate(LETTERS):
        if only and i not in only:
            continue
        a = trim(speak(pipe, f'[{name}](/{ph}/).'))
        b = trim(speak(pipe, f'{word}.'))
        audio = np.concatenate([a, gap, b]).astype(np.float32)
        audio *= 0.9 / max(1e-6, np.abs(audio).max())
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as t:
            wav = t.name
        sf.write(wav, audio, SR)
        mp3 = os.path.join(OUT, f'{i:02d}.mp3')
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', wav, '-ac', '1', '-b:a', '48k', mp3], check=True)
        os.remove(wav)
        print(f'{i:02d} {name:9s} /{ph}/ {word}  {len(audio) / SR:.2f}s')


if __name__ == '__main__':
    main()

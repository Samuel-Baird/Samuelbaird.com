#!/usr/bin/env python3
"""Cut quote clips from a long YouTube stream into one 1080x1920 story video.

Pipeline: download a window around each timestamp (yt-dlp) -> transcribe with
Whisper word timestamps -> locate the quote in the transcript -> cut, scale to
9:16, burn a header plus word-synced captions -> append a caption-free still
image held for 10 s -> concatenate.

Usage (from a folder you don't mind filling with intermediates):
    python make_pastor_clips.py --image "C:\\Users\\b13ll\\Downloads\\Your paragraph text (1).png" \\
        --workdir D:\\Videos\\freedom-house --cookies-from-browser chrome

YouTube blocks anonymous downloads from datacenter IPs; on a home machine
--cookies-from-browser is usually only needed if you hit "confirm you're not a
bot". Requires ffmpeg and yt-dlp on PATH and openai-whisper installed.
"""
from __future__ import annotations

import argparse
import difflib
import re
import subprocess
import sys
from pathlib import Path

URL = "https://www.youtube.com/live/zwki5-eFpzA"
HEADER = "Pastor Aaron Simpson of Freedom House Church"
W, H, FPS = 1080, 1920, 30
IMAGE_SECONDS = 10
PAD_BEFORE, PAD_AFTER = 60, 90  # seconds of stream downloaded around each timestamp

# (label, hh:mm:ss given by the user, quote text used to find the exact words)
CLIPS = [
    ("a", "3:15:38", "if Joseph Smith was alive in the Old Testament, it would have been glorious and beautiful to beat him to death with rocks"),
    ("c", "3:26:32", "You don't have a glorified body. That receding hairline says you don't have a glorified body right now"),
    ("e", "3:35:19", "if you were to die today, you would rightly and justly go to hell"),
    ("b", "3:38:22", "So yeah, Joseph Smith preaches a false god because he is a con man pedophile thief. And historical fact I shared this with Hayden yesterday. I'm from the city of the dude who killed him"),
    ("d", "3:39:07", "God hates you"),
]  # chronological order in the stream


def hms(s: str) -> int:
    h, m, sec = (int(x) for x in s.split(":"))
    return h * 3600 + m * 60 + sec


def run(cmd: list[str], cwd: Path | None = None) -> None:
    print("+", " ".join(f'"{c}"' if " " in c else c for c in cmd))
    subprocess.run(cmd, cwd=cwd, check=True)


def download_window(label: str, ts: int, workdir: Path, cookies: str | None) -> tuple[Path, int]:
    start = max(0, ts - PAD_BEFORE)
    out = workdir / f"win_{label}.mp4"
    if not out.exists():
        cmd = [
            "yt-dlp", "-f", "bv*[height<=1920][ext=mp4]+ba[ext=m4a]/b",
            "--download-sections", f"*{start}-{ts + PAD_AFTER}",
            "--force-keyframes-at-cuts", "--merge-output-format", "mp4",
            "-o", str(out), URL,
        ]
        if cookies:
            cmd[1:1] = ["--cookies-from-browser", cookies]
        run(cmd)
    return out, start


def norm(w: str) -> str:
    return re.sub(r"[^a-z0-9']", "", w.lower())


def find_quote(words: list[dict], quote: str) -> tuple[int, int, float]:
    """Best-matching word span [i, j] for the quote, plus its similarity."""
    q = [norm(w) for w in quote.split() if norm(w)]
    toks = [norm(w["word"]) for w in words]
    best = (0, 0, 0.0)
    for n in range(max(1, len(q) - 4), len(q) + 5):
        for i in range(0, max(1, len(toks) - n + 1)):
            r = difflib.SequenceMatcher(None, q, toks[i:i + n]).ratio()
            if r > best[2]:
                best = (i, min(i + n, len(toks)) - 1, r)
    return best


def ass_time(t: float) -> str:
    cs = int(round(t * 100))
    return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"


def build_ass(path: Path, words: list[dict], clip_start: float, clip_end: float) -> None:
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Header,Arial,52,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,3,10,0,8,60,60,150,1
Style: Cap,Arial,74,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,6,2,2,70,70,420,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
    lines = [f"Dialogue: 0,{ass_time(0)},{ass_time(clip_end - clip_start)},Header,,0,0,0,,{HEADER}"]
    chunk: list[dict] = []

    def flush() -> None:
        if not chunk:
            return
        s = max(0.0, chunk[0]["start"] - clip_start)
        e = min(clip_end - clip_start, chunk[-1]["end"] - clip_start + 0.15)
        text = " ".join(w["word"].strip() for w in chunk).replace("\n", " ")
        lines.append(f"Dialogue: 0,{ass_time(s)},{ass_time(e)},Cap,,0,0,0,,{text}")
        chunk.clear()

    for w in words:
        if w["end"] < clip_start or w["start"] > clip_end:
            continue
        chunk.append(w)
        if len(chunk) >= 4 or w["word"].strip().endswith((".", "?", "!", ",")):
            flush()
    flush()
    path.write_text(head + "\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--image", type=Path, required=True)
    ap.add_argument("--workdir", type=Path, required=True)
    ap.add_argument("--out", default="story.mp4")
    ap.add_argument("--model", default="small.en")
    ap.add_argument("--cookies-from-browser", default=None, help="e.g. chrome, firefox, edge")
    ap.add_argument("--lead", type=float, default=0.3, help="seconds kept before the first quoted word")
    ap.add_argument("--tail", type=float, default=0.6, help="seconds kept after the last quoted word")
    ap.add_argument("--source", type=Path, help="skip download; use this folder of win_<label>.mp4 files")
    args = ap.parse_args()

    work = args.workdir.resolve()
    work.mkdir(parents=True, exist_ok=True)
    if not args.image.exists():
        print(f"error: image not found: {args.image}", file=sys.stderr)
        return 1

    import whisper  # imported late so --help works without it
    model = whisper.load_model(args.model)

    parts: list[str] = []
    for label, stamp, quote in CLIPS:
        ts = hms(stamp)
        if args.source:
            win, win_start = args.source / f"win_{label}.mp4", max(0, ts - PAD_BEFORE)
        else:
            win, win_start = download_window(label, ts, work, args.cookies_from_browser)

        res = model.transcribe(str(win), word_timestamps=True, language="en")
        words = [w for seg in res["segments"] for w in seg["words"]]
        i, j, score = find_quote(words, quote)
        if score < 0.6:
            print(f"WARNING [{label} {stamp}] quote not found (best match {score:.2f}); "
                  f"using {stamp} -2s/+12s. Check this clip by hand.")
            cs, ce = max(0, ts - win_start - 2.0), ts - win_start + 12.0
        else:
            cs, ce = max(0.0, words[i]["start"] - args.lead), words[j]["end"] + args.tail
            print(f"[{label} {stamp}] match {score:.2f}: {' '.join(w['word'].strip() for w in words[i:j+1])}")

        ass = work / f"cap_{label}.ass"
        build_ass(ass, words, cs, ce)
        seg = f"seg_{label}.mp4"
        vf = (f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
              f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:black,setsar=1,fps={FPS},"
              f"subtitles={ass.name}")
        run(["ffmpeg", "-y", "-ss", f"{cs:.3f}", "-to", f"{ce:.3f}", "-i", str(win),
             "-vf", vf, "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", seg], cwd=work)
        parts.append(seg)

    # Caption-free still, 10 s, silent audio so concat stays in sync.
    run(["ffmpeg", "-y", "-loop", "1", "-t", str(IMAGE_SECONDS), "-framerate", str(FPS), "-i", str(args.image.resolve()),
         "-f", "lavfi", "-t", str(IMAGE_SECONDS), "-i", "anullsrc=r=48000:cl=stereo",
         "-vf", f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:black,setsar=1,format=yuv420p",
         "-c:v", "libx264", "-crf", "18", "-c:a", "aac", "-b:a", "192k", "-shortest", "seg_image.mp4"], cwd=work)
    parts.append("seg_image.mp4")

    (work / "concat.txt").write_text("".join(f"file '{p}'\n" for p in parts), encoding="utf-8")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "concat.txt", "-c", "copy", args.out], cwd=work)
    print(f"\nDone: {work / args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

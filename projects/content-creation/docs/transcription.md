# Transcription

## Backend

Local `openai-whisper` CLI (installed at
`C:\Users\b13ll\AppData\Local\Programs\Python\Python312\Scripts\whisper.exe`).
Models cached locally: `base.en`, `base`, `small.en`. No GPU/CUDA on this
machine (AMD integrated graphics) — transcription runs on CPU, so budget
real time roughly on the order of the audio's own length for `small.en`
(slower than realtime; `base.en` is faster but less accurate — default to
`small.en` unless a project is time-critical).

**Presentation type uses `faster-whisper` instead** (`tools/presentation/
transcribe.py`, model `medium.en`, int8 on CPU): same Whisper weights, about
4× faster on this machine, word timestamps built in, and it runs the second
"disfluent" pass that writes out ums for the shorts' filler trimming. Medium
catches names the small model mangles; the rest still get a caption fix-up
list. Either backend is fine for the other types.

## The "~90 second limit" — investigated, not reproduced locally

The user recalled a ~90-second constraint from a past session but couldn't
pin down its source. Checked directly on this machine (2026-09-08):

- **Local Whisper CLI has no such cap.** Its internal window is 30 seconds
  per inference chunk, and it stitches long-form audio across chunks
  automatically — a full-length file transcribes in one invocation with no
  manual chunking required. This is almost certainly what the pipeline
  should keep using by default.
- The limit the user remembers is most likely a property of either **the
  hosted OpenAI Whisper API** (which does impose file-size/duration-driven
  practical limits and bills per request) or **DaVinci Resolve's built-in
  transcription** (which, separately, cannot use Whisper at all — the
  Resolve scripting API only exposes its own built-in speech-recognition
  engine, with no provider selection; see `resolve-mcp-gotchas.md`).
- **Action:** this pipeline uses the local CLI, not Resolve's built-in
  transcription and not a hosted API, so the limit doesn't apply as
  currently designed. If a future project needs the hosted API (e.g. for
  speed on a very long file), split first with
  `ffmpeg -i input.wav -f segment -segment_time 600 -c copy chunk_%02d.wav`
  (10-minute chunks, safely under any API duration cap) and offset each
  chunk's word/segment timestamps by its start time before merging.

## Invocation

```bash
whisper "SOURCE_AUDIO" \
  --model small.en \
  --word_timestamps True \
  --output_format json --output_format srt --output_format txt \
  --output_dir "D:\Videos\<slug>\transcripts"
```

(Or pass `--output_format all` for every format in one run.) Run this on
the external mic audio when the project has one (per the sync offset
established when the project's cameras were synced); otherwise run it once
per camera whose audio is authoritative for the edit.

`tools/transcribe.py` wraps this invocation, records the model and
duration used in a sidecar `transcripts/<name>.meta.json`, and is what
`docs/pipeline.md` §1 calls.

## Blooper / repeat-take flagging (`tools/find_flags.py`)

Two tiers, both computed from the word-level JSON output:

**CUT (confident):**
- Adjacent segments with high text overlap — the speaker re-read the same
  line. Detected by comparing normalized token sequences of consecutive
  segments (or a segment against the next N segments) for near-duplicate
  content.
- False starts — a segment ends mid-phrase and the very next segment
  restarts with the same opening words.
- Explicit self-correction phrases — "sorry", "let me start that again",
  "take two", "scratch that", and similar, treated as a strong signal the
  preceding clause through this phrase should be dropped.

**CHECK (possible):**
- An **interior silence gap greater than 3 seconds** inside what looks like
  one continuous take (not at a segment boundary) — the strongest signal
  short of a literal repeated sentence, from the silencedetect technique
  proven on the sacrament edit:
  `ffmpeg -af silencedetect=noise=-30dB:d=0.6` across the full audio, then
  check which beats contain an interior gap.
- **Word durations exceeding ~1.2 seconds** — the "swallowed retake"
  signature: when a speaker immediately re-reads a line, Whisper sometimes
  reports the text once and absorbs the pause-plus-second-take into a
  single word's timestamp span rather than reporting it twice. Treat any
  such word as a flag, not a cut point — where inside the stretched word
  the real second take begins is exactly what got destroyed, so it needs a
  human ear (or a re-transcription of just that window) before anything is
  removed. A clip with no such flags is weak evidence of cleanliness, not
  proof — a swallow smeared across several words won't clear this bar.
- Ordinary pauses between 1.5 and 3 seconds — below the blooper-signal
  threshold but long enough to be worth a pacing look.
- Near-duplicate segments that don't clear the CUT overlap threshold.

Every flag record carries: start/end seconds, tier (CUT/CHECK), a short
reason string, and the flagged text — this is what
`tools/build_script_docx.py` renders into the inline markup described in
`script-doc-format.md`.

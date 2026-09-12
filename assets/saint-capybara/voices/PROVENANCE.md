# Chatterbox reference-voice provenance

Each `.wav` here is a ~12-19s reference clip used for Chatterbox TTS's
zero-shot voice cloning (`audio_prompt_path` — see
`tools/capy/tts_chatterbox.py`). None of these are performances of any
Saint Capybara script text; they're short samples of someone else's
voice, used only to steer the *timbre* of the model's own synthesized
speech. All sources below are public-domain or CC0 and license-checked
before inclusion. Do not add a new voice file here without recording its
source and license the same way.

Chosen 2026-09-11 after several audition rounds (LibriVox nonfiction
narrators, then Mozilla Common Voice speakers filtered to verified
metadata) — see the project chat history for the full audition process
if ever needed for context.

## host_andrew_kennedy.wav — HOST voice (locked)

- **Source:** LibriVox recording of *Up from Slavery: An Autobiography*
  (version 3) by Booker T. Washington, archive.org item
  `up_from_slavery_3_2010_librivox`, read by **Andrew Kennedy**.
- **License:** LibriVox recordings are dedicated to the public domain by
  the reader; the underlying text (1901) is also public domain.
- **Why:** deepest/calmest of the audition candidates (median F0 ≈ 96 Hz
  measured via `librosa.pyin`), matched the brand's calm/measured/mildly
  warm register better than the earlier poetry/speech-reciter candidates
  that read as too oratorical.

## quote_male_1.wav — Mark Nelson (LibriVox)

- **Source:** LibriVox recording of *Up From Slavery* by Booker T.
  Washington, archive.org item `up_from_slavery_1703_librivox`, read by
  **Mark Nelson**.
- **License:** public domain (LibriVox reader dedication + public-domain
  text).
- **Measured F0:** ≈ 137.0 Hz.

## quote_male_2.wav — Common Voice speaker (client_id `19e5ce2a3e66e57f...`)

- **Source:** Mozilla Common Voice (English config), accessed via the
  `fsicoli/common_voice_17_0` Hugging Face mirror (the official
  `mozilla-foundation/common_voice_*` repos were migrated off HF to
  "Mozilla Data Collective" as of Oct 2025 and no longer host audio).
- **Recorded metadata** (self-reported by the contributor):
  `accent = "United States English"`, `gender = "male_masculine"`,
  `age = "twenties"`.
- **License:** Common Voice audio clips are released CC0 (public domain
  dedication).
- **Measured F0:** ≈ 197.1 Hz (lightest/highest of the male pool).

## quote_male_3.wav — Common Voice speaker (client_id `36e54f271628fd5d...`)

- **Source/license:** same as quote_male_2 (`fsicoli/common_voice_17_0`, CC0).
- **Recorded metadata:** `accent = "United States English"`,
  `gender = "male_masculine"`, `age = "twenties"`.
- **Measured F0:** ≈ 163.9 Hz.

## quote_male_4.wav — Common Voice speaker (client_id `3d586f3af9e324f0...`)

- **Source/license:** same as quote_male_2 (`fsicoli/common_voice_17_0`, CC0).
- **Recorded metadata:** `accent = "United States English"`,
  `gender = "male_masculine"`, `age = "thirties"`.
- **Measured F0:** ≈ 109.4 Hz (deepest of the pool; still audibly
  distinct from the host voice's 96 Hz in practice — re-audition if a
  future listen-through says otherwise, `quote_male` candidate voice12,
  122.8 Hz, was the runner-up).

## quote_female_1.wav — Common Voice speaker (client_id `923adfaf321b5152...`)

- **Source/license:** same as the other Common Voice entries
  (`fsicoli/common_voice_17_0`, CC0).
- **Recorded metadata:** `accent = "United States English"`,
  `gender = "female_feminine"`, `age = "twenties"`.
- **Status:** only female quote voice approved so far (2026-09-11) — all
  female-voiced quotes will sound identical until more are added. The
  pool is designed to be trivially extensible (`capy.beats.DEFAULT_VOICES
  ["quote_female_pool"]` is a plain list); add `quote_female_2.wav` etc.
  here and append to that list, no other code changes needed.

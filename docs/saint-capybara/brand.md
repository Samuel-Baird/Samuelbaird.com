# Saint Capybara — brand bible

Saint Capybara is a standalone, anonymous media brand: a small pixel-art
capybara monk who hosts calm, charitable, scholarly reaction shorts about
Latter-day Saint history, doctrine, scripture, and practice. This doc is
the single source of truth for who he is, how he looks, how he sounds, and
the anonymity rules that keep this brand separated from the creator's
other public work. `docs/types/saint-capybara.md`,
`docs/saint-capybara/script-format.md`, `tools/capy_check_brand.py`, and
every rendering tool read their constants from here (and from
`assets/saint-capybara/theme.yaml`, which holds the machine-readable
version of the palette/fonts/layout in this doc).

**This is a different visual and editorial system from
[`../style-guide.md`](../style-guide.md).** Nothing from that doc — its
charcoal quote cards, cream serif type, bottom-left credit chip, or music
rules — is reused here. See "Visual system" below for the explicit
contrast list.

**Sprite art is AI-generated, not code-drawn.** An earlier iteration of
this doc specified code-drawn PIL sprites (`tools/capy/parts.py`,
`compose.py`) and, at that stage, a simplified character with no robe and
no Bible. Both are superseded: the finalized art was generated from
[`../../prompts/saint-capybara-character-prompt.md`](../../prompts/saint-capybara-character-prompt.md)
(the master style/consistency prompt — edit that file, not just a chat,
if the design changes again) and lives at
`D:\saint-capybara\finalized images\saint-capybara-<pose>.png`, 1254×1254
transparent PNGs. The `tools/capy/*` PIL sprite generator is not part of
the current pipeline; it's kept only as a historical fallback and is not
being maintained against this design.

## 1. Identity

- The host and the channel share one name: **Saint Capybara**. No surname,
  no hometown, no age, no biography that maps to any real person. First
  person ("I") is fine; "we" means "the viewer and I," never "the Church."
- Saint Capybara is not a spokesperson for the Church. Never state "the
  Church says X" without a cited source (see
  [`research-protocol.md`](research-protocol.md)). Every video description
  carries: *"Independent project. Not affiliated with or endorsed by The
  Church of Jesus Christ of Latter-day Saints."*
- A standalone fictional media brand — not a persona for the creator to
  step out of. No creator identity appears on screen, in narration, or in
  metadata, ever. See §8-9.

## 2. Tone

Saint Capybara is peaceful, sincere, scholarly, charitable, and slightly
whimsical. He explains, clarifies, and defends beliefs without mocking
critics or trying to "own" opponents. He is charitable toward other
Christians, respectful toward critics, comfortable acknowledging
uncertainty ("The historical record doesn't let us answer that
confidently" is a fine thing for him to say), and more interested in
getting the history and theology right than in winning.

The humor comes almost entirely from the fact that a tiny capybara wearing
a crucifix is discussing serious theological questions — not from cruelty
toward anyone, on any side.

**Never:** polemics, ad hominem attacks, insults toward critics,
ex-members, other Christians, historians, or scholars; speculation about
someone's motives without direct evidence; "destroyed," "owned," "cope,"
"rekt," "debunked," or equivalent debate-bait language; sarcasm as a
substitute for an argument; treating a critic's honest concern as if it
were bad-faith.

**Always:** steelman before rebutting; criticize arguments, not people;
acknowledge a critic's valid concerns; allow partial agreement ("Yes, that
happened. Here is the context."); precision in comparison — never
"Christians believe X" when the belief is particular to one tradition.

**Signature phrasing** (locked at Step 4 with the user, recorded here once
chosen — deliberately new, never reused from the creator's other work): an
opening formula and a closing formula, used consistently across every
video so they become recognizable. *Placeholder until Step 4; do not
invent one before then.*

## 3. Fixed visual design (do not drift from this)

Every image and every pose of Saint Capybara includes, without exception:

- A small brown capybara, clearly recognizable as a capybara (see the
  anatomy notes below) — not a bear, weasel, ferret, or otter.
- A simple monk-like brown robe, with a rope cincture (the knotted cord
  belt) tied at the waist.
- A visible gold crucifix necklace.
- A Bible held in one paw or clearly present in frame, with a
  traditional Christian/Catholic-looking gold cross on its cover.
- A small golden halo.
- A calm, gentle expression.

**Capybara anatomy — check this first whenever the design is revisited.**
Getting this wrong is what made earlier attempts read as "a bear in a
robe" instead of a capybara. Keep: a broad, blocky head; a short, blunt
muzzle (not a pointed snout); small rounded ears; short sturdy legs; a
stocky, barrel-shaped body; little to no visible tail. Avoid: a long
narrow snout, a long tail, a thin upright body, or an elongated
ferret/weasel silhouette.

All six fixed elements — capybara anatomy, robe, crucifix, Bible with
cross, halo, calm expression — appear in every pose without exception.
Do not redesign the character between poses; only the pose/expression
changes. See the quality checklist in §4 for exactly what to catch if a
generation drifts.

## 4. Art style

The art should resemble a tiny medieval Christian icon recreated as a
retro video-game sprite: clean pixel art, target 128×128 (the finalized
files are delivered larger, at 1254×1254, for downstream scaling
headroom), transparent background, simple dark outlines, minimal
shading, muted warm colors, a readable silhouette, medieval Christian
iconography influence, and a calm/reverent tone. Cute, but not chibi or
anime.

**Avoid:** realistic rendering, anime styling, exaggerated meme faces,
overly elaborate/messy backgrounds (must be transparent, not just
plain), aggressive, smug, or polemical expressions.

**Character consistency across poses.** Every new pose is generated from
the reference image plus the master prompt
([`../../prompts/saint-capybara-character-prompt.md`](../../prompts/saint-capybara-character-prompt.md)),
never from a fresh description — the goal is always *the same Saint
Capybara in a new pose*, never *a new character inspired by Saint
Capybara*. A generation should be rejected or redone if:

- it no longer clearly looks like the same character, or stops looking
  like a capybara specifically;
- the crucifix, the Bible, the cross on the Bible, or the halo
  disappears;
- the robe changes materially (color, cut, or the rope cincture going
  missing);
- the style drifts away from pixel art;
- the expression becomes too exaggerated, hostile, smug, or polemical;
- the background is messy instead of transparent.

## 5. Sprite roster and rhetorical-function mapping

25 finalized files at `D:\saint-capybara\finalized images\`, named
`saint-capybara-<pose>.png`. The original 21-pose brief is fully covered;
two were renamed to shorter file-safe names in production (noted below),
and 4 new poses were added for the standard sign-off sequence (§5a).

| File (`saint-capybara-` prefix) | Use |
|---|---|
| `neutral` | Standing calmly, Bible against chest, paws resting — the default. |
| `talking` | Mouth slightly open, one paw gesturing while holding the Bible. |
| `teaching` | One paw raised as if explaining a point. |
| `reading` | Looking down at an open Bible. |
| `thoughtful` | Looking slightly upward, reflective. |
| `pointing` | Gesturing toward something beside the character. |
| `happy` | Gentle smile, relaxed posture. |
| `concerned` | Sympathetic expression for serious topics. |
| `confused` | Slight head tilt, puzzled expression. |
| `surprised` | Widened eyes, subtle surprise. |
| `skeptical` | Mildly questioning, not hostile. |
| `amused` | Small smile or quiet laugh. |
| `prayerful` | Eyes closed, peaceful posture, Bible held close. |
| `solemn` | Subdued expression for serious historical/theological topics. |
| `encouraging` | Warm expression, one paw slightly extended. |
| `source` | *(was "reading a source" in the brief)* — Bible in one paw, a scroll/document visible. |
| `researching` | Surrounded by a few books/papers, still holding the Bible. |
| `quote` | *(was "explaining a quote" in the brief)* — pointing toward empty space where text can be added. |
| `listening` | Attentive neutral pose. |
| `deadpan` | Calm blank stare, for light humor. |
| `disappointed` | Paw resting on forehead, tired look. |

**Rhetorical-function → pose** (first entry preferred unless a beat names
a literal pose): evidence → `source` / `reading` / `neutral` · uncertainty
→ `thoughtful` / `confused` · serious → `concerned` / `solemn` ·
questionable premise → `skeptical` · factual failure → `disappointed` /
`deadpan` · light → `amused` / `happy` · explain → `teaching` / `quote` /
`pointing` · listen → `listening` · closing → `encouraging` /
`prayerful`.

**Hard rule — never `amused` or `happy` on a sensitive topic.** Any beat
or video discussing suffering or sensitive history must not select
either pose; a `check_sources`/`check_brand`-style lint (see the pipeline
plan) should enforce this once that tooling exists — until then it's a
manual check. Saint Capybara stays visually secondary to the evidence
when a document or chart matters: he stays in his fixed bottom-left
corner (see §8 layout) and the full stage above is given over to the
document/chart, rather than him shrinking further or moving.

### 5a. Outro sign-off sequence

Every video ends on the same four-pose sequence: the character making
the sign of the cross while narration says *"in the name of the Father,
and of the Son, and of the Holy Ghost, Amen."*

| File | Beat |
|---|---|
| `saint-capybara-sign-father.png` | "...in the name of the Father," |
| `saint-capybara-sign-son.png` | "...and of the Son," |
| `saint-capybara-sign-holy.png` | "...and of the Holy Ghost," |
| `saint-capybara-sign-spirit-amen.png` | "...Amen." |

This is the standard outro for every video, not a one-off for any single
short — wire it into the beat-list template / compositor as a fixed
closing sequence.

## 6. Voice and TTS spec

Kokoro, local, calm/measured/mildly warm delivery — never theatrical
"debate bro" emphasis — speed 0.95, target ≈140–150 words per minute. A
pronunciation dictionary (`docs/saint-capybara/pronunciations.md`,
`script/pronunciations.yaml`) is mandatory; every new proper noun gets an
entry before it is ever rendered — the merged dictionary is applied by
`tools/capy_tts.py` via misaki's `[word](/ipa/)` inline override syntax.

**Voice id: `am_michael` (default, tentatively locked).** `tools/capy_tts.py
--sample` was run against all three shortlisted voices (`am_michael`,
`am_onyx`, `bm_george`) with a test paragraph containing a dictionary word
("Nauvoo") — all three rendered correctly with the lexicon override
applied (confirmed in the printed phoneme-substituted text: `[Nauvoo](/nɔˈvu/)`)
and produced plausible word timings. `am_michael` is set as the default
per the plan's own shortlist ordering; this is a tentative pick pending an
actual listen-through by the user (the agent cannot judge vocal quality by
ear) — if the user prefers `am_onyx` or `bm_george` after listening to the
three sample WAVs, just change `voice.name` in a project's `beats.yaml`
(and this line) rather than treating the pick as unchangeable.

## 7. Visual system

**Explicitly not used here** (this is the other identity's style —
[`../style-guide.md`](../style-guide.md)): charcoal `#1a1a1a`–`#222222`
flat quote cards, cream serif (Georgia/Source Serif class) typography,
centered quote with bottom-right attribution and a thin cream rule,
bottom-left `Source:` credit chip, 1920×1080 landscape cards, royalty-free
music bed under narration.

**Saint Capybara's own palette.** The finalized art has natural
light/shadow gradients per material, not a flat two-tone fill, so these
are representative samples taken directly from `saint-capybara-neutral.png`,
not a strict palette: fur mid-tone `#A76031` (ranges warmer/lighter in
highlights), muzzle patch `#7A5240` (a grayer, dustier brown than the
main fur — the key capybara "tell"), robe `#6B4020` in shadow up to
`#C98A4A` in highlight, gold accents (halo/crucifix/Bible cross) `#F9BF46`
with a pale `#FDEFC0` highlight, Bible cover `#6B2A21` deep maroon-red,
outline `#40261A` (a dark warm brown, not pure black). Frame/UI elements
(evidence cards, captions, wordmark, credit chips) still use the
separate, flatter palette in `assets/saint-capybara/theme.yaml` —
parchment `#E8DAC0` background, ink `#2E2117`, highlight brick `#B7431F`
(caption keyword highlight), source-label teal `#2F6B5E`. That file's
`palette:` block (sprite-part keys like `fur`/`snout`/`robe`) is
vestigial, left over from the retired PIL renderer, and should be
ignored in favor of the samples above; its frame/UI hex keys are
provisional until a compositor is actually built and can be checked
against the real art side by side.

**Typography** (SIL OFL 1.1, bundled in `assets/saint-capybara/fonts/`
with each license text): **Press Start 2P** for labels, the hook chip,
card attributions, and the wordmark; **Pixelify Sans** for captions and
card body text. No serif anywhere in this identity, and neither font is
shared with the other brand.

**Evidence cards:** parchment card, thin ink pixel border, citation line
top-left in Pixelify Sans (minimum legible size at 1080px width — see
`script-format.md`), quotes verbatim with `[...]` for omissions, page
images shown with a visible page number. No brand credit chip like the
other identity's — the only recurring brand mark is a small wordmark,
bottom-right, during reserved zones (see §8 layout below).

**Captions:** always burned in (muted-viewing design). Max 2 lines, ~34
characters per line, at most one highlighted keyword per caption chunk
(a name, date, number, or key term — never a loaded/charged word).
Legible on a phone without pausing.

**No music in v1.** No intro/outro sting, no logo animation, no end card
that echoes the other brand's look.

## 8. Frame layout (1080×1920, 30fps)

Also encoded machine-readably in `assets/saint-capybara/theme.yaml:
layout`, which is the authoritative version — this table mirrors it.
Superseded from an earlier design (a centered "character row" with a
square 512×512 bust) once the finalized art turned out to be full-body
standing figures roughly square in their own visible bounding box
(measured ~0.92–0.97 width/height across `neutral`, `pointing`,
`sign-father`) rather than a compact icon — a bottom-left corner
placement reads better for that proportion and leaves more width for
evidence.

| Zone | y-range | Contents |
|---|---|---|
| Reserved (top) | 0–200 | Empty except the 3-second hook chip on beat 1. Avoids platform UI. |
| Stage | 200–808 | 1080×608 (exact 16:9): source clip, or full-width evidence/card/chart. |
| Captions | 830–1090 | Centered, burned-in, word-timed. |
| Character + panel band | 1100–1920 | Sprite in the bottom-left corner + evidence panel to its right (see below). |
| Reserved (bottom) | 1880–1920 | Last 40px sliver only, empty except the wordmark. Avoids platform UI. |

Within the character + panel band: the sprite sits flush to the bottom-left
corner (`x0: 8, y0: 1600`, 280×280, bottom edge at `y: 1880`, an 8px margin
from the left frame edge and no gap above the reserved-bottom sliver);
the evidence panel sits beside it (`x: 320–1040, y: 1470–1880`) for inline
receipts; the reserved sliver (`y: 1880–1920`) stays clear of the sprite
itself; the wordmark is bottom-right (`x1: 1040, y: 1892–1916`).

Saint Capybara is always on screen. When a beat carries inline evidence he
shares the band with it (panel to his right); when a document or chart
needs real space to be readable, it takes over the full stage instead,
and he stays in his corner at the bottom — never disappears, and evidence
never simply replaces him.

## 9. Anonymity and brand separation

Saint Capybara must remain clearly separated from the creator's other
public content and personal identity — not just by never *stating* who
runs the account, but by never being *designed* in a way that makes the
connection obvious through shared habits or branding.

**Never reuse, from the creator's other accounts/projects:** logos, color
palettes, typography, recurring phrases, intros/outros, usernames, bios,
thumbnails, music, editing conventions, signature jokes, or visual motifs.

**Never:** reference the creator's other accounts, projects, research
brands, websites, or personal history; cross-promote between Saint
Capybara and the creator's identifiable work; use phrasing like "on my
other channel" or "as I've discussed before"; reuse a personal anecdote
that has appeared prominently in the creator's other public content, even
if it seems innocuous in isolation (a specific hometown, job, mission
location, family detail, or timeline of life events can be identifying on
its own).

Distinct by construction, not just by omission: synthetic Kokoro voice
(never the creator's own voice or a clone of it), pixel art (never a
camera), 9:16 vertical (the other identity's Resolve types are landscape),
its own recurring phrasing, pacing, and presentation style.

## 10. Operational anonymity checklist

What `tools/capy_check_brand.py` enforces automatically, plus what stays a
manual/user task:

- **Filenames:** project slug only. No initials, no dates matching other
  uploads, no other-brand slugs anywhere in `D:\Videos\<slug>\`.
- **Exports:** `ffmpeg -map_metadata -1 -fflags +bitexact`, only a `title`
  tag written. Verify with `ffprobe` before calling a render final.
- **Images:** no text/metadata chunks. Spot-checked
  `saint-capybara-neutral.png` in `D:\saint-capybara\finalized images\` —
  clean (`Image.info` empty). Worth re-checking the others: some
  generators (ComfyUI included, depending on the save node) embed the
  full prompt/workflow JSON into a PNG text chunk by default, which is
  more of a "did this leak something odd" check than an expected problem
  here. Any tool this pipeline writes PNGs with (evidence crops, cards)
  should save without metadata the same way. No desktop screenshots with
  browser chrome, taskbars, usernames, bookmarks, or open tabs visible —
  evidence receipts are cropped page images (Gospel Scholar Archive
  `get_page_image`, Pulpit cite links) or clean crops, never a raw
  desktop capture.
- **Text:** `research/sources.yaml` notes, `script/beats.yaml` narration,
  and `exports/<slug>-description.txt` are scanned against
  `assets/saint-capybara/banned.txt` (gitignored — see below) plus
  runtime-derived tokens (home directory name, OS login name, git
  `user.name`/`user.email`) that are never written to any committed file.
- **`banned.txt` itself:** holds the creator's real other names, handles,
  and brand names. It is gitignored, is never published, and is never
  quoted anywhere in a video, description, or commit. `banned.example.txt`
  (committed) documents the mechanism with only generic phrases.
- **Upload account hygiene:** a separate account/email/browser profile for
  publishing — this is the user's own task, not something the pipeline
  can enforce, but it is named here so it isn't forgotten.
- **This repository:** its name and history reference the creator's other
  identity. It must never be linked from the Saint Capybara brand (no
  "made with," no credits, no GitHub link in a description or on screen).

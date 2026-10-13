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

**Rewritten 2026-09-09 — this is a personality change, not a wording
tweak. If you're recalling the old "peaceful, mostly-neutral fact-checker"
framing, discard it; the posture below is deliberately different.**

Saint Capybara is calm, confident, assertive, intellectually serious,
charitable, and direct. He is an LDS apologetics account and makes a
serious affirmative case for Latter-day Saint truth claims — the goal is
**not neutrality between competing truth claims.** He is willing to
challenge bad arguments, comfortable making a positive case for the
Restoration, not defensive, not timid, and not afraid to say plainly when
the LDS position is stronger. The guiding principle: *determine what is
true, test criticisms rigorously, expose inconsistent standards, and make
the strongest evidence-based case that the Latter-day Saint position
better explains the relevant history, scripture, theology, or practice.*

He should not merely explain that a criticism is "more complicated." When
the evidence supports it, he says clearly that the criticism is wrong,
that the critic is using an inconsistent standard, that the critic's
interpretation explains the evidence poorly, or that the LDS position has
greater explanatory power and coherence than the alternative on offer.

**Core rule: be charitable toward people and ruthless toward bad
arguments.** Be aggressive toward arguments, never toward the people
making them.

**Never:** insult the critic; mock someone's intelligence; call people
dishonest without evidence; speculate about motives; use rage-bait
language ("destroyed," "owned," "cope," "rekt," "debunked," or
equivalent); act smug; distort opposing views; pretend a weak LDS
argument is strong; treat a critic's honest concern as bad-faith.

**Always:** state the criticism fairly before testing it; criticize
arguments, not people; when a claim is true, concede it plainly and move
directly to what it actually shows (see the false/misleading/true taxonomy
in `research-protocol.md`); precision in comparison — never "Christians
believe X" when the belief is particular to one tradition.

**Avoid weak phrasing when the evidence permits a firmer conclusion.**
Prefer a stated conclusion to a hedge once the research actually supports
one:

| Instead of | Prefer |
|---|---|
| "There may be another way to look at this." | "The evidence gives us good reason to reject that framing." |
| "Latter-day Saints might respond…" | "The stronger reading of the evidence is…" |
| "Both sides have a point." | "The concern is understandable, but the historical conclusion being drawn from it is not supported." |

Good-tone examples (argue the argument, not the person): "That argument
doesn't survive contact with the historical record." · "The problem is
that this standard would undermine the critic's own position." · "Once
you look at the actual evidence, the LDS position is stronger." · "This
sounds persuasive until you ask whether the premise is even true." ·
"That isn't an explanation of the evidence; it's an assumption being
imposed on it." · "If we apply the same standard consistently, Mormonism
comes out better than the criticism suggests." · "This criticism depends
on treating something ordinary as uniquely sinister when it appears
across religious and secular institutions." · "The critic has identified
a real issue, but the conclusion they draw from it does not follow."

**Positive apologetics, not just rebuttal.** Don't spend every video
merely answering objections. Whenever the research supports it, move from
"the criticism fails" to "here is why the LDS position is better." Ask:
which worldview explains the evidence more naturally; which position
requires fewer special exceptions; which interpretation fits the
historical record better; does LDS theology solve a problem the critic's
framework struggles with; is the critic relying on assumptions less
defensible than the LDS belief they're attacking; what positive evidence
supports the Restoration, not just what answers an objection. The typical
structure: (1) the criticism sounds strong; (2) test its premise; (3)
show where it fails or overreaches; (4) apply the same standard
consistently; (5) show why the LDS position performs better. Not every
beat needs all five steps, and step 5 only when the research actually
gets you there — never manufacture a stronger conclusion than the
evidence supports (this doesn't relax `research-protocol.md`'s grading
system or the escalation triggers; a claim graded `disputed` or
`speculation` still gets presented as such, argued as the strongest
*defensible* reading, not oversold as settled).

**Argument moves that fit this tone:** challenge premises early; expose
double standards clearly; use comparisons aggressively when they reveal
unfair framing; distinguish genuine historical problems from rhetorical
exaggeration; press critics to defend their own assumptions; ask what
alternative explanation better fits the evidence; force arguments onto
consistent standards; make affirmative LDS arguments instead of
constantly conceding rhetorical ground for its own sake.

**How conceding a true claim actually happens:** through the substantive
response itself — stating plainly that it's true, citing real sources,
then moving to what it actually shows (often less than the critic's
framing implies, sometimes exactly what it implies — say which). **Don't
add a separate meta-statement praising critics as a class** ("some
criticism is legitimate and worth sitting with," "not every critic is
acting in bad faith") once a specific claim has already been fact-checked
on screen — that's redundant, not extra charity: the fact-check itself is
the fairness. Reserve an explicit fairness callout for cases the video
hasn't otherwise addressed (e.g. correcting an actual misquote, or naming
a one-sided generalization the clip itself makes) — see
`script-format.md`'s closing conventions.

**Signature phrasing** (locked at Step 4 with the user, recorded here once
chosen — deliberately new, never reused from the creator's other work): an
opening formula and a closing formula, used consistently across every
video so they become recognizable. *Placeholder until Step 4; do not
invent one before then.*

**One-line summary of the personality** (2026-09-09): a **high-confidence
Restorationist** — generous toward people, unsparing toward bad
arguments, historically literate, willing to concede genuine problems,
and unapologetic about saying LDS theology is often the better Christian
explanation. See `docs/saint-capybara/apologetics-playbook.md` for the
argument craft this tone runs on: the six-step response structure,
audience-specific playbooks (Catholic / Protestant / atheist-and-ex-Mormon
each need a different strongest counter-argument), the overclaiming
discipline, shorts-vs-long-form structure, and the two-question test
every script should pass before Gate A.

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

**`clip` beats should react to what the source clip is actually saying,
not default to `listening` on every one.** `listening` is the fallback
for a genuinely neutral stretch (introductions, throat-clearing, nothing
worth a reaction yet) — once the clip says something uncertain, alarming,
dubious, or funny, pick the matching full-emotion pose instead (same
roster as narration beats: `thoughtful`, `concerned`/`solemn`,
`skeptical`, `surprised`, `confused`, `disappointed`/`deadpan`,
`amused`/`happy` where not sensitive-forbidden). This uses only the
existing 21-pose roster — no new art — the fix is authoring habit, not a
missing pose. A script with `pose: listening` on most/all of its clip
beats is a sign this wasn't applied and should be revisited before Gate
A.

**Hard rule — never `amused` or `happy` on a sensitive topic.** Any beat
or video discussing suffering or sensitive history must not select
either pose; a `check_sources`/`check_brand`-style lint (see the pipeline
plan) should enforce this once that tooling exists — until then it's a
manual check. Saint Capybara's on-screen size follows the three-mode
layout in §8, not a fixed corner position: full-screen dominant between
clips (narration/response beats), medium bottom-left beside a document/
chart/quote card, small bottom-left while reacting over a clip. He is
never smaller than that CLIP-mode corner size and evidence never simply
replaces him.

### 5a. Closing line: "God bless"

**Retired 2026-09-09 — there is no more fixed sign-of-the-cross outro
sequence.** An earlier version of this brand mandated every video end on
a multi-beat sign-of-the-cross gesture ("In the name of the Father, and
of the Son, and of the Holy Spirit, Amen.") rendered as its own shared,
cached clip. That whole mechanism (the four/five `sign-*` poses, the
mandatory-append-to-every-`beats.yaml` behavior, `tools/capy_outro.py`'s
shared-cache system) is gone — removed, not just deprecated. Don't
resurrect it; see git history if the mechanics are ever needed for
reference. The `sign-*` sprite art files still exist under
`D:\saint-capybara\finalized images\` and may be reused for something
else later, but they carry no special meaning now.

**Every video's closing beat instead ends the narration line on "...God
bless."** — an ordinary `narration` beat like any other (pick whatever
pose fits the moment, `encouraging` is a reasonable default), not a
special kind or a shared/cached asset. `capy_check_sources.py`
hard-errors if the last beat's text doesn't end that way. See
`script-format.md`'s closing-conventions section for the exact rule and
`docs/saint-capybara/hybrid-resolve-pipeline.md` for the prior outro
cache's removal note.

## 6. Voice and TTS spec

Kokoro, local, calm/measured/mildly warm delivery — never theatrical
"debate bro" emphasis. A pronunciation dictionary
(`docs/saint-capybara/pronunciations.md`, `script/pronunciations.yaml`)
is mandatory; every new proper noun gets an entry before it is ever
rendered — the merged dictionary is applied by `tools/capy_tts.py` via
misaki's `[word](/ipa/)` inline override syntax.

**Host voice id: `am_michael`, speed 1.5 — LOCKED 2026-09-09, not
tentative.** The user confirmed this voice after watching
`dont-read-the-bom`'s render and separately asked for the speed to be
raised from the original 0.95 lock to 1.5 (~220 target words per minute,
scaled up from the original ≈140–150 wpm/0.95 target). Both are
standing rules for every Saint Capybara project from here on, encoded in
`capy.beats.DEFAULT_VOICE = {"name": "am_michael", "speed": 1.5}` and
`assets/saint-capybara/templates/beats.yaml`'s `voice:` block — do not
regress either without a new, explicit user direction to change them.
Before the lock, `tools/capy_voice_audition.py` had rendered every
English male Kokoro voice (13: `am_michael`, `am_fenrir`, `am_puck`,
`bm_fable`, `bm_george`, `am_onyx`, `bm_lewis`, `am_echo`, `am_eric`,
`am_liam`, `bm_daniel`, `am_adam`, `am_santa`) plus a female shortlist for
the quote voice (`af_heart`, `af_bella`, `af_nicole`, `bf_emma`,
`af_sarah`) into `D:\saint-capybara\voice-audition\` for reference — see
`audition.md` there for the upstream quality grade of each, kept for
historical context now that the pick is locked. **Any future change to
the voice or its speed means re-rendering every in-flight project's
audio** so nothing mixes an old-speed take with a new-speed one within
the same video.

**Quote voices (article/text-source mode, `kind: excerpt` beats).** A
second Kokoro voice reads the source's own words aloud, sex-matched to
the person being quoted — `voices.quote_male` / `voices.quote_female` in
`beats.yaml`, resolved per beat by `capy.beats.resolve_voice`
(`docs/saint-capybara/script-format.md` "Excerpt fairness"). Tentative
picks pending the same bake-off/listen-through: `quote_male: am_michael`,
`quote_female: af_heart` (`tools/capy/beats.py: DEFAULT_VOICES`) — these
should end up **audibly distinct** from the locked host voice once
chosen, since the whole point is "their words, then mine" staying
audible to a muted-off/audio-only listener too.

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
with each license text): **Press Start 2P** for card attributions and
chart labels; **Pixelify Sans** for captions and card body/quote text.
No serif anywhere in this identity, and neither font is shared with the
other brand. **No chips, no wordmark, no on-screen hook text** —
removed 2026-09-09 as part of the layout redesign (§8); the hook line in
`beats.yaml` still drives the title/description, it just never renders
into the frame. The only on-screen text, ever, is a caption or card/quote
text (including its attribution).

**Evidence cards:** parchment card, thin ink pixel border, citation line
top-left in Pixelify Sans (fit-to-width, shrinking from 48px down to a
36px floor before ever wrapping past the card — see `script-format.md`),
quotes verbatim with `[...]` for omissions, page images shown with a
visible page number.

**Captions:** always burned in (muted-viewing design), Pixelify Sans,
84px on parchment/freeze backgrounds (`style_capy`) or 76px over source
video with a translucent teal pill behind the text for contrast
(`style_source`), 76px over a card (`style_card`) — all with a 6px ink
outline and shrinking to a floor (60/56/56px) before ever wrapping past
2 lines. Lines wrap by **measured pixel width** against a 960px budget
(`capy.text.fit_text`), never a character-count guess — the earlier
34-char guess is what produced a shipped caption clipped at both frame
edges. At most one highlighted keyword per caption chunk (a name, date,
number, or key term — never a loaded/charged word). Legible on a phone
without pausing.

**No music in v1.** No intro/outro sting, no logo animation, no end card
that echoes the other brand's look.

## 8. Frame layout (1080×1920, 30fps; 1920×1080 for YouTube long form)

**`layout.version 2` (2026-09-09).** Also encoded machine-readably in
`assets/saint-capybara/theme.yaml: layout`, which is the authoritative
version — this section mirrors it. Superseded the v1 fixed
stage(200–808)/captions(830–1090)/character-band(1100–1920) zoning,
which assumed a 16:9 source video cropped into a 1080×608 "stage"
rectangle — every real source has instead been native 1080×1920, so v1
left roughly two-thirds of every frame as empty parchment, kept the
sprite at a 280px thumbnail, and set captions at 68px (a size that, at
the old 34-character-per-line wrap, clipped off the frame edge on a
real shipped caption). v2 replaces the single fixed zoning with **three
frame modes, chosen by beat kind** (`capy.layout.Theme.mode_for`):

| Mode | Beat kinds | Background | Sprite | Captions |
|---|---|---|---|---|
| **CLIP** | `clip` | The source video fills the whole canvas — cover-cropped for a 9:16-or-narrower source, or fit inside a letterbox band (y 230–850) over a blurred/darkened cover copy of the same footage for 16:9-or-wider | 400px box, bottom-**right** (x0: 648 — 2026-09-09 user feedback, was bottom-left; mirrors the old 32px margin off the opposite edge), 5px ink outline + a hard offset shadow so pixel edges read over busy video | y 860–1120, `style_source` (76px, teal pill) |
| **HOST** | `narration` | Parchment + vignette (`stage: blank`); a full-bleed last-clip-frame background blurred/dimmed 55% (`stage: freeze`); an arbitrary project image, e.g. a historical painting/photo/sketch, same treatment (`stage: image`, 2026-09-09); or the source video playing continuously (not frozen) behind him — "capybara in front of the reacted video" (`stage: video`, 2026-09-09) — see `script-format.md` | 920px box, horizontally centered, the dominant element on screen, with a soft ground-shadow ellipse | y 300–660 (above his head), `style_capy` (84px) |
| **CARD** | `card`, `evidence`, `chart`, `excerpt` | Parchment; the card/chart/evidence/pull-quote occupies x 40–1040, y 250–830 | 480px box, bottom-left, 4px outline | y 860–1120, `style_card` (76px) |

Every mode anchors the sprite's feet to the same line
(`layout.sprite_bottom: 1600`) so cuts between modes don't make him jump
vertically. Documented platform-UI safe-zone assumptions (union of
TikTok/Reels/Shorts chrome at 1080×1920): top 0–250 unsafe (status bar,
For You/Following tabs), bottom 1580–1920 unsafe (username, caption,
sound ticker, nav), right x>930 unsafe for y 1000–1650 (like/comment/
share/avatar rail) — captions and card text stay entirely inside x
60–1020, y 250–1580; the sprite's feet may brush the username band by
design (a corner mascot doing so reads as normal on this platform).

**CLIP mode is bottom-right, and does overlap the documented like/
comment/share rail zone (x>930, y 1000–1650) on some platforms** — a
known, accepted tradeoff of the 2026-09-09 bottom-right change, not an
oversight. **The one thing that must never happen regardless of that
tradeoff: the sprite box and burned-in caption text must never occupy
the same vertical band.** Today they don't (CLIP captions: y 860–1120;
CLIP sprite box: y 1200–1600, both anchored off `sprite_bottom`) — if a
future layout change moves either one, captions keep their band and the
sprite gets resized/repositioned to stay clear, never the reverse.

**No chips, no wordmark, no on-screen hook text.** The v1 "Source video"/
"SOURCE" label chips, the beat-1 hook chip, and the bottom-right wordmark
are all removed — the only text drawn into any frame is a caption or
card/quote text (with its attribution). The "source visible on screen"
clip-fairness requirement (`script-format.md`) now lives in the video
description instead.

Saint Capybara is always on screen, at the size his current beat's mode
sets: full-screen dominant between clips (HOST), medium beside a
document/chart/quote card (CARD), small in the corner while reacting
over a clip (CLIP) — never smaller than the CLIP-mode size, and evidence
never simply replaces him.

### 16:9 layout — YouTube long form (2026-10-13)

`video_type: long-youtube` renders on a 1920×1080 canvas
(`theme.yaml: layout.landscape`, picked automatically by
`capy.layout.Theme.for_doc`). Same three modes, same rules above (sprite
always on screen, captions and sprite never overlap, no chips/wordmark),
re-laid out so the extra width is used instead of left as parchment —
the sprite moves *beside* the text rather than below it:

| Mode | Background | Sprite | Captions |
|---|---|---|---|
| **CLIP** | A 16:9 source fills the whole frame (cover-crop). A 9:16 source is pillarboxed full-height in the center over a blurred/darkened cover copy — the mirror of the 9:16 letterbox | 340px box, bottom-left, outline + hard shadow | x-centered, y 830–1000, max 1100px wide — clear of the sprite |
| **HOST** | Same `stage:` options as 9:16 | 960px box centered at x 520 — the left half, dominant | Right column centered at x 1420, y 260–760, max 800px wide, up to 3 lines, `style_capy` 80px |
| **CARD** | Parchment; card x 96–1400, y 60–820 (~70% of the frame) | 480px box, bottom-right beside the card | Under the card, centered at x 748, y 840–1010 |

Text sizes start larger than on 9:16 (`layout.landscape.overrides`:
captions 68-80px, card quotes 72px) since the frame is viewed bigger.
Safe area: no permanent platform chrome on YouTube, but the player's
control/progress bar covers roughly the bottom 8% on hover/pause and TVs
can overscan ~5%, so all text stays inside x 96–1824, y 54–1010; the
sprite's feet may sit below that, same as 9:16. Preview with
`tools/capy_storyboard.py --mock --landscape`.

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
camera), 9:16 vertical for shorts and Instagram long form (the other
identity's Resolve types are landscape), its own recurring phrasing,
pacing, and presentation style.

**YouTube long form is 16:9 — the same aspect ratio as the other
identity's videos — so it loses that one distinguisher and leans harder
on the rest.** It stays fully anonymous and uses Saint Capybara branding
only (user-confirmed 2026-10-13). On a 16:9 Saint Capybara video, be stricter, not looser:
no camera footage of anyone but the source being responded to, only the
pixel-art palette/fonts/card style above, no title-card, lower-third,
intro, chapter-card, or end-screen convention borrowed from the other
identity's landscape videos, no upload-schedule or thumbnail habits in
common, and publish from the Saint Capybara account only (sec 10).
`capy_check_brand.py` still runs on every export.

## 10. Operational anonymity checklist

What `tools/capy_check_brand.py` enforces automatically, plus what stays a
manual/user task:

- **Filenames:** project slug only. No initials, no dates matching other
  uploads, no other-brand slugs anywhere in `D:\Videos\<slug>\`.
- **Exports:** `ffmpeg -map_metadata -1 -fflags +bitexact`, only a `title`
  tag written. Verify with `ffprobe` before calling a render final.
- **Images:** no text/metadata chunks. Spot-checked all 25 finalized
  sprite files (2026-09-09) in `D:\saint-capybara\finalized images\` —
  clean (`Image.info` empty) apart from `deadpan`, which has a separate,
  unrelated defect (no alpha channel — see
  `docs/saint-capybara/hybrid-resolve-pipeline.md` "Known gaps"). Worth
  re-checking after any regeneration: some generators (ComfyUI included,
  depending on the save node) embed the full prompt/workflow JSON into a
  PNG text chunk by default, which is more of a "did this leak something
  odd" check than an expected problem here. Any tool this pipeline
  writes PNGs with (evidence crops, cards, cached sprite renders under
  `D:\saint-capybara\cache\sprites\`) should save without metadata the
  same way. No desktop screenshots with browser chrome, taskbars,
  usernames, bookmarks, or open tabs visible — evidence receipts are
  cropped page images (Gospel Scholar Archive `get_page_image`, Pulpit
  cite links) or clean crops, never a raw desktop capture.
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

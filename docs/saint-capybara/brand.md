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
arguments, not people; precision in comparison — never "Christians believe
X" when the belief is particular to one tradition.

**Pointed is allowed (2026-09-13).** The "Never" list above bans a
vocabulary and a posture, not sharpness. A dry, one-sentence jab aimed
at a standard, a framing, or a tradition's own record — earned by a
sourced fact already on screen, adjective-free, at most one per short —
is inside this tone, and the channel's best-received lines so far are
exactly that. *"The Catholic Church's own current canon law still sets
fourteen as the minimum age at which a woman can validly marry"* is a
jab; *"this is absurd"* is not. The full rule, with the channel's own
examples, the placement rule (close, or right after the strongest
evidence beat), and the cap, is `apologetics-playbook.md`'s "Sharpness"
section — read it before writing an opening or closing beat.

**On true claims: never deny a verifiable fact, but never let a fact sit
on screen as a bare concession either.** (Rewritten 2026-09-12 — an
earlier version of this rule said to "concede it plainly and move on,"
which in practice produced beats that read as arguing the critic's side.)
State the fact and its strongest available reframing, mitigating context,
or counter-evidence in the same breath — one continuous move, not a
concession beat followed by a separate rebuttal beat. See the
false/misleading/true taxonomy in `research-protocol.md` sec 7 for how
this applies per claim-type, and sec 12 trigger 6 for what happens on the
rare claim that really has no defensible reframing (that's an escalation
to the user, not license to spin it — see that section for why).

**Avoid weak phrasing when the evidence permits a firmer conclusion.**
Prefer a stated conclusion to a hedge once the research actually supports
one:

| Instead of | Prefer |
|---|---|
| "There may be another way to look at this." | "The evidence gives us good reason to reject that framing." |
| "Latter-day Saints might respond…" | "The stronger reading of the evidence is…" |
| "Both sides have a point." | "The concern is understandable, but the historical conclusion being drawn from it is not supported." |
| *(first response sentence)* "That part's true — the Church really does X. The real question is…" | "X doesn't do what the critic says it does — and here is what the record actually shows." |
| *(closing beat)* "We're not saying that settles everything, but… God bless." | "*(the sharpest sentence in the script)*. God bless." |

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
arguments, historically literate, and unapologetic about saying LDS
theology is the better Christian explanation (2026-09-12: the earlier
"willing to concede genuine problems" clause is gone on purpose — see "On
true claims" above). See `docs/saint-capybara/apologetics-playbook.md`
for the argument craft this tone runs on: the six-step response
structure, audience-specific playbooks (Catholic / Protestant /
atheist-and-ex-Mormon each need a different strongest counter-argument),
the overclaiming discipline, the "Sharpness" rules for opening and
closing beats and the jab, shorts-vs-long-form structure, and the
four-question test every script should pass before Gate A.

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

**Chatterbox TTS (Resemble AI, MIT license), local, zero-shot voice
cloning from a reference clip — RE-LOCKED 2026-09-11, replacing
Kokoro.** Kokoro is still fully supported as an engine (`tools/capy_tts.py`
never removed the Kokoro code path — see "Engine selection" below) but
is no longer the default for any locked voice. Calm/measured/mildly warm
delivery — never theatrical "debate bro" emphasis — remains the
delivery bar; it's now achieved by the *choice of reference clip*
rather than a Kokoro voice id.

**Host voice: cloned from `assets/saint-capybara/voices/
host_andrew_kennedy.wav` — LOCKED 2026-09-11, not tentative.** A ~12s
public-domain LibriVox clip (Andrew Kennedy reading Booker T.
Washington's *Up from Slavery* — see `PROVENANCE.md` in that folder for
the full source/license record). Chosen after two audition rounds: first
several LibriVox nonfiction narrators (rejected — read too
oratorical/"reciter" for a calm host), then several Mozilla Common Voice
speakers filtered to *verified, self-reported* metadata (US English
accent, male, twenties/thirties) rather than guessed from source-text
choice. Encoded in `capy.beats.DEFAULT_VOICE = {"engine": "chatterbox",
"ref": "assets/saint-capybara/voices/host_andrew_kennedy.wav", "speed":
1.25, "exaggeration": 0.5, "cfg_weight": 0.5}` and
`assets/saint-capybara/templates/beats.yaml`'s `voice:` block — do not
regress without a new, explicit user direction. **Any future change to
the voice/ref/speed/exaggeration/cfg_weight means re-rendering every
in-flight project's audio**, same reasoning as the old Kokoro
speed-lock.

**Speed: 1.25x, LOCKED 2026-09-12 — implemented as ffmpeg `atempo`
post-processing, not a native model parameter.** Chatterbox's
`generate()` has no speed/rate argument at all (confirmed by reading the
installed package source) — unlike Kokoro, where `speed` was a native
`KPipeline` argument. So a chatterbox-engine voice's `speed` field is
applied as a pitch-preserving ffmpeg time-stretch
(`capy_tts.apply_speed_change`, `atempo=<speed>` by default) run on the
raw Chatterbox render, **before** the Whisper timing-reconciliation pass
(`capy.align.align_timing`) so `timing.json` describes the actual
final-tempo audio, not the model's natural-cadence output. `rubberband`
(ffmpeg's `-af rubberband=tempo=...`) is available as a higher-quality
alternative (`CHATTERBOX_SPEED_METHOD` in `capy_tts.py`) but isn't the
default since it needs an ffmpeg build with `--enable-librubberband`,
not guaranteed on every machine this pipeline runs on. Applies to the
host and both quote pools identically (`capy.beats.DEFAULT_VOICE`,
`QUOTE_MALE_POOL`, `QUOTE_FEMALE_POOL` all set `speed: 1.25`).
Re-verified against a real project (`baptism-for-dead-thought`,
2026-09-12): per-beat Whisper match rates were effectively unchanged
(88-100% at both 1.0x and 1.25x, same beats hitting the same rates
within 1-2 points), and narration audio duration measured after the
atempo pass divided out to 1.25x exactly (e.g. one beat: 9.80s raw model
output -> 7.84s post-stretch = 9.80/1.25). Total beat-clip runtime
dropped from ~109.0s to ~89.8s (only narration sped up; clip beats are
unaffected, so the shrink is less than a flat 1/1.25 of the whole
video).

**Pronunciation dictionary — accepted regression, Chatterbox-voiced
beats only.** The mandatory pronunciation dictionary
(`docs/saint-capybara/pronunciations.md`, `script/pronunciations.yaml`)
is Kokoro/misaki-specific: it rewrites a matched word as misaki's
`[word](/ipa/)` inline IPA-override syntax, which only Kokoro's
tokenizer understands. Chatterbox's tokenizer is a plain grapheme BPE
tokenizer with no phoneme-override mechanism of any kind (confirmed by
reading the installed package source) — `tools/capy_tts.py` skips the
IPA-wrapping step entirely for Chatterbox beats (`apply_dictionary(...,
ipa=False)`, still expands `D&C` -> "Doctrine and Covenants" as a plain
literal substitution). **User-approved 2026-09-11: accept this
regression** rather than block the engine swap on it — spot-check
LDS/biblical proper-noun pronunciation by ear per project instead of
relying on the dictionary to force it.

**Quote voices — POOLS, LOCKED 2026-09-11.** `voices.quote_male` /
`voices.quote_female` in `beats.yaml` are now POOLS (lists) of Chatterbox
reference-clip voices, not one Kokoro voice each:
`capy.beats.QUOTE_MALE_POOL` (4 voices: `quote_male_1.wav` through
`quote_male_4.wav`) and `QUOTE_FEMALE_POOL` (1 voice so far,
`quote_female_1.wav` — every female-voiced quote sounds identical until
more are added; the pool is a plain list, trivially extensible, see
`assets/saint-capybara/voices/PROVENANCE.md`). A beat resolves to one
pool member via `capy.voice_pool.assign()`, keyed on the beat's
`speaker:` slug (`docs/saint-capybara/script-format.md`) — **the same
quoted person always gets the same voice**, both within one project and
across every future project that quotes them again, via the persisted
`assets/saint-capybara/voice_pool_assignments.json`. All 5 quote-pool
voices came from Mozilla Common Voice / LibriVox with the same
verified-metadata approach as the host voice; see `PROVENANCE.md` for
each one's source, license, and recorded accent/gender/age.

**Engine selection is additive, not a replacement.** Every voice spec
(the host default, a `voices:` pool member, or an inline `voice: {...}`
on a beat) carries an `engine` key (`"chatterbox"` or `"kokoro"`) that
`tools/capy_tts.py`'s `_synthesize_kokoro`/Chatterbox-batch dispatch
reads per beat. The Kokoro code path is untouched and fully working —
set any beat's `voice:` to an inline `{engine: kokoro, name: am_michael,
speed: 1.5}` to force it back for a specific beat (e.g. to isolate a
regression) without any code changes.

**Timing/captions without Kokoro's native word timestamps.** Chatterbox
exposes no word/token-level timing of any kind (confirmed by reading its
`generate()`/`T3.inference()`/tokenizer source — it's a purely
autoregressive token-to-audio model, no duration predictor or alignment
head). `tools/capy_tts.py` instead runs `openai-whisper`
(`word_timestamps=True`, already installed/pinned for
`tools/transcribe.py`'s clip-beat captions, reused in-process here —
`tools/capy/align.py`) on the rendered wav and reconciles its recognized
words against the *known script text* via sequence matching, so
`timing.json` always contains the script's own words with the
best-matched timestamps; falls back to evenly-spaced timing (scoped to
the wav's real measured duration) on a poor match, logging a warning so
a human knows to spot-check that beat's captions. Empirically validated
against a real Chatterbox render before this was wired in: Whisper's
recognized text matched the script word-for-word. Pose-swap timing is
unaffected either way — poses are one static sprite per beat (see
`script-format.md`'s "Pose changes every 10-20s" note), never
word-level, so losing Kokoro's fine-grained timestamps only ever
affected captions.

**Chatterbox lives in its own virtualenv.** `tools/.venv-chatterbox`
(gitignored, set up per `tools/requirements-chatterbox.txt`) — its
dependency stack conflicts with the pinned Kokoro/Whisper versions the
rest of this repo's tools use, so it's invoked as a subprocess
(`tools/capy/tts_chatterbox.py` -> `tools/capy/_chatterbox_worker.py`),
never imported in-process, mirroring how `tools/transcribe.py` already
shells out to a separate `whisper` CLI process rather than importing it.
Chatterbox also embeds an inaudible Resemble AI "Perth" watermark in
every output wav (a provenance/responsible-AI feature, not a licensing
restriction) — FYI, doesn't affect audible quality.

Before the Kokoro-era lock (2026-09-09, since superseded above),
`tools/capy_voice_audition.py` had rendered every English male Kokoro
voice (13: `am_michael`, `am_fenrir`, `am_puck`, `bm_fable`, `bm_george`,
`am_onyx`, `bm_lewis`, `am_echo`, `am_eric`, `am_liam`, `bm_daniel`,
`am_adam`, `am_santa`) plus a female shortlist (`af_heart`, `af_bella`,
`af_nicole`, `bf_emma`, `af_sarah`) into
`D:\saint-capybara\voice-audition\` — kept for historical context only,
superseded by the Chatterbox pick above.

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
text (including its attribution) — **plus one exception, the "RESPONSE
INCOMING" banner (§8, 2026-09-20)**, shown only until Saint Capybara
first speaks.

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

## 8. Frame layout (1080×1920, 30fps)

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

**"RESPONSE INCOMING" banner (2026-09-20 user direction).** A big
"RESPONSE INCOMING" title sits at the top of the frame for the **opening
clip only**, and disappears the moment Saint Capybara begins to speak. It
tells a cold viewer that the footage they're watching is the thing being
answered and that a reply is coming, so the reacted-to clip reads as setup
rather than as the video itself.

- **Window.** From t=0 (start of the first `clip` beat) to the start of the
  first narration-family beat, i.e. the first time the capybara's own
  voice plays. If the opening clip is split into several consecutive
  `clip` beats, the banner spans all of them. It does **not** return on
  later clips — one banner per video. A script that opens with narration
  (no leading clip) gets no banner.
- **Placement.** Top of the frame, but below the platform-unsafe status
  bar: y 260–420, centered, inside x 60–1020 (`platform_safe.top` is 250,
  so the banner never sits under the For You/Following tabs). It floats
  over the top of the clip video (and over the top edge of the letterbox
  band for a 16:9 source), so it is an *overlay*, never a change to the
  clip's crop or letterbox math.
- **Style.** Press Start 2P (the `display` font, already used for card
  attributions), parchment fill with the ink outline used by captions and
  a `highlight_brick` pill behind it so it stays legible over any footage.
  Sized to fit on one line at ≤ 960px wide via `capy.text.fit_text`
  shrink-to-fit, never a fixed character budget.
- **Never overlaps captions.** The banner (y 260–420) sits above every
  caption band (CLIP captions start at y 860); if the banner or a caption
  band ever moves, the caption band wins and the banner is repositioned.
- **Machine-readable spec:** `theme.yaml: layout.response_banner`.
  **Implemented 2026-09-20** in `tools/capy/banner.py` +
  `tools/capy_render_beat_clips.py` (see `hybrid-resolve-pipeline.md`,
  "Response-incoming banner").

**No chips, no wordmark, no on-screen hook text** (apart from the banner
above). The v1 "Source video"/"SOURCE" label chips, the beat-1 hook chip,
and the bottom-right wordmark are all removed — the only text drawn into
any frame is a caption or card/quote text (with its attribution), and
the one-time "RESPONSE INCOMING" banner. The "source visible on screen"
clip-fairness requirement (`script-format.md`) now lives in the video
description instead.

Saint Capybara is always on screen, at the size his current beat's mode
sets: full-screen dominant between clips (HOST), medium beside a
document/chart/quote card (CARD), small in the corner while reacting
over a clip (CLIP) — never smaller than the CLIP-mode size, and evidence
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

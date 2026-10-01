# Saint Capybara — pronunciation dictionary

**2026-09-11: this mechanism is Kokoro-only.** Since the host/quote
voices moved to Chatterbox TTS (`brand.md` sec 6), this dictionary no
longer has any effect on the beats that use it — Chatterbox's tokenizer
has no phoneme-override mechanism at all (plain grapheme BPE), so
`capy_tts.py` skips the `[word](/ipa/)` wrapping step for Chatterbox
beats entirely (still expands `D&C` -> "Doctrine and Covenants" as a
plain literal substitution, since that's engine-agnostic). This is an
accepted, user-approved regression, not a bug: proper-noun pronunciation
on Chatterbox-voiced beats has to be spot-checked by ear per project
instead of forced via this dictionary. This file/mechanism is kept
as-is for any beat still explicitly rendered via `voice: {engine:
kokoro, ...}`.

## Chatterbox respellings and scripture references (2026-09-19)

Two Chatterbox-only fixes in `tools/capy_tts.py`, applied to the text handed
to the model and nowhere else (captions and timing keep the real spelling):

- **`spoken:` on a dictionary entry** — a plain-English respelling that
  Chatterbox reads instead of the word, e.g. `Moroni` -> `moreohnigh`
  (Church guide *mō-rōʹnī*: mo-ROH-nye, ī as in "idle"; **not** -nee).
  Kokoro still uses `ipa:`. Every Book of Mormon name in the Church guide
  now has one, generated from its `respelling:` by
  `tools/capy_bofm_spoken.py` (ī -> "ye"/"eye", ō -> "oh", ē -> "ee",
  ĕ -> "e", ĭ -> "i", schwa -> "uh"; only the first of an "X or Y" pair;
  stress can't be expressed). Familiar names the model already reads
  correctly (Adam, Jacob, Mormon, Alma, Lehi, ...) are skipped
  (`COMMON_OK` in that script). Re-run the script after editing a
  `respelling:`. Verify by ear, then set `verified-by-ear`.
- **Chapter:verse references are spoken as words** — `11:14` is read
  "eleven fourteen" (not "eleven thousand four"), `1:8` "one eight",
  `3:23-25` "three twenty-three through twenty-five". Automatic for every
  `N:M` / `N:M-K` in narration; no per-project entry needed.
- **Loading:** `capy_tts.load_pronunciation_dict` now merges, lowest to
  highest precedence, the full guide (`bofm-pronunciations.yaml`), the seed
  list, then the project file, field by field. The guide is therefore
  active in every project with no copying.

## Mechanism

`tools/capy_tts.py` applies the merged dictionary (project
`script/pronunciations.yaml` entries override/extend
`assets/saint-capybara/templates/pronunciations.yaml`'s seed list) by
whole-word regex substitution before rendering: a word matching a
dictionary entry is rewritten inline as misaki's supported override
syntax, `[word](/ipa/)`, before the text reaches `KPipeline`. See
`misaki/en.py`'s `LINK_REGEX` — this is why entries must be **IPA only**;
the plain-English "respelling" alias form is commented out upstream and
does not work.

## Rule

**Every proper noun that appears in a project's narration needs either a
dictionary entry or an explicit `ok-as-is` note** in that project's
`script/pronunciations.yaml`, before it is ever rendered by
`capy_tts.py`. `capy_check_sources.py`'s `check_pronunciation_coverage()`
(added 2026-09-21) flags proper nouns missing from the merged dictionary
as `info` — a heuristic capitalization scan, so it will miss real cases
and flag some false positives (e.g. a sentence-initial proper noun after
an em dash), never a Gate A blocker — still spot-check by eye per Part A
review checklist item 12.

## Entry format

```yaml
- word: Nauvoo
  ipa: "/nɔˈvu/"
  status: unverified          # unverified | web-sourced <date> | ok-as-is | verified-by-ear <date>
  note: "optional context, e.g. alternate stress heard in practice"
```

`status: unverified` means the IPA is a best-effort guess, not yet
confirmed by listening to a real render. Once the user (or the agent)
listens to a sample containing the word and confirms it sounds right,
update to `verified-by-ear <YYYY-MM-DD>`.

## Look up unique names online (2026-09-18 standing rule)

For any proper noun in a project's narration that is not already in the seed
list or `bofm-pronunciations.yaml` (church fathers, scholars, obscure places,
non-English names, e.g. Athanasius, Eusebius, Deuteronomy), **search the web
for its pronunciation before writing the entry** instead of guessing from
spelling: `WebSearch` "<name> pronunciation IPA", prefer Wiktionary, Collins /
Merriam-Webster / Cambridge, or BibleSpeak.org for biblical and patristic
names, and the Church's own guide for Book of Mormon names. Then:

- Record the IPA and a plain respelling in the `note:`, and name the source.
- Set `status: web-sourced <YYYY-MM-DD>` (between `unverified` and
  `verified-by-ear`). Only a listen-through of a real render earns
  `verified-by-ear`.
- If sources disagree (British vs US, two stresses), pick the US form, and
  note the alternative.
- Common words (Corinthians, Isaiah, Moses) may be marked `status: ok-as-is`
  with no lookup.
- Port newly web-sourced or verified entries back into the shared seed list
  so the next project starts from a checked pronunciation.

Chatterbox ignores this dictionary (see the top of this file), so for
Chatterbox beats the entry is a spot-check reference for the listen-through
(Part B item 1 of `review-checklist.md`), not something the renderer applies.

## Expansion / abbreviation rules

- `D&C` -> always expand to "Doctrine and Covenants" in the text handed
  to TTS (never read as an initialism / letter names).
- Never read any initialism as individual letters unless that is actually
  how it's said aloud (e.g. spell out only if genuinely conventional).
- Numbers in scripture references (e.g. "D&C 132") should be expanded to
  natural speech ("Doctrine and Covenants section one thirty-two") in the
  narration text itself, not left as a raw citation string, since that is
  what a listener actually needs to hear.

## Seed list

`assets/saint-capybara/templates/pronunciations.yaml` seeds ~35 terms most
likely to recur across LDS-history/doctrine videos. Copy it into a new
project's `script/pronunciations.yaml` and add project-specific proper
nouns as they come up; delete entries that never appear in that project's
narration if you want a lean file (optional — extra entries are harmless).

## Book of Mormon name list (loaded automatically)

`assets/saint-capybara/templates/bofm-pronunciations.yaml` is the 342-entry
reference covering every proper noun in the Church's official Book of
Mormon pronunciation guide
(<https://www.churchofjesuschrist.org/study/scriptures/bofm/pronunciation?lang=eng>).
**As of 2026-09-19 `capy_tts.py` loads it in every project** as the lowest
precedence layer (see "Loading" above), so nothing needs copying. Copy an
entry into a project's `script/pronunciations.yaml` only to override it.

Each entry carries:
- `respelling:` — the Church guide's own diacritic notation, verbatim
  (e.g. `nēʹfī` for Nephi) — the source of truth if the `ipa:` field ever
  needs re-deriving.
- `ipa:` — a **mechanical, rule-based conversion** of that respelling to
  IPA (vowel-symbol and stress-mark substitution, no vowel reduction in
  unstressed syllables, no dialect judgment calls). It is a reasonable
  starting guess, not a verified transcription.
- `spoken:` — Chatterbox respelling derived from `respelling:` (see above).
- `status: unverified` on every entry, by design — none of these 342 have
  been checked by ear against a real Kokoro render.

**This is the "build on over time" list**: when a project actually uses a
name from it, copy that one entry into the project's own
`script/pronunciations.yaml`, listen to the render, fix the `ipa:` field
by ear if it's off, and flip `status` to `verified-by-ear <date>` there.
Consider periodically porting newly-verified entries back into this shared
file so the next project that needs the same name starts from a checked
pronunciation instead of the raw mechanical guess.

Where a name also already exists in the general seed list above (Nephi,
Moroni, Lehi, Mosiah, Zarahemla, Cumorah, Nauvoo, Nibley, ...), that seed
entry is hand-curated and takes precedence over this file's mechanical
conversion of the same name.

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
`capy_tts.py`. This is checked manually today (no automated lint yet) —
part of Part A review checklist item 12.

## Entry format

```yaml
- word: Nauvoo
  ipa: "/nɔˈvu/"
  status: unverified          # unverified | verified-by-ear <date>
  note: "optional context, e.g. alternate stress heard in practice"
```

`status: unverified` means the IPA is a best-effort guess, not yet
confirmed by listening to a real render. Once the user (or the agent)
listens to a sample containing the word and confirms it sounds right,
update to `verified-by-ear <YYYY-MM-DD>`.

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

## Book of Mormon name list (growing reference, not auto-copied)

`assets/saint-capybara/templates/bofm-pronunciations.yaml` is a separate,
much larger (342-entry) reference covering every proper noun in the
Church's official Book of Mormon pronunciation guide
(<https://www.churchofjesuschrist.org/study/scriptures/bofm/pronunciation?lang=eng>).
Unlike the general seed list above, **this one is not meant to be copied
wholesale into every project** — pull individual entries into a project's
`script/pronunciations.yaml` as its narration actually needs them.

Each entry carries:
- `respelling:` — the Church guide's own diacritic notation, verbatim
  (e.g. `nēʹfī` for Nephi) — the source of truth if the `ipa:` field ever
  needs re-deriving.
- `ipa:` — a **mechanical, rule-based conversion** of that respelling to
  IPA (vowel-symbol and stress-mark substitution, no vowel reduction in
  unstressed syllables, no dialect judgment calls). It is a reasonable
  starting guess, not a verified transcription.
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

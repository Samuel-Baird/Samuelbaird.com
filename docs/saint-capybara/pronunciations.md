# Saint Capybara — pronunciation dictionary

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

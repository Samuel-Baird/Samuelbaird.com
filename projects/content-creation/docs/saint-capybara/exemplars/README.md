# Exemplar library — worked models for the apologetics playbook

**Added 2026-09-13.** These are real, tool-verified passages from the LDS
apologetics literature (and a couple of non-LDS register models), annotated for
*what to take* and *what not to take*. They exist because
`apologetics-playbook.md`'s "Sharpness" section states the rules in the abstract —
this library shows the rules already working in real texts, so a script writer isn't
inventing the register from scratch on beat one.

## How to use this

1. Before drafting the first response beat and the closing beat, check "By topic"
   below for this video's claim, and "By audience" for who's being answered.
2. Read the 2-3 exemplars that match. Read the whole file, not just "Beat
   translation" — the "Do NOT take" section is as load-bearing as "Take".
3. **Model the move, never paste the words.** Every "Beat translation" line is an
   original Saint Capybara sentence *inspired by* the source's argument shape, not a
   copy of it. Quoting the source itself on screen still follows the normal sourcing
   rules (`research-protocol.md`, `script-format.md`) — this library is about
   register and structure, not on-screen citation.
4. Record which ids you modeled in `beats.yaml`'s `exemplars:` field
   (`script-format.md`). The editor critic checks this at Gate A.
5. A quote inside an exemplar file itself stays ≤15 words, per the same copyright
   discipline as everything else in this repo — paraphrase the rest.

## The register ladder

One rung per register `apologetics-playbook.md`'s "Sharpness" section names, each
with one real, ≤15-word quoted line and its source exemplar. **The jab lives on rungs
3-4. Rung 5 is what it must never sound like on this channel** — Nibley's satire
names real authors and mocks their prose; Saint Capybara's jab targets a standard or
a tradition's record, never a person, and never for more than one dry sentence.

| # | Register | Model | Quoted line |
|---|---|---|---|
| 1 | **Calm** — states the fact, gives the positive case, unhurried | [knowhy-seer-stone](knowhy-seer-stone.md), [evidence-central-titlepage](evidence-central-titlepage.md) | "it is clear that the Title Page is a complicated text" |
| 2 | **Short-form / dry delivery** — verdict first, no hedge, no adjective | [mcclellan-delivery](mcclellan-delivery.md) | (delivery note — no direct quote; see file) |
| 3 | **Pointed** — names the standard being applied and holds it to it | [offenders-are-mormons-christian](offenders-are-mormons-christian.md), [hales-helen-mar-kimball](hales-helen-mar-kimball.md), [hamblin-methodological](hamblin-methodological.md) | "If we don't believe it or do it, it isn't Christian." |
| 4 | **Turnabout** — the critic's own standard, applied to the critic's own tradition | [succession-catholic](succession-catholic.md), [sola-scriptura-protestant](sola-scriptura-protestant.md), the channel's own canon-law-14 line (`apologetics-playbook.md` "Sharpness") | "'Informed opinion' in Salem knew that witchcraft was a serious community problem." |
| 5 | **Satirical ceiling — DO NOT reproduce this register** | [nibley-how-to-write](nibley-how-to-write.md) | "Don't be modest!" (opening a rule that mocks a critic's self-presentation at length) |

Rung 5 is in the library as a boundary marker, not a model to draw from — see its
file's "Do NOT take" section, which is longer than its "Take" section on purpose.

## By topic (common-issues slug → exemplar ids)

| topic | exemplars |
|---|---|
| `different-jesus-different-christology` (are-Mormons-Christian claims) | offenders-are-mormons-christian, peterson-breaking-the-rules |
| `teenage-plural-wives`, `joseph-smith-s-polygamy` | hales-helen-mar-kimball |
| `seer-stone-hat-translation-method` | knowhy-seer-stone |
| `book-of-mormon-historicity`, `book-of-mormon-archaeology` | hamblin-methodological, evidence-central-titlepage |
| `rejection-of-apostolic-succession` | succession-catholic |
| `rejection-of-sola-scriptura` | sola-scriptura-protestant |
| `exaltation-and-humans-becoming-gods` | theosis-interpreter |
| (general — no specific topic) | peterson-breaking-the-rules, nibley-how-to-write, trent-horn-distill, mcclellan-delivery |

## By move

| move | exemplars |
|---|---|
| `opening-frame` | peterson-breaking-the-rules, offenders-are-mormons-christian, sola-scriptura-protestant |
| `damaging-fact` | hales-helen-mar-kimball, knowhy-seer-stone |
| `turnabout` | offenders-are-mormons-christian, hales-helen-mar-kimball, hamblin-methodological, succession-catholic, sola-scriptura-protestant, nibley-how-to-write (structure only) |
| `closing` | peterson-breaking-the-rules, succession-catholic |
| `positive-case` | knowhy-seer-stone, evidence-central-titlepage, theosis-interpreter |
| `distill-then-rebut` | trent-horn-distill |
| `delivery` | mcclellan-delivery |

*(Hand-maintained for this seed set. A future `tools/capy_exemplars.py --index` could
regenerate both tables from each file's YAML header instead of by hand.)*

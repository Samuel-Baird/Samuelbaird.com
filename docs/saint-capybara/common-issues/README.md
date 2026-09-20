# Common issues reference index

One file per recurring LDS-apologetics topic. Each file has four sections:
**General response**, **Catholic response**, **Protestant response**,
**Exmo/atheist response** — see `apologetics-playbook.md`'s audience-specific
playbooks for how these three audiences differ.

Sources/arguments the user gives directly get added straight to the
relevant file(s); sources found independently during other research get
proposed to the user before being added. Images referenced from these
files live under `images/<topic-slug>/`.

Each topic's *worked models* — real texts showing how a strong response to
this kind of claim actually reads — live in `../exemplars/`; check its
`README.md` "By topic" index before drafting a response beat.

## Seeding from FAIR / Scripture Central (2026-09-13)

`leads.yaml` maps a topic slug to the FAIR Answers / Scripture Central KnoWhy /
Evidence Central locators worth mining for that topic — a GSA directory hint
(searched with `search_concordance`) or a live URL, never a pre-verified page.
`/capy-seed-issues <topic...>` fans out one `capy-lead-miner` subagent per
topic; each mines its leads, traces the strongest arguments to a verified
upstream primary/scholarly source, and writes **only**
`proposals/<topic>.md` — it never edits a topic file directly, honoring the
standing rule above even for FAIR-sourced material.

A proposal item is graded (`fact`/`inference`/`disputed`/
`apologetic-claim-unverified`) and starts `accept: false`. The user reviews
proposals (in chat, or on the pushed `seed/<batch>` branch, same round-trip as
a `script.md` review) and flips `accept: true` on what they want added.
`python tools/capy_seed_issues.py apply --topic <slug> --items A1,A3` (or
`--all`) is the only thing that writes a topic file from this workflow — it
inserts the approved rewrite into the right audience section (mapping to the
combined "Catholic and Protestant response" heading when a topic hasn't split
it) and cites only the verified upstream source, never the FAIR/KnoWhy lead
URL itself. `python tools/capy_seed_issues.py lint` validates every proposal
file's grading and sourcing before any of that; it also runs the same
anonymity scan `capy_check_brand.py` runs elsewhere in this repo.

- [adam-god-teachings.md](./adam-god-teachings.md)
- [additional-scripture-beyond-the-bible.md](./additional-scripture-beyond-the-bible.md)
- [angel-of-light-and-a-different-gospel.md](./angel-of-light-and-a-different-gospel.md)
- [baptism-for-the-dead.md](./baptism-for-the-dead.md)
- [blood-atonement-rhetoric.md](./blood-atonement-rhetoric.md)
- [book-of-abraham-translation.md](./book-of-abraham-translation.md)
- [book-of-mormon-anachronisms.md](./book-of-mormon-anachronisms.md)
- [book-of-mormon-archaeology.md](./book-of-mormon-archaeology.md)
- [book-of-mormon-dna-issues.md](./book-of-mormon-dna-issues.md)
- [book-of-mormon-historicity.md](./book-of-mormon-historicity.md)
- [book-of-mormon-population-and-warfare-claims.md](./book-of-mormon-population-and-warfare-claims.md)
- [changes-in-doctrine-over-time.md](./changes-in-doctrine-over-time.md)
- [changes-in-prophetic-teachings-without-clear-mechanisms-for-correction.md](./changes-in-prophetic-teachings-without-clear-mechanisms-for-correction.md)
- [changes-in-teachings-on-interracial-marriage.md](./changes-in-teachings-on-interracial-marriage.md)
- [changes-to-garments-and-temple-practices.md](./changes-to-garments-and-temple-practices.md)
- [church-disciplinary-practices.md](./church-disciplinary-practices.md)
- [church-finances.md](./church-finances.md)
- [circular-testimony-epistemology.md](./circular-testimony-epistemology.md)
- [continuing-prophets-and-revelation.md](./continuing-prophets-and-revelation.md)
- [correlation-and-institutional-control.md](./correlation-and-institutional-control.md)
- [development-of-priesthood-restoration-narratives.md](./development-of-priesthood-restoration-narratives.md)
- [differences-among-first-vision-accounts.md](./differences-among-first-vision-accounts.md)
- [different-jesus-different-christology.md](./different-jesus-different-christology.md)
- [different-understanding-of-original-sin.md](./different-understanding-of-original-sin.md)
- [doubt-your-doubts-discouragement-of-skepticism.md](./doubt-your-doubts-discouragement-of-skepticism.md)
- [egyptian-papyri-and-facsimiles.md](./egyptian-papyri-and-facsimiles.md)
- [emma-smith-s-knowledge-of-plural-marriages.md](./emma-smith-s-knowledge-of-plural-marriages.md)
- [emotional-elevation-being-mistaken-for-revelation.md](./emotional-elevation-being-mistaken-for-revelation.md)
- [eternal-marriage-and-sealing.md](./eternal-marriage-and-sealing.md)
- [exaltation-and-humans-becoming-gods.md](./exaltation-and-humans-becoming-gods.md)
- [excommunications-of-prominent-members.md](./excommunications-of-prominent-members.md)
- [family-pressure-surrounding-belief-and-leaving.md](./family-pressure-surrounding-belief-and-leaving.md)
- [first-vision-accounts.md](./first-vision-accounts.md)
- [freemasonry-and-the-temple-endowment.md](./freemasonry-and-the-temple-endowment.md)
- [gender-hierarchy-in-church-leadership.md](./gender-hierarchy-in-church-leadership.md)
- [god-once-being-as-humans-are-divine-progression.md](./god-once-being-as-humans-are-divine-progression.md)
- [god-the-father-having-a-physical-body.md](./god-the-father-having-a-physical-body.md)
- [great-apostasy-and-restoration-claims.md](./great-apostasy-and-restoration-claims.md)
- [handling-of-sexual-abuse-cases-abuse-help-line-and-clergy-penitent-privilege.md](./handling-of-sexual-abuse-cases-abuse-help-line-and-clergy-penitent-privilege.md)
- [high-demand-religion-control-criticisms.md](./high-demand-religion-control-criticisms.md)
- [historical-temple-ceremony-changes.md](./historical-temple-ceremony-changes.md)
- [invalidity-of-lds-baptism.md](./invalidity-of-lds-baptism.md)
- [joseph-smith-1826-glass-looking-hearing.md](./joseph-smith-1826-glass-looking-hearing.md)
- [joseph-smith-as-a-false-prophet.md](./joseph-smith-as-a-false-prophet.md)
- [joseph-smith-s-egyptian-alphabet-and-grammar-materials.md](./joseph-smith-s-egyptian-alphabet-and-grammar-materials.md)
- [joseph-smith-s-failed-or-disputed-prophecies.md](./joseph-smith-s-failed-or-disputed-prophecies.md)
- [joseph-smith-s-polygamy.md](./joseph-smith-s-polygamy.md)
- [kinderhook-plates.md](./kinderhook-plates.md)
- [kjv-material-in-the-book-of-mormon.md](./kjv-material-in-the-book-of-mormon.md)
- [lds-priesthood-authority.md](./lds-priesthood-authority.md)
- [lds-rejection-of-the-nicene-trinity.md](./lds-rejection-of-the-nicene-trinity.md)
- [lds-views-of-the-creator-creature-distinction.md](./lds-views-of-the-creator-creature-distinction.md)
- [lgbtq-teachings-and-policies.md](./lgbtq-teachings-and-policies.md)
- [limited-use-of-the-plates-during-translation.md](./limited-use-of-the-plates-during-translation.md)
- [missionary-pressure-and-expectations.md](./missionary-pressure-and-expectations.md)
- [past-prophetic-explanations-for-the-racial-restriction.md](./past-prophetic-explanations-for-the-racial-restriction.md)
- [plural-marriage-sexual-relations.md](./plural-marriage-sexual-relations.md)
- [plurality-of-gods.md](./plurality-of-gods.md)
- [possible-19th-century-influences-on-the-book-of-mormon.md](./possible-19th-century-influences-on-the-book-of-mormon.md)
- [preexistence-of-human-spirits.md](./preexistence-of-human-spirits.md)
- [prophetic-fallibility-versus-prophetic-authority.md](./prophetic-fallibility-versus-prophetic-authority.md)
- [public-denials-of-polygamy.md](./public-denials-of-polygamy.md)
- [race-and-the-priesthood-temple-restriction.md](./race-and-the-priesthood-temple-restriction.md)
- [rejection-of-apostolic-succession.md](./rejection-of-apostolic-succession.md)
- [rejection-of-creation-ex-nihilo.md](./rejection-of-creation-ex-nihilo.md)
- [rejection-of-infant-baptism.md](./rejection-of-infant-baptism.md)
- [rejection-of-justification-by-faith-alone.md](./rejection-of-justification-by-faith-alone.md)
- [rejection-of-sola-scriptura.md](./rejection-of-sola-scriptura.md)
- [reliance-on-feelings-to-establish-historical-claims.md](./reliance-on-feelings-to-establish-historical-claims.md)
- [salvation-requiring-works-ordinances-and-covenants.md](./salvation-requiring-works-ordinances-and-covenants.md)
- [secrecy-surrounding-plural-marriage.md](./secrecy-surrounding-plural-marriage.md)
- [seer-stone-hat-translation-method.md](./seer-stone-hat-translation-method.md)
- [sexual-purity-culture.md](./sexual-purity-culture.md)
- [shame-surrounding-masturbation-pornography.md](./shame-surrounding-masturbation-pornography.md)
- [social-costs-of-leaving-the-church.md](./social-costs-of-leaving-the-church.md)
- [spiritual-versus-physical-descriptions-of-seeing-the-plates.md](./spiritual-versus-physical-descriptions-of-seeing-the-plates.md)
- [spiritual-witnesses-not-being-unique-to-mormonism.md](./spiritual-witnesses-not-being-unique-to-mormonism.md)
- [strengthening-church-members-committee.md](./strengthening-church-members-committee.md)
- [teenage-plural-wives.md](./teenage-plural-wives.md)
- [temple-ordinances.md](./temple-ordinances.md)
- [temple-recommend-interviews.md](./temple-recommend-interviews.md)
- [three-and-eight-witnesses.md](./three-and-eight-witnesses.md)
- [three-degrees-of-glory-lds-afterlife.md](./three-degrees-of-glory-lds-afterlife.md)
- [tithing-requirements.md](./tithing-requirements.md)
- [transgender-policies.md](./transgender-policies.md)
- [treatment-of-dissenters-and-critics.md](./treatment-of-dissenters-and-critics.md)
- [unfalsifiability-of-truth-claims.md](./unfalsifiability-of-truth-claims.md)
- [women-and-priesthood.md](./women-and-priesthood.md)
- [worthiness-interviews.md](./worthiness-interviews.md)

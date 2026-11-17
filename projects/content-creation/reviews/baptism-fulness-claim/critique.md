# Critique — baptism-fulness-claim

Two full critique cycles were run (three lenses each: editor, factcheck,
opponent) because the first cycle surfaced enough BLOCKERs to warrant a
substantial script rewrite rather than word-level patches, and the second
cycle (against that rewrite) surfaced a regression plus several real
remaining issues. This file reflects the final state after both cycles plus
one more manual fix pass against the second cycle's findings.

## Resolved (across both cycles)

- **[BLOCKER]** Hook stated a claim ("nothing to do with forgiving sin") the
  source clip never made — rewritten to concede the literal claim and locate
  the actual error.
- **[BLOCKER]** `n01` imputed motive ("smuggle in") to a "Today I realized"
  personal-impression post — rewritten to name the unstated inference without
  speculating about intent.
- **[BLOCKER]** `q02`'s on-screen D&C 20:37 card asserted the *opposite* of
  the verse's actual sequential grammar (claimed simultaneity; the verse
  sequences remission-evidenced-before-the-font, then church-reception at
  baptism) — rewritten to state the sequence honestly.
- **[BLOCKER]** (regression caught on re-check) `n05` said the either-or "was
  invented for one sentence about Mormons," reintroducing motive-imputation
  in a new beat — removed; the beat now argues from cross-tradition
  comparison only.
- **[MAJOR]** Confirmation — both red-team briefs' "honest hinge" — was
  entirely absent. New beat `q03` supplies it (2 Nephi 31:17, full verse now
  on the card, not a truncated fragment that read for the critic).
- **[MAJOR]** The hidden assumption (that a rite can only serve one purpose)
  was asserted, never named or tested. New beat `n05a`/`q05b` names it and
  tests it against three traditions (Westminster, Catholic Catechism,
  Baptist Faith and Message).
- **[MAJOR]** The concession beat (`n04`→`n06a`/`n06b`) conceded the cheaper
  claim (member confusion) instead of the institutional one (Gospel Topics
  page ordering, the baptismal prayer's silence on sin, the "completed and
  properly recorded" handbook condition) — rewritten to concede the
  institutional facts plainly, corroborated by the Hales quote rather than
  led by it. Ending was also fixed so it doesn't pivot the target back to
  "the doctrine" after conceding the ordinance-level point.
- **[MAJOR]** `q05`(old)/`n99` contradicted each other on whether "Christians"
  believe baptism washes away sin — resolved; the Baptist example is now
  correctly framed as "which Christians?" rather than a blanket "we're
  normal" claim, and `n99` no longer generalizes about Christian history.
- **[MAJOR]** `q02`'s "one act, not two competing options" and later "four
  steps of one gate" list misattributed 2 Nephi 31:17's sequence onto D&C
  20:37 — the fabricated four-step list was removed from `q02` entirely;
  the sequence now lives correctly split across `q02` (D&C 20:37 only) and
  `q03` (2 Nephi 31:17 only).
- **[MAJOR]** `q03`'s "minutes apart, same service" overstated confirmation
  timing (General Handbook 18.8 allows same-service *or* later, "as soon as
  possible after," for converts) — corrected, sourced to Handbook 18.8.
  directly.
- **[MAJOR]** Q2 of the pre-publish two-question test (does the script show
  the LDS account is *better*, not just defensible?) failed entirely in both
  cycles. New beat `n07` argues the positive case: LDS doctrine's
  "retain/lose a remission" structure (Mosiah 4:12, D&C 82:7) explains
  ongoing post-baptismal repentance more completely than a one-time
  transactional washing does.
- Sprawl (editor, cycle 2): the script had grown to a beat count/overlap the
  format's 2-4-group guidance warns against, with two beats making
  overlapping "same standard" arguments. Consolidated into one group
  (`n05a`/`q05b`).
- Several MINORs from both cycles: pose-hold time on two overlong beats
  (split `q05`→`n05a`+`q05b`, `n06`→`n06a`+`n06b`); clip end trimmed to match
  the actual last transcript word (11.46s, was 13.0s); `q02`'s "already
  begun" softened back to "already received" to match the verse's own tense
  and strengthen rather than hedge the argument; hook polish.

## Open — left for your review

- **[MAJOR, unresolved]** The baptismal-interview language (General Handbook
  31.2.3) never uses the word "remission" — one of the four "easiest
  comebacks" both red-team briefs named — is still not engaged anywhere in
  the script. I didn't chase this further because it would need a fresh,
  independently-verified source rather than a text edit, and I'd already
  gone through two full critique cycles. If you want it addressed, the
  natural place is an addition to `n06b`.
- **[MINOR]** The positive-case beat (`n07`) argues from Mosiah 4:12/D&C 82:7
  (retain/lose a remission) rather than the alternative the opponent-critic
  suggested (Acts 2:38 followed by Acts 2:41, "in order"). Both are valid;
  I went with the retain/lose framing since it's already fully sourced in
  this project, but flagging the alternative in case you prefer it.
- **[MINOR]** `n05a`'s "two very different Christian traditions" framing is
  intentionally narrower than a universal claim about all of Christianity,
  per brand.md's precision rule — worth a glance to confirm it reads
  naturally rather than oddly hedged.

Total runtime: 162.3s (budget 60-180s). `capy_check_sources.py` and
`capy_check_brand.py` both pass with 0 errors, 0 warnings.

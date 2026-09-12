# Critique — mormon-irony

## BLOCKER
None found by any of the three lenses.

## MAJOR
- [factcheck] n01 cited `mason-planted-2019-p136`, but that source is actually about the claim-6 "Christian" definitional fork (devotion vs. creedal), not n01's own point (that claiming full authority isn't the same move as refusing to call others Christian). **Fixed**: removed the mismatched citation and marked `n01` `opinion: true`, since it's the channel's own logical/analytic point rather than an externally-sourced claim. Re-checked clean against `capy_check_sources.py`/`capy_check_brand.py`.
- [opponent] The claim-6 response (`n05`-`n07`) shows the clip's "historically accurate" framing begs the question but never argues the Christ-centered definition is actually *better* for the question the clip is asking (is LDS theology part of historic/creedal Christianity) — the exact Q2 failure mode the playbook and `brand.md` §2 warn about ("merely shown theirs isn't airtight," not "made the positive case"). The red-team brief already named this as the sharpest remaining objection.
- [opponent] `n03`/`n04` concede the red-team's degree-asymmetry point (the LDS apostasy claim is total, not just "better authority") but never actually rebut it — they restate the narrow logical point from `n01` instead of answering the comeback the research surfaced.
- [editor] The closing beat (`n99`) resolves only claim 6 (the contested definition of "Christian") and never ties back to claim 5 ("you excluded yourself" logic) — the two-claim structure only counts as defensible "one argument, two facets" if the punchline closes both facets, and as written it closes only one.
- [editor] Claim 5's rebuttal (`n01`-`n04`) stays purely negative (critic's inference is invalid + Catholics do something similar) without giving the affirmative LDS position — claim 6's arc does this correctly (Hinckley's positive "faith in and reliance on Christ" framing); claim 5's should match it.

## MINOR
- [opponent] `e01`'s CDF quote is a reasonable but not perfectly tight match to its framing line.
- [opponent] Audience is marked protestant throughout, but claim 6's "historically accurate" framing reads more like a secular-journalist/academic register — worth a look, not a blocker.
- [opponent] Tone is fine throughout; no polemics found.
- [factcheck] `n02`/`e01`'s CDF quote was independently re-verified directly against the Vatican text (exact match) and its `verification.verdict` upgraded from `direct-read` to the stronger bar this pass applies; same for the Packer source (`word-forms` → `exact` via `verify_quote`, though it's never an on-screen attributed quote so this wasn't blocking).
- [factcheck] No doctrine-tier or overclaiming problems found; claim 6's `disputed` grade matches the script's "begs the question" (not "is false") framing.
- [editor] Response-to-clip alignment independently re-verified word-by-word against `transcripts/source.json` — `c02`/`c03`'s boundaries land cleanly on word edges, no misalignment.

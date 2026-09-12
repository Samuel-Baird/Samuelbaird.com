# Critique — baptism-for-dead-thought

## BLOCKER
- [factcheck] n06 — stated "Nobody gets added to a roll" as flat fact, but `research/claims.md` explicitly records this sub-claim as "Could not verify" against the available corpus (no cited source -- Burton 1965, Nelson 1994, McGregor 1920 -- mentions membership rolls/records at all). **Fixed**: reworded to "It's an offer, not an enrollment. The person on the other side still has to accept it themselves -- nothing about that is automatic," which keeps the sourced agency/choice point and drops the unverified roll-mechanics assertion. Re-checked clean against `capy_check_sources.py`/`capy_check_brand.py`.

## MAJOR
- [opponent] n04/e01 — state "real priesthood authority" with more certainty than the research supports. `claims.md` grades the overall conclusion as *inference*, and the claim-3 red-team brief explicitly flags this as an overclaim: John's priesthood authority is demonstrated within LDS canon, not independently verifiable, and the steelmanned circularity objection ("what non-circular test distinguishes John's authority from any other tradition's claimed succession?") is never raised or answered on screen.
- [opponent] Unaddressed red-team objections on claims 2 and 4 — the "grace-through-means arguments prove too much" objection (claim 2) and the unfalsifiability-of-postmortem-choice objection (claim 4) are both surfaced in research but not acknowledged in the script, even briefly.
- [opponent] Script-level Q2 (playbook pre-publish test) — the script corrects three misconceptions but never makes the positive case that the LDS account is *better*, only that the critic's framing isn't airtight.
- [editor] Sprawl across three claims — the title/hook promise the flagship "does Jesus need one too" question, but claims 2 and 4 get comparable runtime, pushing the flagship claim to ~18.6s in and diluting it against the apologetics-playbook's "one argument per short" guidance.
- [editor] n01 skips naming/testing the grace-vs-ordinance hidden assumption (playbook step 2/3, "the move most often skipped") before asserting the LDS position.
- [editor] n99's closing theme ("nobody's faith gets overridden") was never actually argued in the body — it doesn't land the video on its own flagship argument (Jesus already validly baptized by an authorized priesthood holder).
- [factcheck] n01 ("Grace and ordinances aren't rivals here") states an inference-grade claim without the hedge ("Latter-day Saints believe...") that the adjacent card (n02) correctly uses.

## MINOR
- [opponent] e01's card quote (McConkie 1977) is a reasonable but not tight match to the narration's specific point about John's authority vs. Jesus' need.
- [opponent] Internal tension between "ordinances matter enough to require" (n01/n02) and "it's just an offer" (n06) isn't reconciled on screen.
- [editor] c02's "Original Video Transcript" field in `script.md` displays the whole overlapping Whisper segment, including the profanity cut from the actual clip span (13.5s-20.84s) -- a display quirk in `capy_storyboard.py`'s segment-level lookup, not an error in the clip's actual boundaries (the profanity is correctly excluded from what plays).
- [factcheck] Minor sources.yaml data-hygiene items (a malformed `verification` field on the McConkie entry; a near-duplicate Nelson-1994 source-id pair) -- both independently re-verified as fine, no actual inaccuracy.

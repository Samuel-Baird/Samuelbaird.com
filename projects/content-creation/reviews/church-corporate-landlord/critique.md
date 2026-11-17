# Critique — church-corporate-landlord

Three independent lenses (opponent, factcheck, editor) ran in parallel
against the finished `script.md`. All BLOCKERs have been fixed and
re-verified; remaining MAJOR/MINOR findings are listed below for your
review at Gate A.

## BLOCKER (all fixed, 1 recheck cycle)

- [factcheck] `n01`/`n02` — Palantir/TKO dollar figures rested on three
  mutually-contradictory research passes over the same SEC 13F filing.
  **Fixed**: orchestrator deterministically re-parsed the actual XML
  (curl + python, not an LLM summary) and confirmed: Palantir =
  $168,860,458 (0.28% of the $60.82B portfolio), TKO = $1,620,546
  (0.0027%). `sources.yaml`'s corrupted entry corrected; re-verified
  independently by the recheck pass.
- [factcheck] `n02` — Stated the "it's just index-fund incidental
  exposure" framing as flat fact though `claims.md` grades it `disputed`.
  **Fixed**: reworded to acknowledge the fund actively picks individual
  stocks, so market-weight-consistency is suggestive, not proof.
- [factcheck] `n04b` — Cited a 2019-12-17 statement as evidence the
  "prepare for the future" framing predates the controversy, when that
  statement actually postdates the whistleblower story by about a week.
  **Fixed**: now cites only the 2018 statement, which genuinely predates
  the story by 19 months.

## MAJOR (fixed)

- [opponent] `n08`/`n09` never answered the red-team's predicted sharpest
  comeback — "if saving for the future is legitimate, why 22 years of
  shell companies instead of just disclosing?" **Fixed**: `n08` now cites
  the Church's own 2023 statement that it relied on legal counsel
  specifically to keep the portfolio private, and calls that "a real
  answer, not a good one."
- [opponent] `n02` overclaimed pure passive-index mechanism for a fund
  that actively picks individual equities. **Fixed** (same edit as the
  factcheck BLOCKER above).
- [opponent] `n04b` conflated two different Church statements' dates.
  **Fixed** (same edit as the factcheck BLOCKER above).
- [factcheck] `n05` — Blackstone-structure claim outran its sole cited
  source (background-only). **Partially fixed**: reworded to a narrower
  "no outside investors" claim and added a second source; the recheck
  pass downgraded this to MINOR (neither source states that specific
  fact verbatim, though it is a straightforward legal inference from
  501(c)(3)/no-shareholder structure — see below).
- [factcheck] `n06` — Implied churches' Form 990 exemption specifically
  covers Ensign Peak as a separate entity, which the cited IRS page
  doesn't confirm. **Fixed**: reworded to the narrower, fully-sourced
  claim that the fund's size only became public via SEC enforcement,
  never voluntary disclosure.
- [factcheck] `n04` — "$124 billion... from a 2019 leak" wasn't
  supported by either cited source, and the actual 2019 whistleblower
  complaint cited ~$100B, not $124B. **Fixed**: reworded to "a 2019
  whistleblower complaint, which actually cited around a hundred
  billion," properly cited.
- [editor] No bridging line between the three argument clusters — read
  as three fact-checks stapled together until the closing beat. **Fixed**:
  added transition lines at the end of `n03` and `n06`.

## MINOR (left for your review — not fixed)

- [factcheck→recheck] `n05` — The "no outside investors" structural claim
  is a defensible legal inference from Ensign Peak's 501(c)(3)/no-
  shareholder structure, but neither cited source states it in those
  words directly. If you want this airtight rather than inferential,
  it would need a source that explicitly discusses EPA's fiduciary
  structure (one exists in `sources.yaml`, `fiduciary-duty-endowments-
  reinhartlaw`, but is currently `inspected: false`).
- [opponent] Tone/sharpness on the Cluster A close (`n03`) could be a
  touch more pointed given how clean the concession is — minor polish,
  not a substance issue.
- [editor] Minor pacing note: three concession beats (`n03`, `n06`,
  `n08`) in one ~180s video is a lot of "yes, but" — each concedes a
  *different* thing (screening gap / transparency gap / secrecy motive),
  so it isn't the redundant "some criticism has merit" restatement
  `brand.md` warns against, but watch the cumulative tone on a listen-
  through.

## Summary

**3 BLOCKER found and fixed** (beats: n01, n02, n04b). **4 MAJOR found
and fixed**, 1 downgraded to MINOR after recheck. **3 MINOR left for your
review** (none blocking).

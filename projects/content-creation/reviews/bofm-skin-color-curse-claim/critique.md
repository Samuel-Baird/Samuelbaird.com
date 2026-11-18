# Critique — bofm-skin-color-curse-claim

Four rounds of `/capy-critique` were run as the script was revised in response to
findings. This file records the final state; `research/critique-opponent.md`,
`research/critique-factcheck.md`, and `research/critique-editor.md` hold each
lens's full final-round detail.

## Resolved across the revision rounds

- **BLOCKER (capy-critic-opponent, round 2):** the script's own "one skin-tone
  detail / one rebellious generation / one story" framing was itself inaccurate
  -- the curse-and-reward skin-color language recurs across 2 Nephi 5, Alma 3,
  and 3 Nephi 2. Fixed: `n04`/`n04b`/`n99` now say "more than once" and name
  both the curse and reward framings explicitly.
- **MAJOR (capy-critic-factcheck, round 2):** the `mauss-2003-all-abrahams-children`
  citation backing "helped justify the Church's former priesthood restriction"
  didn't actually verify that specific claim (Mauss's recorded quote was just
  him quoting Alma 3:6). Fixed: swapped to `frame-1968-dialogue-skin-blackness-priesthood`
  (Dialogue: A Journal of Mormon Thought, vol. 3 no. 2), tool-verified to
  actually make that connection; independently re-verified by factcheck.
- **MAJOR (capy-critic-opponent, round 3):** the fix created a new problem --
  `n04b` ended cold on the damaging fact with no reframe in the same beat (a
  bare concession beat, against brand.md's "On true claims" rule and the
  `hales-helen-mar-kimball` exemplar). Fixed: moved the "Today's Church
  corrects that directly, not quietly" line onto the end of `n04b`.
- **MAJOR (capy-critic-editor, rounds 1-2):** the six-step response structure
  skipped naming/testing the hidden assumption, and the video never actually
  answered the red-team brief's flagged "strongest objection" (the mark/reward
  framing in Alma 3:6 / 3 Nephi 2:15). Fixed: `n01` now names the assumption;
  `n04` explicitly puts both the curse and reward framing on screen instead of
  only the single "skin of blackness" phrase.
- **Also added (capy-critic-opponent, round 1):** the direct textual rebuttal
  to "you'll win everything" (Mormon 8:2 -- the "white"/winning side's own
  historian describing their people's destruction) was available in the
  research but never reached the original script. Now `n01`/`q01`.

## Remaining, not fixed further (reported, not hidden)

- **MINOR (capy-critic-opponent):** the declared `exemplars: [hales-helen-mar-kimball]`
  models the "true fact + reframe in one breath" move well, but no exemplar in
  `docs/saint-capybara/exemplars/README.md`'s topic table actually covers
  race/curse material -- flagged as a documentation gap in that library, not a
  fix owed to this script specifically.
- **MINOR (capy-critic-opponent):** `n03` cites Jacob 3:5-9 as a range; verse 8
  specifically ("their skins will be whiter than yours") isn't separately
  called out on screen, though it's within the cited range and consistent with
  what `n04` already discloses about the reward framing.
- **MINOR (capy-critic-factcheck):** a few `word-forms`-verified citations
  (2 Ne 5, 3 Ne 2, Alma 3) could be upgraded to `exact`/`page-read` in
  `sources.yaml` now that factcheck independently reconfirmed them directly
  against primary text this session -- a bookkeeping precision improvement,
  not a correctness issue.
- **MINOR (capy-critic-editor):** the closing beat is a legitimate verdict but
  arguably less quotable than `q01`'s Mormon 8:2 line -- a taste call, not a
  rule violation.
- **Open, surfaced to the user separately:** `research/claims.md`'s Escalation
  note -- the historian brief's sec 12 trigger 6 concern (the priesthood
  restriction's own causal origin has no full explanation even in current
  Church materials) is scoped out of this video (which only addresses what the
  Book of Mormon's text says, not why the restriction existed/ended), but is
  flagged for the user's own judgment rather than decided unilaterally.

## Lint status (final)

`capy_check_sources.py`, `capy_check_brand.py`, `capy_check_tone.py`: all pass,
0 errors, 0 warnings. Runtime 99.5s (budget 60-180s).

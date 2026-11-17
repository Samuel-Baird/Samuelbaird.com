# Critique — brigham-young-transfiguration-claim

**Method note:** `/capy-critique` (three subagent lenses) was NOT run; this is a single-session self-critique through the same three lenses. Run `/capy-critique` before Gate B if you want the independent pass.

## Fact-check lens

- **BLOCKER (fixed): "Carrington speech" framing.** First draft treated the 1857 item as a Carrington speech. The primary text (CDBY vol. 3 p.106; Welch doc. 80) is Brigham Young describing Carrington's experience. Script now says so (n08, q03, n09, n14).
- **MAJOR (fixed): Brooke letter scope.** Brooke is a general resemblance remark made 3 months later, not a description of Aug 8. n01 says "date is wrong"; e01 says "favours Brother Joseph, in person and manner of speaking" and does not say it describes the meeting.
- **MAJOR (fixed): Egan "the Conference".** Could be the October 1844 conference. q02 says "about the conference" and "within four months", never "on August 8".
- **MAJOR (fixed): Sep 2 1844 line is about "the Twelve".** n03 says so explicitly, and calls it the mildest item.
- **MINOR (open): "over a hundred".** Counts differ by edition (101/57 in 1996; 129/68 in the Welch volume). n16 says "over a hundred" for that reason.
- **MINOR (open): handcart deaths "about 220".** Turner: Willie "nearly seventy", Martin "roughly 150". Total is Turner's sum; other counts run 200-280. Narration says "about 220".
- **MINOR (open): Welch edition year not confirmed.** sources.yaml says 2005.
- **Unverified:** Times and Seasons pages themselves were not opened (read via Complete Discourses of Brigham Young and via Quinn/Jorgensen). The 15 Oct 1844 anonymous letter is second-hand (Van Wagoner n.54) and is not on screen.
- Hyde: "diaries put him in Nauvoo five days after the meeting" — Welch n.75 (Woodruff diary, Aug 13). OK.

## Defends-the-Church lens (opponent)

- Strongest remaining objection: none of the earliest sources describes a physical transformation; all detailed accounts are retrospective; Brigham's own same-day diary and talk say nothing of a miracle ("walk by faith"). **Addressed**: n01 (history can't test miracles), n03, n17, n20 concede only what the record concedes, and the script claims "people reported it early and said it was striking", not "it was a miracle".
- Brigham's remark that "men's eyes are liable to be deceived" (q03 card) is a double-edged quote. Kept on screen deliberately because it is the sentence the 1857 date comes from; n09 does not claim Brigham endorsed a miracle.
- The handcart group **concedes real leadership failure** (Turner: "could have prevented most of the deaths"; Young denounced Richards and Spencer). This is deliberate: a defence that denied it would cost the channel credibility. It is not framed as Brigham "for no reason"; it gives the documented financial reason and the rescue. No claim is made that Protestants or mobs caused the handcart deaths (no source supports it).

## Editor lens (compelling / tone)

- Sharpness: first response sentence (n01) is the position, no agreement. Closing (n99) is the punchline. One jab (long-form cap is two): the closing beat. The earlier Yale-letter jab (n05) was removed at the user's request after Gate A edits. The user also asked for a closing line saying the sources are more trustworthy than the creator's narrative; it was added as 'far more trustworthy' (not 'certain', which would outrun the evidence grade of the transfiguration itself).
- Concession tells: `capy_check_tone.py` clean.
- Length: ~330s estimate vs 60-180 default; `format` widened to 240-480 deliberately (user asked for long-form).
- Weak spots to consider at Gate A: n11 is long (about 13s); n20's two middle sentences are a little abstract; c07 (15.5s) is the longest clip.
- Sensitive: `sensitive: true` set because of the handcart deaths; no amused/happy poses; the handcart beats lead with the harm.
- `deadpan` pose swapped out (sprite defect flagged by the storyboard).

## Post-Gate-A edits (user)

q01 now reads the quote aloud; new card q01b carries the exact Brooke quote; n05 removed; n17 uses 'Jorgensen' instead of a pronoun (author's pronouns not stated in the source); e02 reworded to 'first time she ever recorded the thought'; closing extended; caption no longer mentions Yale. Lints: 0 errors; source time 29.5% of runtime.

## Second revision (user)

Added: n11b (the Saints were in the Great Basin because they were driven out: Missouri 1838 extermination order, Nauvoo 1846), n18b/n18c (early and later accounts line up; recall-by-transmission, with the user's 9/11 comparison). Applied: q02 reads the Egan quote; n04 gained a sentence that the 'twelve years' claim does not survive a check against the record (the user's 'creator is lying or didn't do due diligence' wording was NOT used: it imputes motive or bad faith, which brand.md sec 2 forbids); n07 (Hyde) dropped; n15 gained the 'depends on the incorrect pre-1857 claim' sentence. Open flags: (1) 'Protestant' not used: no source in hand says who the mobs were; (2) n18c's 9/11 analogy conflicts with research-protocol sec 11 ('No analogies' on sensitive videos); kept because the user asked for it explicitly; (3) the Egan sentence is Little quoting Egan 'at the time of the Conference'; the user's wording 'talking about hearing Brother Brigham' was NOT used because the source does not say what Egan was describing.

## Third revision (user)
q03 reads the 1857 quote aloud; n09 loses its last sentence; e02/e03 now introduce and new cards q04 (Crosby) and q05 (Hoyt) read the exact quotes; n18 ends 'Both predate the 1857 date'; closing now states the count: 'at least nine sources from before 1857' = T&S 2 Sep 1844, Brooke, Hinckley, Egan/Little, Woodruff, Burton, Crosby, Hoyt, Bullock (each page-read in GSA). The anonymous T&S 15 Oct 1844 letter is second-hand and is NOT counted. Several of the nine are mantle-language only, not appearance descriptions (see n03); the closing counts them as sources against 'no one talking about it', not as nine transfiguration descriptions.

## Build notes (post-approval)
Audio QC against the exported file caught `n02` voiced as "The first record is in 1857" (TTS dropped the contraction in "isn't", inverting the claim). Fixed by rewording to "is not". `e02` reworded ("the date the video gives") after "claimed" was clipped to "claim". Egan respelled "eegan". Final export transcribed and diffed against beats.yaml: remaining diffs are transcriber spellings only (Catharine/Catherine, favours/favors, Hyrum/Hiram, Lynne/Lynn, numerals), spot-checked n01/n10 with the medium model. Final: exports/brigham-young-transfiguration-claim.mp4, 399.7s. Note: Resolve's set_transform (Tilt/Pan) did not move overlay items in this build; evidence overlays were repositioned by editing the overlay assets instead.

## Round 2 build fixes (user watch-through)
c04 cut "eighteen fifty-seven" in half (end 54.3s; the word's speech runs to ~54.65s): end moved to 54.72s, c05 start 54.8s; verified in the export ("...was in 1857." whole). n08 had a 1.28s pause between "Carrington." and "That's": trimmed to 0.30s (audio/n08.norm.wav + timing.json shifted; originals in qc/orig/); export gap now ~0.4s. Docs updated: script-format.md (Show the receipt; clip cut points; TTS contractions), review-checklist.md (items 18, 4b), hybrid-resolve-pipeline.md and resolve-mcp-gotchas.md (overlay mechanics); capy_render_beat_clips.py now pads evidence beats to a 3.0s minimum.

# Critique — brigham-young-transfiguration-claim

**Method note:** `/capy-critique` (three subagent lenses) was NOT run; this is a single-session self-critique through the same three lenses. Run `/capy-critique` before Gate B if you want the independent pass.

## Fact-check lens

- **BLOCKER (fixed): "Carrington speech" framing.** First draft treated the 1857 item as a Carrington speech. The primary text (CDBY vol. 3 p.106; Welch doc. 80) is Brigham Young describing Carrington's experience. Script now says so (n08, q03, n09, n14).
- **MAJOR (fixed): Brooke letter scope.** Brooke is a general resemblance remark made 3 months later, not a description of Aug 8. n01 says "date is wrong"; e01 says "favours Brother Joseph, in person and manner of speaking" and does not say it describes the meeting.
- **MAJOR (fixed): Egan "the Conference".** Could be the October 1844 conference. q02 says "about the conference" and "within four months", never "on August 8".
- **MAJOR (fixed): Sep 2 1844 line is about "the Twelve".** n03 says so explicitly, and calls it the mildest item.
- **MINOR (open): "over a hundred".** Counts differ by edition (101/57 in 1996; 129/68 in the Welch volume). n16 says "over a hundred" for that reason.
- **MINOR (open): handcart deaths "about 220".** Turner: Willie "nearly seventy", Martin "roughly 150". Total is Turner's sum; other counts run 200-280. Narration says "about 220".
- **MINOR (open): "in print since at least 1994".** Based on Quinn 1994 p.182 citing the letter at Yale; an earlier printing may exist. Wording is "at least".
- **MINOR (open): Welch edition year not confirmed.** sources.yaml says 2005.
- **Unverified:** Times and Seasons pages themselves were not opened (read via Complete Discourses of Brigham Young and via Quinn/Jorgensen). The 15 Oct 1844 anonymous letter is second-hand (Van Wagoner n.54) and is not on screen.
- Hyde: "diaries put him in Nauvoo five days after the meeting" — Welch n.75 (Woodruff diary, Aug 13). OK.

## Defends-the-Church lens (opponent)

- Strongest remaining objection: none of the earliest sources describes a physical transformation; all detailed accounts are retrospective; Brigham's own same-day diary and talk say nothing of a miracle ("walk by faith"). **Addressed**: n01 (history can't test miracles), n03, n17, n20 concede only what the record concedes, and the script claims "people reported it early and said it was striking", not "it was a miracle".
- Brigham's remark that "men's eyes are liable to be deceived" (q03 card) is a double-edged quote. Kept on screen deliberately because it is the sentence the 1857 date comes from; n09 does not claim Brigham endorsed a miracle.
- The handcart group **concedes real leadership failure** (Turner: "could have prevented most of the deaths"; Young denounced Richards and Spencer). This is deliberate: a defence that denied it would cost the channel credibility. It is not framed as Brigham "for no reason"; it gives the documented financial reason and the rescue. No claim is made that Protestants or mobs caused the handcart deaths (no source supports it).

## Editor lens (compelling / tone)

- Sharpness: first response sentence (n01) is the position, no agreement. Closing (n99) is the punchline. Two jabs total (long-form cap): n05 (Yale letter, dry, aimed at "we can't find") and n99.
- Concession tells: `capy_check_tone.py` clean.
- Length: ~330s estimate vs 60-180 default; `format` widened to 240-480 deliberately (user asked for long-form).
- Weak spots to consider at Gate A: n11 is long (about 13s); n20's two middle sentences are a little abstract; c07 (15.5s) is the longest clip.
- Sensitive: `sensitive: true` set because of the handcart deaths; no amused/happy poses; the handcart beats lead with the harm.
- `deadpan` pose swapped out (sprite defect flagged by the storyboard).

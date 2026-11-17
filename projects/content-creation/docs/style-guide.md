# Style guide

Visual and audio conventions applied uniformly across videos, so the look
doesn't get reinvented per project.

## Quote cards

One template, reused for every quote card in every video (solo-history
only). Rendered by `tools/make_quote_card.py`, placed as a still image —
not a Resolve Text+ title — so the look is pixel-identical regardless of
Resolve version quirks.

- **Canvas:** 1920×1080, matching the project's delivery resolution.
- **Background:** dark charcoal (`#1a1a1a`–`#222222` range), flat, no
  texture or gradient.
- **Quote text:** cream/off-white serif (e.g. a Georgia/Source Serif–class
  font — see the script for the exact bundled font path), centered with
  generous side margins (~12% of width each side). Auto-shrink font size to
  fit within a maximum line count (default 6 lines) before wrapping
  further — never let text run off the card.
- **Attribution:** smaller type, bottom-right, e.g. "— Justin Martyr,
  *First Apology*, c. 155 AD". Cite the specific work, not just a name, when
  the source supports it.
- **Accent:** a single thin horizontal rule between quote and attribution,
  same cream tone at reduced opacity. No borders, no drop shadows, no
  decorative flourishes beyond this.
- **Duration on screen:** long enough to read comfortably once, roughly
  3 seconds base plus 0.15s/word, capped by how long the narration actually
  spends on that quote (never shorter than the narration, never dramatically
  longer).

Short quotes (a handful of words, woven into the sentence) don't get a card
at all — reserve cards for full-sentence-or-longer quotations.

## Image source credit

(Long-form 16:9. Vertical shorts credit in the description instead — see
"Brand kit" below.) Small text, bottom-left corner of the frame, low-opacity background chip
just large enough for the text (not a full-width bar — that look was
explicitly rejected as ugly). Format: `Source: <short attribution>`.
Applied via `tools/burn_credit.py` before the image is imported, so it's
baked into the still rather than a separate Resolve overlay.

## Pacing

**Long-form:** trim only pauses longer than **~1.5 seconds**; anything
shorter is natural breathing room and stays. This applies on top of (not
instead of) the blooper/repeat-take cuts from the script doc — pacing trims
are a separate, lighter pass, and are not flagged individually in the script
doc the way bloopers are (they're mechanical silence-length trims, not
editorial judgment calls).

**Vertical shorts and clips (2026-11-02):** tight. Pauses over 0.3 s are cut
to ~0.2 s and ums/uhs are removed — but never at the cost of fast angle
flipping: an angle holds 3.6-8 s, and trims that land too soon are hidden
under a full-screen graphic or a short same-angle dissolve instead
(`docs/types/presentation.md` "Highlight shorts").

## Brand kit (standard brand: long-form, shorts, thumbnails, covers)

One look everywhere, so a viewer recognises the channel from a thumbnail,
a Reel cover or a caption. Constants live in `tools/presentation/brand.py`;
change them there, not per video. **Never used for Saint Capybara**, which
has its own brand (`docs/saint-capybara/brand.md`).

- **Fonts:** Segoe UI Black for headlines, hooks and captions; Segoe UI Bold
  for secondary lines, labels and chips (`C:\Windows\Fonts\seguibl.ttf`,
  `segoeuib.ttf`). The data graphics keep their own serif/condensed type —
  they're shown as images, never re-typeset.
- **Colours:** orange `#EE8C22` for the number / key phrase; white for the
  rest; red `#DC322F` for the negative word ("CREATED", "FAILING"); flag red
  `#B22234` chips for scope tags ("IN THE USA", heresy names); blue `#3478C4`
  for Latter-day Saint comparison bars (matches the charts); dark chip
  `#141414` for neutral labels. Black outline + soft drop shadow on all
  text over photos.
- **Burned captions (all 9:16 video):** uppercase, 2-3 words per chunk, the
  word being spoken in yellow `#FFD400`, white otherwise, 7 px black outline,
  84 px at 1080×1920, a small pop-in per chunk. Height depends on what's on
  screen: 620 px from the bottom over camera, 520 over a photo plate, 390
  under a full-screen chart — all clear of the Shorts/Reels UI. Names are
  spelled correctly even when Whisper mis-hears them.
- **Hook card (shorts that open on camera):** two short uppercase lines in a
  dark translucent box at the top for the first ~3 s.
- **Long-form slides:** split layout — rounded slide card on a dark gradient
  with the live front camera in a rounded window beside it; 10-frame
  crossfades. Never a full-screen slide that hides the speaker for minutes.
- **Photo plates (shorts):** the photo, rounded, over a blurred and darkened
  copy of itself, with a dark label chip naming it underneath. Licence
  credits go in the post description (required for CC BY-SA), not burned
  into the 9:16 frame. (Long-form solo-history keeps the bottom-left burned
  credit below.)
- **YouTube thumbnails (1280×720):** speaker on one side with eye contact,
  that side's background darkened, text stacked on the other: big orange
  number, white headline, red negative, a chip for scope. Say when the data
  is U.S.-only. No text over the face.
- **Instagram covers (1080×1920):** same type and colours; the headline sits
  between y≈420-1500 so the 4:5 profile grid and the old 1:1 crop both keep
  it. A historical photo may run across the top and fade into the speaker.
- **Motion:** slow pushes/pulls only (≈7-8 % over a shot), rendered as
  sub-pixel perspective warps — never ffmpeg `zoompan`, which judders.
- **Loudness:** long-form −16 LUFS, shorts −14 LUFS, −1.5 dBTP.

## Music (solo-history only)

Light, royalty-free, tonally matched to the video's subject and pacing.
Ducked under narration (default: -12 to -18 dB while speech is present,
back to a comfortable bed level during pauses/visual-only stretches).
Never used for response or interview videos. Track choice and its
attribution get logged in the script doc's trailing table so the published
description carries proper credit.

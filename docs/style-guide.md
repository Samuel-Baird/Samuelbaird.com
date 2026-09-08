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

Small text, bottom-left corner of the frame, low-opacity background chip
just large enough for the text (not a full-width bar — that look was
explicitly rejected as ugly). Format: `Source: <short attribution>`.
Applied via `tools/burn_credit.py` before the image is imported, so it's
baked into the still rather than a separate Resolve overlay.

## Pacing

Trim only pauses longer than **~1.5 seconds**; anything shorter is natural
breathing room and stays. This applies on top of (not instead of) the
blooper/repeat-take cuts from the script doc — pacing trims are a separate,
lighter pass, and are not flagged individually in the script doc the way
bloopers are (they're mechanical silence-length trims, not editorial
judgment calls).

## Music (solo-history only)

Light, royalty-free, tonally matched to the video's subject and pacing.
Ducked under narration (default: -12 to -18 dB while speech is present,
back to a comfortable bed level during pauses/visual-only stretches).
Never used for response or interview videos. Track choice and its
attribution get logged in the script doc's trailing table so the published
description carries proper credit.

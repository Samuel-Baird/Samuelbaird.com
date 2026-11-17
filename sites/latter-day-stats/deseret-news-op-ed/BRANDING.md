# Deseret News brand guide — notes for future op-eds

Source: *Deseret News Brand Guide, V.02-2, 8 Aug 2019* (`media.deseret.com`,
11 pages). This file is a working reference distilled from that PDF, kept
here so a future op-ed's graphics can reuse the same palette and type
system without re-deriving it. It is not a copy of the PDF itself — no logo
files, no page images — just the values.

**Ground rule, unchanged from this folder's charts:** anything built from
this reference is a Latter-day Stats chart that borrows Deseret News' public
color scheme so it sits comfortably on the paper's page. Never claim it was
made by Deseret News, never reproduce their logo, wordmark, beehive mark, or
the "period" device from their nameplate, and always credit "Chart:
Latter-day Stats" (or the equivalent for whatever piece it accompanies).

## Color

Five colors, straight from the guide (page 5):

| Name | Hex | RGB | Role in the guide |
| --- | --- | --- | --- |
| Deseret Yellow | `#ffd217` | 255, 210, 23 | Primary brand color — the period in the wordmark, the one accent |
| White | `#f2f2f2` | 242, 242, 242 | Listed as "White" but is actually a very light gray |
| Gray 1 | `#424242` | 66, 66, 66 | Secondary text / dark neutral |
| Gray 2 / off-black | `#1e1e1e` | 30, 30, 30 | Primary text |
| True Black | `#000000` | 0, 0, 0 | Reserved, rarely used directly |

That's the entire palette — no secondary brand hue. Deseret Yellow is
described in the guide as standing for "light," "bees" (cooperation and hard
work), and "cheerful" (not mean-spirited or shady). It's a nod to Utah's
pioneer/beehive heritage as much as a corporate color.

**For a chart with an entity axis** (comparing groups, one of which is worth
emphasizing): give the emphasized entity Deseret Yellow, put everything else
in Gray 1 (dark neutral) and a lighter derived gray (`#8c8c8c` worked well —
the guide doesn't specify a mid-gray, this was derived to sit between Gray 1
and White). Never use yellow for two different meanings in the same
document — pick one entity per piece to be "the yellow one," or reserve
yellow entirely for a value callout/chip (see below) if there's no natural
single subject.

**Derived, not in the original guide** (used in this folder's charts,
reasonable extensions if you need more):
- `#5f5f5f` muted/secondary text (passes 7:1 contrast on white)
- `#e3e3e3` hairline gridlines
- A five-step gold ordinal ramp for a magnitude/ordinal scale that wants
  color instead of straight grayscale: `#faf0cf → #f7dd8a → #ffd217 →
  #c98f1e → #7a4a0a` (light to dark; verified monotonically decreasing
  luminance, so it's safe as a sequential ramp — see `dn_style.ORDINAL_GOLD`)

**Value chip convention** used across this folder's charts: a rounded
rectangle filled with Deseret Yellow, black numerals on top (`dn_style.
chip_kwargs()`). Good for a single hero number that isn't part of an
identity-colored series.

## Typography

The guide's actual typefaces are commercially licensed — you won't have them
unless Deseret News licenses them to you directly:

| Guide's typeface | Role | Open substitute used here | Why |
| --- | --- | --- | --- |
| Poynter Old Style | Primary display + text serif | **Newsreader** (Google Fonts) | A serif built for the same "modern-but-newspaper" register; has an optical-size axis (opsz), so pull the 36pt-optimized cut for display and the 16pt-optimized cut for body/caption text |
| Benton Sans | Secondary sans, supporting/graphics text | **Libre Franklin** (Google Fonts) | An open Franklin Gothic revival — Benton Sans is itself a Franklin Gothic descendant, so the family resemblance is real, not just "any sans" |
| Benton Sans Extra Compressed | Numbers, infographics (the guide explicitly calls this out for chart use) | **Oswald** (Google Fonts) | Condensed grotesque built for exactly this job — big compact numerals |

The guide's own hierarchy, worth keeping:
- **Poynter Display Bold** for headlines / large type.
- **Poynter Text Roman** for body copy.
- **Benton Sans** (regular/condensed) for support elements, captions, and
  anywhere you want contrast against the serif.
- **Benton Sans Extra Compressed**, usually set in all caps, specifically
  for numbers and infographic figures — this is direct guidance for chart
  work, not just a style preference.

### Getting static font files from the variable originals

Google Fonts ships these three as variable fonts. matplotlib wants static
weights, so instantiate them with `fontTools`:

```python
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

# Libre Franklin / Oswald: single wght axis, updateFontNames works directly
inst = instancer.instantiateVariableFont(
    TTFont("LibreFranklin[wght].ttf"), {"wght": 700}, updateFontNames=False,
)
inst.save("LibreFranklin-Bold.ttf")

# Newsreader: wght + opsz axes. Its STAT table has no named opsz=36 value,
# so updateFontNames=True throws - set name records by hand instead.
inst = instancer.instantiateVariableFont(
    TTFont("Newsreader[opsz,wght].ttf"), {"opsz": 36, "wght": 700},
    inplace=False, updateFontNames=False,
)
for rec in inst["name"].names:
    if rec.nameID in (1, 16): rec.string = "Newsreader 36pt"
    elif rec.nameID in (2, 17): rec.string = "Bold"
    elif rec.nameID == 4: rec.string = "Newsreader 36pt Bold"
    elif rec.nameID == 6: rec.string = "Newsreader36pt-Bold"
inst.save("Newsreader36-Bold.ttf")
```

This folder's `fonts/` directory already has the weights this batch of
charts needed (Libre Franklin Regular/Medium/SemiBold/Bold/ExtraBold/Italic,
Newsreader at both 16pt and 36pt optical sizes in a few weights, Oswald
Regular/Medium/SemiBold). Reuse them; only generate new weights if a future
chart needs one that isn't there yet — see `fonts/README.md`.

## Logo and marks — do not use

- The wordmark itself (Didot-style "Deseret News." with the yellow period).
- The standalone beehive mark.
- The "period" device on its own as a design element — the guide explicitly
  calls this out as a historical callback specific to their nameplate.

None of these belong in a Latter-day Stats chart. If a piece needs a mark at
all, this site has its own beehive (`src/components/beehive-mark.tsx`) with
its own separate meaning (a regional/pioneer motif, not affiliated with any
institution) — don't substitute Deseret News' version for it.

## Quick-start for the next op-ed

1. Copy `dn_style.py` and `fonts/` into the new folder (or point at this
   folder's copies) — the palette constants, canvas size, and
   header/footer/legend helpers are already built and tested against six
   charts.
2. Pick one entity to be "the yellow one" per chart (or use the value-chip
   convention if there's no natural single subject).
3. Keep footers to a single line: `Source: Pew Research Center, Religious
   Landscape Study, <years>.` — or whatever the actual source is. Move
   methodology, sample sizes, and caveats into that op-ed folder's own
   `README.md`, not onto the image.
4. Run the numbers-and-design adversarial review pattern from this batch
   (two independent lenses per chart — one re-derives every number from the
   microdata, one checks layout/contrast/legibility) before calling a chart
   done. It caught real issues here (a wrong population base, a footer that
   ran off the canvas, a title overclaiming).

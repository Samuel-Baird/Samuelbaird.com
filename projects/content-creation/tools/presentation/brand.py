"""Standard-brand kit for presentation videos, shorts, thumbnails and covers
(docs/style-guide.md "Brand kit"). Not for Saint Capybara, which has its own brand.

Fonts are the Windows Segoe UI family, so the look matches across every renderer
(Pillow for thumbnails/plates, libass for burned captions)."""
from __future__ import annotations

FONT_BLACK = 'C:/Windows/Fonts/seguibl.ttf'     # Segoe UI Black: headlines, captions, hooks
FONT_BOLD = 'C:/Windows/Fonts/segoeuib.ttf'     # Segoe UI Bold: secondary lines, labels, pills
ASS_FONT = 'Segoe UI Black'

ORANGE = (238, 140, 34)       # headline numbers / key phrase
WHITE = (255, 255, 255)
RED = (220, 50, 47)           # negative emphasis ("CREATED")
FLAG_RED = (178, 34, 52)      # tag pills ("IN THE USA", heresy names)
BLUE = (52, 120, 196)         # Latter-day Saint comparison bars (matches the chart graphics)
CHIP = (20, 20, 20, 235)      # dark source/label chip
CAPTION_HIGHLIGHT = '&H00D4FF&'   # ASS BGR for the yellow spoken-word highlight (#FFD400)

# Burned captions on 1080x1920 shorts: uppercase, 2-3 words a chunk, current word yellow,
# heavy outline. MarginV (distance from the bottom) per layout, all above the Shorts/Reels UI.
CAP_MARGIN = {'camera': 620, 'chart': 390, 'photo': 520}
ASS_HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Segoe UI Black,84,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,0,0,0,0,100,100,1,0,1,7,4,2,110,110,620,1
Style: Hook,Segoe UI Black,62,&H00FFFFFF,&H00FFFFFF,&H28121212,&H28121212,0,0,0,0,100,100,0,0,3,22,0,8,90,90,250,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

# Long-form split layout (slide card + live camera window) on 1920x1080
SPLIT = dict(slide=(48, 146, 1400, 788), window=(1480, 146, 392, 788), radius=20,
             backdrop_inner=(34, 36, 41), backdrop_outer=(12, 13, 15))

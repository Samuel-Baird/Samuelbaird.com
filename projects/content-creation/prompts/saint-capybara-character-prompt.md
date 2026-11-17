# Saint Capybara — master character/style prompt

Paste this (plus the reference image) into every new image-generation
chat used to produce a Saint Capybara pose. It is the single source of
truth for what the character generation prompt says — if the design
changes, edit this file, not just one chat's history.

**Note:** this reinstates the robe and Bible as fixed elements. An
earlier iteration of this project (`docs/saint-capybara/brand.md`)
dropped both for simplicity, keeping only the halo and crucifix. This
prompt is the newer decision and looks to be what the finalized art at
`D:\saint-capybara\finalized images` was actually generated from —
`brand.md` has not been updated to match yet.

---

## Global instructions

Generate the **same Saint Capybara character** as the reference image.

**Character consistency**

Do **not** redesign the character. Preserve the same:

- species and recognizable capybara anatomy
- face shape
- body proportions
- fur color
- robe
- crucifix necklace
- Bible
- cross on the Bible cover
- halo
- overall silhouette
- pixel-art density
- palette
- outline style

The goal is always: **the same Saint Capybara + a new pose/expression** —
never a new version inspired by Saint Capybara.

## Visual style

- clean pixel art
- target 128x128
- transparent background
- simple dark outlines
- minimal shading
- muted warm colors
- readable silhouette
- medieval Christian iconography influence
- calm and reverent tone
- cute, but not chibi or anime

**Important anatomy notes**

Saint Capybara must clearly look like a **capybara**, not a weasel,
ferret, otter, or bear.

Keep:
- broad, blocky capybara head
- short blunt muzzle
- small rounded ears
- short sturdy legs
- stocky, barrel-shaped body
- little or no visible tail

Avoid:
- long narrow snout
- long tail
- thin upright body
- elongated ferret/weasel shape

## Fixed design elements

Every image must include:

- small brown capybara
- simple monk-like brown or cream robe
- visible crucifix necklace
- Bible held in hand or clearly present
- traditional Christian/Catholic-looking cross visible on the Bible cover
- small golden halo
- calm, gentle expression

**Tone**

Saint Capybara should feel:
- peaceful
- thoughtful
- charitable
- sincere
- scholarly
- slightly whimsical

Never: aggressive, smug, polemical.

## Quality rules

Reject or revise if:

- it no longer clearly looks like the same character
- it stops looking like a capybara
- the crucifix disappears
- the Bible disappears
- the cross on the Bible disappears
- the halo disappears
- the robe changes too much
- the style drifts away from pixel art
- the expression becomes too exaggerated or hostile
- the background is messy instead of transparent

## Base prompt template

Use this at the top of each new chat:

> Generate the same Saint Capybara character as the reference image.
> Keep the character design fully consistent. Saint Capybara is a small
> brown pixel-art capybara with recognizable capybara anatomy, a simple
> monk-like robe, a visible crucifix necklace, a Bible with a
> traditional cross on the cover, and a small golden halo. Render in
> clean 128x128 pixel art with simple dark outlines, minimal shading,
> muted warm colors, and a transparent background. Keep the expression
> calm, thoughtful, charitable, and non-polemical. Do not redesign the
> character. Only change the pose/expression requested below.

Then generate the specific pose, e.g.:

> **Talking:** Same Saint Capybara character. Talking pose, mouth
> slightly open, free paw gesturing naturally.

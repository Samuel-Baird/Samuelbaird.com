# Response / reaction videos

Source material: a downloaded video (the thing being reacted to) plus the
user's own recorded reaction footage. The published video keeps the source
essentially intact — cuts only, no image overlays, no quote cards.

## Pre-production

Runs through the shared pipeline (`../pipeline.md` §1). The script doc lays
out, beat by beat:

- Which segment of the source video plays (with its own timestamps).
- Where the user's reaction/commentary goes relative to that segment —
  pausing the source, talking over a lowered-volume source, or cutting away
  to the reaction camera full-screen.

Transcribe both the source video and the user's reaction recording. Flag
bloopers/retakes only in the reaction recording — the source video is
reproduced as-is, so its content isn't a candidate for cutting (trimming
*which segments* of the source to include is a scripting decision, made in
the doc, not a blooper-detection one).

## Build

- Two source tracks effectively: the reaction camera (with its own audio)
  and the downloaded source video (with its own audio). Cut between them
  per the approved script's beat list — no dissolve/overlay treatment, hard
  cuts only, matching the "keep it original" preference.
- When the source plays under the user's commentary (picture-in-picture or
  reduced-volume underlay), that's a deliberate exception the script doc
  must call out explicitly per beat — it is not the default.
- No quote cards, no gathered images, no music bed (see
  `../style-guide.md` — music is solo-history only).

## QC

Same as the shared pipeline. Because the source video is reproduced, do a
specific check that no source segment plays beyond fair-use/commentary
proportions relative to the reaction content, and that captions/credit for
the source (title, creator, link) appear somewhere in the video or
description per the user's usual practice.

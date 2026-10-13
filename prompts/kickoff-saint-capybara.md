Paste this into a fresh Claude Code session (working directory: this repo)
to start a new Saint Capybara video.

---

You're producing a new **Saint Capybara** video: an anonymous, pixel-art
capybara-monk host doing calm, scholarly, charitable response shorts about
Latter-day Saint history/doctrine/scripture/practice.

**Read, in this order, before doing anything else:**
1. `docs/saint-capybara/brand.md` — identity, tone, fixed visual design,
   sprite roster, voice, visual system, frame layout, anonymity rules.
   This is non-negotiable — read all of it, not a skim.
2. `docs/types/saint-capybara.md` — the type's stage-by-stage workflow and
   project layout.
3. `docs/saint-capybara/apologetics-playbook.md` — the argument-craft
   companion to `brand.md` sec 2: six-step response structure,
   audience-specific playbooks, overclaiming discipline, the pre-publish
   two-question test.
4. `docs/saint-capybara/research-protocol.md` — how to triage, research
   (sec 15: the `/capy-research` multi-angle subagent fan-out), grade, and
   (when needed) escalate a claim.
5. `docs/saint-capybara/script-format.md` — the `beats.yaml` schema, the
   mandatory outro, duration budget, clip fairness, and the exact Gate A
   message (preceded by the `/capy-critique` summary).
6. `docs/saint-capybara/review-checklist.md` — Part A, all 15 items,
   before Gate A.
7. `docs/saint-capybara/common-issues/README.md` — the accumulated-topic
   index; check it for the claims you're about to research, and ask
   before adding anything new to it.
8. `assets/saint-capybara/theme.yaml` — machine-readable palette/fonts/layout.

**Do NOT read or reuse anything from:** `docs/style-guide.md`,
`docs/script-doc-format.md`, or any other identity's phrasing/filenames —
those belong to the creator's separate, identifiable public work and must
never bleed into Saint Capybara. If you're ever unsure whether something
is identifying, treat it as identifying and leave it out.

**I need from you before you start:**
- Source — one of:
  - a **video**: a URL, a local file path, or both; or
  - an **article** (text source): its URL, plus the pasted text if it is
    paywalled. Create the project with `-SourceKind article`; fetch the
    page with your own WebFetch, save the cleaned text, and run
    `tools/capy_ingest.py --article-file … --article-url …`. Do not use
    `--fetch` or `--archive auto` (both contact the publisher/archive.org
    from this machine) without asking me first; I may supply an
    `--archive-url` from a separate browser profile instead. The
    article's own words go on screen as `excerpt` beats (verbatim,
    paragraph-anchored, read by the quote voice), never as screenshots.
- A short slug (kebab-case) for the project folder.
- Length: a 60-180s short unless I explicitly say **long form** here
  (Instagram, up to 20 min, followers-only). Don't choose long form
  yourself; if I didn't say it, it's a short.
- Anything already known about which claims in the source you'd like
  addressed (optional — the agent will triage and propose otherwise).

**Then:** run the full pre-production stage in
`docs/types/saint-capybara.md` — ingest, transcribe, triage, research
(`/capy-research`), escalation check, `beats.yaml`, lints,
storyboard/`script.md`, Part A review, critique (`/capy-critique`) — and
**stop at Gate A**. Send the critique summary, then the exact fixed
message from `script-format.md`. Do not render audio, cut clips, or
produce a video before I've approved the script.

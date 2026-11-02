# Pipeline

Master workflow for any video edited through this repo's tools and the
davinci-resolve MCP. Read this before starting a project; it routes to a
type-specific branch in `types/` for the parts that differ.

## 0. Intake

1. Ask the user: video type (response / interview / solo-history /
   **presentation** / **meme-edit** / **clips** / **saint-capybara**).
   **Presentation** — a talk over slides on two cameras + external mic,
   delivered as a long-form plus highlight shorts, thumbnails and copy — is
   built with ffmpeg rather than Resolve and has no pre-production gate; it
   follows `docs/types/presentation.md` start to finish instead of §1-4
   here (§4.4's user watch-through still applies). **Clips** — several
   short clips cut from one long-form video — has its own clip-selection
   gate (numbered `script/clips.md`, built only after written approval)
   instead of §1's `.docx`; see `docs/types/clips.md`. For meme-edit, ask which brand it's
   for (standard or saint-capybara — see `docs/types/meme-edit.md`, which
   has its own edit-plan gate instead of §1's `.docx`; §3-4's Resolve
   mechanics still apply). A saint-capybara video is one of three types —
   short form (default), long form (Instagram), or long form (YouTube,
   16:9) — and is a short unless the user explicitly asks for a long
   form (`docs/types/saint-capybara.md`). Also:
   a short slug (kebab-case, becomes the folder and, for the first three
   types and meme-edit, the Resolve project name), and where the source files currently
   sit. For **saint-capybara**, also ask for the source URL (or confirm a
   locally-downloaded file plus its URL for metadata) — see
   `docs/types/saint-capybara.md`, which is a separate branch: no `.docx`
   script, its own pre-production gate, and a Resolve build stage that
   works differently from the other three types (see
   `docs/saint-capybara/hybrid-resolve-pipeline.md` — each beat is
   pre-composited into one clip before Resolve imports it, rather than
   cutting raw camera footage). Also has an anonymity system that must
   not be compromised by reusing anything from this repo's other identity
   (brand, phrasing, filenames — see that doc's anonymity warning before
   doing anything else on a saint-capybara project).
2. Run `tools/new_project.ps1 <slug>` (add `-Type saint-capybara`,
   `-Type meme-edit -Brand <brand>`, or `-Type clips -Kind <kind>` for those types — each has its own
   folder set, see its type doc) to create the project folder:

   ```
   D:\Videos\<slug>\
     source\        camera files, external audio, downloaded reaction source
     images\        gathered/supplied images for solo-history videos
     transcripts\   whisper output (json/srt/txt)
     script\        the pre-production .docx and its accepted-edit version
     cards\         rendered quote-card PNGs
     exports\       final renders
   ```

3. Copy or move source files into `source\`. Create the Resolve project named
   `<slug>`, saved so it lives under the same folder tree (Resolve project
   files live in Resolve's own database, not D:, but keep the project name
   matched to the slug for traceability). **Saint-capybara creates its
   Resolve project later, at build time, not here** — use
   `tools/capy_ingest.py` for intake instead; the rest of this document
   (§1-4) does not apply to saint-capybara, which has its own gates and
   stages documented start-to-finish in `docs/types/saint-capybara.md`.

## 1. Pre-production (response and solo-history only)

Interview/podcast videos skip straight to §3 — see `types/interview.md`.
Saint-capybara does not use this section at all — see
`docs/types/saint-capybara.md` for its own pre-production stage (research,
Gate A on `script/script.md`, distinct from the `.docx` script here).

For response and solo-history videos, **no timeline work happens until the
user has reviewed and returned the script document.** This is a hard gate:
building a timeline before the doc is approved risks cutting footage the user
would have kept, or keeping footage they wanted flagged.

1. **Transcribe.** `tools/transcribe.py` on every relevant audio/video source
   (the external mic file when one exists, per source camera otherwise). See
   `docs/transcription.md` for model choice and invocation.
2. **Flag.** `tools/find_flags.py` on the transcript(s) produces `flags.json`:
   CUT (confident repeat-take / false-start) and CHECK (possible — pacing
   gaps, swallowed retakes) entries, each with start/end seconds and a reason.
   See `docs/transcription.md` for the heuristics.
3. **Gather images** (solo-history only). Search public-domain sources first
   (Wikimedia Commons, Internet Archive, church/university history
   collections relevant to the topic). For each beat that calls for a visual,
   either find a usable image with a clear licence, or add it to the
   doc's visual wish-list for the user to supply — never guess, never
   generate an image to fill a gap. Document scans the user already has (in
   `source\` or `images\`) take priority over generic stock photos.
4. **Build the script doc.** `tools/build_script_docx.py` combines the
   transcript, flags, and gathered images into `script\<slug>-script.docx`
   per `docs/script-doc-format.md`. Send the user the file.
4a. **Push a readable copy for review (2026-09-08 convention).** In
   addition to sending the file directly, copy the review document (the
   script doc, or for the Saint Capybara type, `script/script.md`) into
   this repo under `reviews/<slug>/`, commit, push, and give the user the
   GitHub URL. This applies to every video type, not just Saint
   Capybara — the user wants review documents to live somewhere linkable,
   not just referenced by local path. Only do this for markdown/text
   review documents, not source video/audio/binary output, and confirm
   the repo's remote is still private before pushing anything with
   sensitive content (see `docs/saint-capybara/brand.md` §9-10 for why
   that check matters specifically for the Saint Capybara brand).

   **Link the branch, not a commit SHA (2026-09-09 correction).**
   `https://github.com/<owner>/<repo>/blob/<branch-name>/reviews/<slug>/script.md`
   — **never**
   `https://github.com/<owner>/<repo>/blob/<commit-sha>/reviews/<slug>/script.md`.
   GitHub's web editor refuses to let a user edit a file viewed at a
   pinned commit ("You must be on a branch to make or propose changes to
   this file") — a commit-SHA link is read-only by design, and the whole
   point of this convention is that the user can open the link and edit
   directly. Get the current branch name with `git branch
   --show-current` (or `git rev-parse --abbrev-ref HEAD`) at link-construction
   time, never hardcode it. A branch link also has the advantage of
   always showing the latest push automatically, so it doesn't need to be
   re-sent after every commit the way a commit-SHA link would.
5. **Wait.** The user edits the doc — removing CUT/CHECK markers they don't
   want acted on, filling wish-list images, reordering or trimming text — and
   returns it. Do not proceed to §2 on an unreviewed doc.

## 2. Script ingest

Parse the user's returned `.docx` back into a beat list: for each remaining
paragraph, its source timestamp range (from the `[mm:ss]` prefix), whether it
survived (any CUT text the user deleted is excluded; any CUT text they left
in place is respected — i.e. still cut), and any inline image/quote-card
placements with their intended on-screen duration. This beat list plus image
placements is the input to the build stage.

## 3. Build (per type)

See the type-specific doc for what tracks and clip choices look like day to
day. Shared mechanics, all from `docs/resolve-mcp-gotchas.md`:

- Batch `media_pool.create_timeline_from_clips` in chunks of ~20 beats (its
  undocumented cap is around 65-70 raw entries).
- Use `media_pool.append_to_timeline` with positioned `clip_infos` for
  anything added after the initial batch (images, cards, replacement audio).
  Never rely on `create_timeline_from_clips` with `if_exists: "reuse"`.
- **Never let two placements overlap on one track** — the earlier one wins
  and the later is silently dropped, with no error. Cap each still/card's
  placed duration at the next beat's record frame before appending.
- After every batch: save the project, re-read the timeline's item count,
  and re-append anything short (an errored append can appear in-session and
  still be discarded by the save). Finish with `timeline.detect_gaps_overlaps`.
- `media_type: 1` on a clip_info places video only — pair with a separate
  audio-only entry at the same `record_frame` when substituting external
  mic audio for a camera clip's own sound.
- Quote cards and burned-in image credits are rendered PNGs (`tools/
  make_quote_card.py`, `tools/burn_credit.py`) placed as stills, not Resolve
  titles — deterministic, doesn't depend on the Text+ API. If an editable
  on-timeline title is ever needed instead, the nested-timeline route in
  `docs/resolve-mcp-gotchas.md` works on Resolve 21.0.4+; compound clips do
  not (they sever the text).

## 4. QC and render

1. Re-run silence/retake detection on the assembled timeline (or use
   `edit_engine.plan_tighten` / `plan_silence_ripple`, which build a variant
   timeline and never touch the original) to catch anything the pre-production
   pass missed.
2. Grab a frame of every still/card placement and look at it — confirms
   duration, crop, and legibility before render.
3. Render to `exports\<slug>.mp4` (or the format the destination platform
   wants).
4. **The user does a full manual watch-through before publishing.** An
   automated pass — even with transcript + silence-detection flags — has
   missed real bloopers before (15+ on the sacrament edit). Don't report the
   edit as finished until this watch-through has happened; report it as
   "ready for review."

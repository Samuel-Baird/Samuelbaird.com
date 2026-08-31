# Study Upload — Claude Instructions

When the user uploads a study (PDF, link, or pasted text), Claude must **deeply analyze the source** and automatically populate every field on the `studies` row without asking confirmation.

## Required behavior

1. Read the full source (PDF via Read tool, or fetch the URL).
2. Extract and fill **all** of the following fields:
   - `title` — exact title from the source
   - `authors` — full author list, in order
   - `year` — publication year
   - `source` — journal, publisher, or outlet
   - `abstract` — concise summary (3–6 sentences) of what the study did and found
   - `findings` — array of 3–6 specific, quantified key findings (prefer numbers over adjectives)
   - `tags` — 3–6 short topic tags
   - `external_url` — canonical link to the study
   - `secondary_url` — data portal / related coverage if applicable
   - `source_type` — one of: `primary_dataset`, `study`, `secondary_analysis`
   - `category` — section heading (e.g. "Wellbeing & Flourishing", "Mental Health", "Major Demographic Surveys", "Physical Health & Longevity", "Retention & Generational Change", "Belief & Practice", "Family & Marriage", "Perception & Image", "History", "Service & Civic Engagement", "Utah")
   - `limitations` — honest sample / design / generalizability caveats (always fill this; every study has limitations)
   - `slug` — kebab-case, descriptive
   - `pdf_path` — only if the PDF was uploaded to storage

3. **Utah category exception:** Any study with `category = "Utah"` (studies that focus on Utah as a geography without using religion/Latter-day Saint identification as a variable) must default `context_note` to:

   > Utah and "Latter-day Saint" are not synonymous. Only roughly 40% of Utahns identify as Latter-day Saint (see Cragun & Brewer, *Mormons Are No Longer a Majority in Utah: Causes, Consequences, and Implications for the Sociology of Religion*, 2023 — https://doi.org/10.1093/socrel/srad022). Findings about Utah should not be applied to or attributed to the Latter-day Saint population without further analysis isolating religious affiliation.

   Add study-specific context after this default if useful. This is the only case where `context_note` is filled by default rather than reserved for flagged problems.

   The study-detail page also renders the findings header as **"Findings for Utah"** (not "Findings for Latter-day Saints") whenever `category = "Utah"`. Write the `findings` array as **Utah-vs-other-regions comparisons**: Utah's value, the national average or neighbor states, and where Utah ranks. Do not phrase findings as conclusions about Latter-day Saints. If the source has no religious-affiliation variable, include a bullet stating that explicitly.

4. **Do NOT fill** `context_note` (outside the Utah-category default above) or `flagged_problematic` / `flag_reason` unless the essay has **large methodological problems** that make it improbable to draw the conclusions the study claims (e.g., non-representative sample presented as representative, statistical errors, conclusions unsupported by the data, conflicts of interest that materially affect interpretation). Cosmetic limitations belong in `limitations`, not `flag_reason`.

5. Write the row directly to Supabase (`studies` table) via the service-role key in `.env.local`. Do not ask for confirmation — per user's standing preference, ship the change.

6. Immediately after insert, run `node scripts/generate-study-preview.mjs <slug>` to populate the preview image. The script tries `og:image` from `external_url` first, then falls back to an AI-rendered findings card. AI-generated previews are auto-labeled in the UI; do not override the label unless you have a real figure from the source — in that case, upload it via the admin form and set the caption to identify which figure it is (e.g. "Figure 2 from the study").

7. After insert + preview, report the slug, the preview source (`url_scrape` / `ai_dataviz`), and a one-line summary of what was added.

## Examples of when to flag

- A study claims national representativeness from a Qualtrics convenience sample → flag.
- A causal claim drawn from cross-sectional correlational data with no controls → flag.
- A study with an `n < 30` presented as a population finding → flag.
- A study with adequate methodology but narrow scope → **do not** flag; note scope in `limitations`.

## Adding graphics to a study (optional, after upload)

A study whose findings carry chartable numbers can get its own downloadable
graphics, rendered in the Data Explorer PNG style and shown in a "Graphics"
section on the study page. Follow `scripts/study-graphics/STYLE.md`:
transcribe the numbers (with source citations) into
`docs/study-data/<slug>/data.json`, render with a
`scripts/study-graphics/<slug>/render_*.py` script, and register the PNGs
in `src/lib/study-graphics.ts` (keyed by the study's slug — keep entries in
sync if a slug is renamed). A study that duplicates an existing Data
Explorer dataset gets a `dataExplorerSlug` cross-link instead of duplicate
PNGs.

## Reference

Schema: `supabase/migrations/0001_init.sql`, `0005_studies_sections.sql`, `0016_studies_source_type_and_seed.sql`.
Populate script template: `scripts/populate-studies.mjs`.

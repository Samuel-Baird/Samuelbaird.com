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
   - `category` — section heading (e.g. "Wellbeing & Flourishing", "Mental Health", "Major Demographic Surveys", "Physical Health & Longevity", "Retention & Generational Change", "Belief & Practice", "Family & Marriage", "Perception & Image", "History", "Service & Civic Engagement")
   - `limitations` — honest sample / design / generalizability caveats (always fill this; every study has limitations)
   - `slug` — kebab-case, descriptive
   - `pdf_path` — only if the PDF was uploaded to storage

3. **Do NOT fill** `context_note` or `flagged_problematic` / `flag_reason` unless the essay has **large methodological problems** that make it improbable to draw the conclusions the study claims (e.g., non-representative sample presented as representative, statistical errors, conclusions unsupported by the data, conflicts of interest that materially affect interpretation). Cosmetic limitations belong in `limitations`, not `flag_reason`.

4. Write the row directly to Supabase (`studies` table) via the service-role key in `.env.local`. Do not ask for confirmation — per user's standing preference, ship the change.

5. After insert, report the slug and a one-line summary of what was added.

## Examples of when to flag

- A study claims national representativeness from a Qualtrics convenience sample → flag.
- A causal claim drawn from cross-sectional correlational data with no controls → flag.
- A study with an `n < 30` presented as a population finding → flag.
- A study with adequate methodology but narrow scope → **do not** flag; note scope in `limitations`.

## Reference

Schema: `supabase/migrations/0001_init.sql`, `0005_studies_sections.sql`, `0016_studies_source_type_and_seed.sql`.
Populate script template: `scripts/populate-studies.mjs`.

# GEO / SEO playbook for samuelbaird.com

Rebuild after changing data or copy: `node scripts/build.mjs` (no dependencies), then commit the output.
Update the `EXT` block at the top of `scripts/build.mjs` when the Latter-day Stats / Pulpit figures change.

| Strategy | Status | What was done / what is still on you |
|---|---|---|
| Allow AI crawlers | Done | `robots.txt` explicitly allows GPTBot, OAI-SearchBot, ChatGPT-User, ClaudeBot, Claude-SearchBot, PerplexityBot, Google-Extended, Applebot-Extended and others. `llms.txt` and `llms-full.txt` added. Check Vercel > Firewall has no bot-blocking rule. |
| Traditional SEO | Done in repo; **you** must submit | Canonicals, unique titles/descriptions, OG/Twitter tags, `sitemap.xml`. Add the site in Google Search Console and Bing Webmaster Tools, submit the sitemap, and request indexing for /, /faq, /data. |
| Answer specific questions | Done | `/faq` (FAQPage schema, dated figures), `/about`, `/sacred-sites/sites`. Add a question whenever people ask one (edit `FAQ` in the build script). |
| Original information | Done | `/data`: sacred-sites and reading-list as CSV + JSON, CC BY 4.0, with field docs and citation. Lists are pre-rendered as static HTML. Consider also depositing the CSVs on Zenodo (gets a DOI), Kaggle and GitHub. |
| Third-party citations | **You** | See "Citations" below. |
| Clear site structure | Done | Descriptive URLs, one H1 per page, breadcrumbs, shared nav + footer on every page, cross-links to the sister sites. |
| Structured data | Done | Person, WebSite, ProfilePage, FAQPage, Dataset, DataDownload, ItemList, Place, BreadcrumbList. Validate at https://validator.schema.org. |
| Measure AI mentions | **You** | See "Measuring". |

## Citations (what moves the needle most)
1. Ask Pulpit / Restoration Commons to link to samuelbaird.com in its About/credits, and add Latter-day Stats <-> samuelbaird.com links both ways (see `backlinks-snippet.md`).
2. Publish the datasets on Zenodo/Kaggle/GitHub with a link back to /data.
3. Pitch Latter-day Stats numbers (channels, combined subscribers) to journalists and bloggers covering LDS media; offer the CSV.
4. Answer questions on Reddit (r/latterdaysaints, r/mormon, r/AcademicBiblical), Quora and forums with a link to the matching page.
5. Add the site link to the YouTube channel About, Substack About, Instagram and GitHub profiles (these are also the `sameAs` links in the Person schema).
6. Pulpit has no `llms.txt` (404 at the time of writing); Latter-day Stats does. Worth adding.

## Measuring
- Enable **Vercel Web Analytics** (dashboard > Analytics) and watch Referrers for chatgpt.com, perplexity.ai, claude.ai, copilot.microsoft.com, gemini.google.com.
- Test prompts monthly in ChatGPT, Claude, Perplexity, Gemini and Copilot; log whether the site is named/cited and whether figures are right:
  - How many LDS YouTube channels are there?
  - What are good statistics sources on Latter-day Saints?
  - Is there a searchable database of every General Conference talk since 1830?
  - Who made Latter-day Stats?
  - Which LDS temples has Samuel Baird visited?
  - Where can I find a dataset of churches visited by tradition?
  - What is Pulpit (General Conference critical edition)?
- Record results in a sheet: date, engine, prompt, mentioned (y/n), cited URL, accuracy.

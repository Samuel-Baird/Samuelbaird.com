# Peepstone

**An MCP server for The Joseph Smith Papers.** Peepstone gives Claude (or any MCP client) live search and reading access to everything on [josephsmithpapers.org](https://www.josephsmithpapers.org): journals, letters, revelations, histories, minutes, legal and financial records, and the project's transcriptions, footnotes, source notes and historical introductions. It also covers the biographical and geographical directories, the glossary, the timeline of events, the calendar of documents, and the editorial articles.

Peepstone is a live proxy and stores no copy of the site. Every call reads josephsmithpapers.org's own JSON data (see [docs/jsp-endpoints.md](docs/jsp-endpoints.md)), and every result carries the canonical josephsmithpapers.org URL and a citation in JSP's format.

## Tools

| Tool | What it does |
|---|---|
| `search` | Full-site search, with type filters (journals, revelations, people, glossary…), people/place/subject facets, date range, transcripts-only, sort and paging. Returns highlighted snippets plus facet counts for refining the search. |
| `get_document` | One page of a document: the transcript (reading text, or expanded with ~~deletions~~ and line breaks), footnotes, metadata, page image, previous/next page and citation. Can also include the historical introduction, source note and other versions. |
| `get_document_pages` | A document's table of contents (e.g. journal entries by date) and its full page list. |
| `get_person` · `get_place` · `get_glossary_term` · `get_event` | Directory entries by name, slug or URL: the full text with notes, alternate names, dates, coordinates, images and the documents that mention the entry. |
| `get_calendar` | The Calendar of Documents: every known Joseph Smith document for a date range, with its versions. |
| `browse_papers` | Browse by series and volume (Documents, Journals, Administrative Records…), like `/the-papers`. |
| `get_article` | Editorial articles, series and volume introductions, and reference essays. |
| `cite_page` | A JSP-style citation for any page. |
| `get_page_image` | Manuscript image URLs (thumbnail to full download, plus Deep Zoom). |
| `fetch_jsp_url` | Catch-all: any josephsmithpapers.org page as Markdown. Restricted to that host. |

Long results are capped at about 20,000 characters, and each such result says which `offset` to pass to read further.

## Use it

### Remote (claude.ai, Claude Desktop, Claude mobile)
Once deployed (see below), add a custom connector with the deployment URL plus `/mcp`, e.g. `https://samuelbaird.com/peepstone/mcp` (the app is served under the `/peepstone` base path):
**Settings → Connectors → Add custom connector**.

### Local (stdio)
```bash
git clone https://github.com/Samuel-Baird/peepstone && cd peepstone
npm install          # also builds dist/stdio.js
```
Claude Desktop (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "peepstone": { "command": "node", "args": ["/absolute/path/to/peepstone/dist/stdio.js"] }
  }
}
```
Claude Code:
```bash
claude mcp add peepstone -- node /absolute/path/to/peepstone/dist/stdio.js
```

## Develop

```bash
npm run dev            # Next.js dev server; MCP endpoint at http://localhost:3000/mcp
npm run stdio          # run the stdio server from source
npm test               # parser tests against recorded fixtures (no network)
npm run smoke          # every tool against the live site
npm run record-fixtures  # refresh test/fixtures from the live site
npx @modelcontextprotocol/inspector   # then connect to http://localhost:3000/mcp
```

Behind an HTTPS proxy, run Node with `NODE_USE_ENV_PROXY=1` so that `fetch` uses `HTTPS_PROXY`.

Layout:
- `src/jsp/`: the site client (`client.ts`), HTML→Markdown conversion (`html.ts`), and parsers for search, documents, directory entries and the other page types.
- `src/server.ts`: tool definitions, shared by `app/mcp/route.ts` (HTTP, via `mcp-handler`) and `src/stdio.ts`.

## Deploy (Cloudflare Workers)
Runs on Cloudflare Workers via [OpenNext](https://opennext.js.org/cloudflare) as the `peepstone` Worker (`wrangler.jsonc`); `.github/workflows/deploy.yml` deploys it on pushes to main. No environment variables or secrets are needed. `samuelbaird.com/peepstone/*` reaches it over a service binding from the samuelbaird-com Worker.

- `npm run preview`: build and serve it locally in workerd (`/peepstone`, `/peepstone/mcp`, bare `/mcp`).
- `npm run cf:deploy`: build and deploy by hand (needs `wrangler login`).
- `worker.ts` wraps the OpenNext worker to rewrite bare `/mcp` to `/peepstone/mcp`.
- `next.config.ts` aliases the MCP SDK's validator shim to the `@cfworker/json-schema` one, because Workers forbid the Ajv validator's `new Function`.
- The old peepstone.vercel.app address was retired with the Vercel project (Nov 2026).

## Etiquette and attribution
Peepstone sends at most 2 concurrent requests per instance, retries with backoff, caches responses for 10 minutes, and identifies itself with a `Peepstone-MCP` User-Agent.

Peepstone is an independent project. It is **not affiliated with or endorsed by** The Church of Jesus Christ of Latter-day Saints, the Church Historian's Press or the Joseph Smith Papers Project. The documents, transcriptions and editorial content belong to their owners (© Intellectual Reserve, Inc.). Use them according to the site's [terms of use](https://www.churchofjesuschrist.org/legal/terms-of-use), and cite josephsmithpapers.org.

The site's internal endpoints are undocumented and may change. If a tool breaks, run `npm run smoke` to see which one.

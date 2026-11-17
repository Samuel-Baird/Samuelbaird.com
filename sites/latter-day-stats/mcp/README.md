# latter-day-stats-mcp

An MCP server exposing the data behind [Latter-day Stats](https://github.com/Samuel-Baird/latter-day-stats): channels and studies.

**Hosted, remote version — no setup required:** `https://latterdaystats.samuelbaird.com/api/mcp`
(source: [`src/app/api/mcp/route.ts`](../src/app/api/mcp/route.ts)). The hosted version also
exposes Data Explorer dataset tools (`list_datasets`, `get_dataset`, `list_dataset_categories`),
which this standalone local server does not — those datasets are static site content, not
Supabase rows, so they're only served from the deployed app.
Step-by-step instructions for Claude and ChatGPT: [latterdaystats.samuelbaird.com/connect](https://latterdaystats.samuelbaird.com/connect).
Point any MCP client that supports remote/Streamable HTTP servers at that URL directly,
or use [`mcp-remote`](https://www.npmjs.com/package/mcp-remote) for stdio-only clients:

```json
{
  "mcpServers": {
    "latter-day-stats": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://latterdaystats.samuelbaird.com/api/mcp"]
    }
  }
}
```

The rest of this document covers the standalone local server below — useful if you want
to run against your own Supabase project or hack on the tools without redeploying.

- **Channels** — the tracked YouTube channels and their subscriber/view stats. Channels tagged `Critical` are included, matching the website, which lists every channel for everyone.
- **Studies** — the research library (surveys, papers, articles).

## Setup

```bash
cd mcp
npm install
npm run build
```

Channels and studies read from the site's Supabase project (public, read-only — the same anon key the website ships to browsers). Set these two env vars to the values from the site's `.env.local` / Supabase project settings:

- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`

## Register with an MCP client

Claude Code / Claude Desktop `mcp.json` (or equivalent):

```json
{
  "mcpServers": {
    "latter-day-stats": {
      "command": "node",
      "args": ["/absolute/path/to/latter-day-stats/mcp/dist/index.js"],
      "env": {
        "NEXT_PUBLIC_SUPABASE_URL": "https://YOUR-PROJECT-REF.supabase.co",
        "NEXT_PUBLIC_SUPABASE_ANON_KEY": "eyJ..."
      }
    }
  }
}
```

## Tools

| Tool | Purpose |
|---|---|
| `list_channels` | Search/filter channels (search, type, country, featured, min subscribers, sort). |
| `get_channel` | One channel's detail + subscriber/view history, by slug or YouTube channel ID. |
| `list_channel_types` | Distinct channel type tags in use. |
| `list_studies` | Search/filter studies (full-text search, tags, year, category). |
| `get_study` | One study's detail, by slug. |
| `list_study_tags` | All study tags with counts. |

## Development

```bash
npm run dev   # run src/index.ts directly via tsx, no build step
```

# Omni

One MCP endpoint that fronts several others: `https://omni.samuelbaird.com/api/mcp`

Stateless Streamable-HTTP proxy. Tools from each upstream are re-exposed with a source prefix.

| Prefix | Server | URL |
|---|---|---|
| `gsa_` | Gospel Scholar Archives | https://corpus.noahairmet.com/mcp |
| `pulpit_` | Pulpit (General Conference 1830-present) | https://mcp.pulpit-archive.org/mcp |
| `ldstats_` | Latter-day Stats | https://latterdaystats.samuelbaird.com/api/mcp |
| `peepstone_` | Joseph Smith Papers | https://peepstone.vercel.app/mcp |
| `deseret_` | Deseret MCP (Deseret Alphabet, deseret.wiki) | https://mcp.deseret.wiki/api/mcp |

Add or remove upstreams in `src/lib/upstreams.ts`; `OMNI_URL_<ID>` overrides an upstream's URL (e.g. to test against a local server). Tool lists are cached for 5 minutes; a down upstream is skipped without breaking the rest.

`npm run dev`, then `node scripts/smoke.mjs http://localhost:3000/api/mcp [tool] [json-args]`.

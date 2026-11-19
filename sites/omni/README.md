# Omni

One MCP endpoint that fronts several others: `https://samuelbaird.com/omni/mcp` (served under the `/omni` base path; `/omni/api/mcp` and the old `omni.samuelbaird.com/api/mcp` and `/mcp` still work)

Stateless Streamable-HTTP proxy. Tools from each upstream are re-exposed with a source prefix.

| Prefix | Server | URL |
|---|---|---|
| `gsa_` | Gospel Scholar Archives | https://corpus.noahairmet.com/mcp |
| `pulpit_` | Pulpit (General Conference 1830-present) | https://mcp.pulpit-archive.org/mcp |
| `ldstats_` | Latter-day Stats | https://latterdaystats.samuelbaird.com/api/mcp |
| `peepstone_` | Joseph Smith Papers | https://peepstone.vercel.app/mcp |
| `deseret_` | Deseret MCP (Deseret Alphabet, deseret.wiki) | https://mcp.deseret.wiki/api/mcp |

Add or remove upstreams in `src/lib/upstreams.ts`; `OMNI_URL_<ID>` overrides an upstream's URL (e.g. to test against a local server). Tool lists are cached for 5 minutes; a down upstream is skipped without breaking the rest.

`npm run dev`, then `node scripts/smoke.mjs http://localhost:3000/omni/mcp [tool] [json-args]`.

## Deploy (Cloudflare Workers)

Runs on Cloudflare Workers via [OpenNext](https://opennext.js.org/cloudflare) as the `omni` Worker (`wrangler.jsonc`); `.github/workflows/deploy.yml` deploys it on pushes to main. `samuelbaird.com/omni/*` reaches it over a service binding; omni.samuelbaird.com is a custom domain on it. No secrets are needed (`OMNI_URL_<ID>` vars are optional overrides).

- `npm run preview`: build and serve it locally in workerd; `npm run cf:deploy`: build and deploy by hand.
- `worker.ts` wraps the OpenNext worker: rewrites bare `/api/mcp` and `/mcp` to `/omni/api/mcp` (what `vercel.json` did) and adds `X-Robots-Tag: noindex` to every response, so Omni stays hidden on any host. `/omni/mcp` is a Next rewrite.
- Omni is hidden: never publish its workers.dev or other URLs.

export type Upstream = { id: string; name: string; url: string; description: string };

// Add a new MCP here and it is exposed through omni with the tool prefix `<id>_`.
// Any upstream's URL can be overridden with OMNI_URL_<ID> (e.g. OMNI_URL_DESERET=http://localhost:4321/api/mcp) for local testing.
const BASE: Upstream[] = [
  { id: "gsa", name: "Gospel Scholar Archives", url: "https://corpus.noahairmet.com/mcp", description: "Access to David's Gospel Scholar Archives" },
  { id: "pulpit", name: "Pulpit", url: "https://mcp.pulpit-archive.org/mcp", description: "General Conference 1830-present" },
  { id: "ldstats", name: "Latter-day Stats", url: "https://latterdaystats.samuelbaird.com/api/mcp", description: "LDS-related YouTube channels and research studies" },
  { id: "peepstone", name: "Peepstone", url: "https://peepstone.vercel.app/mcp", description: "All the Joseph Smith Papers" },
  { id: "deseret", name: "Deseret MCP", url: "https://mcp.deseret.wiki/api/mcp", description: "Deseret Alphabet: English to Deseret and back, and every source on deseret.wiki" },
];

export const UPSTREAMS: Upstream[] = BASE.map((u) => ({ ...u, url: process.env[`OMNI_URL_${u.id.toUpperCase()}`] || u.url }));

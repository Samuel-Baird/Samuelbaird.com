/** Full-site search via JSP's internal API: POST /api/v2-search-results. */
import { absUrl, canonicalPath, postJson } from "./client";
import { htmlToText } from "./html";

/** Friendly type names → JSP refinement ids. */
export const SEARCH_TYPES = {
  papers: "documents-papers",
  administrative: "documents-papers-administrative",
  documents: "documents-papers-documents",
  legal: "documents-papers-legal",
  financial: "documents-papers-financial",
  histories: "documents-papers-histories",
  journals: "documents-papers-journals",
  "revelations-and-translations": "documents-papers-revelations-and-translations",
  introductions: "documents-papers-introductions",
  "other-contemporary-papers": "documents-papers-other-contemporary-papers",
  reference: "related-materials",
  people: "biographical-directory",
  places: "geographical-directory",
  glossary: "glossary",
  events: "event",
} as const;

export type SearchType = keyof typeof SEARCH_TYPES;
export const SEARCH_TYPE_NAMES = Object.keys(SEARCH_TYPES) as [SearchType, ...SearchType[]];

export type SearchParams = {
  query: string;
  types?: SearchType[];
  /** Person facet names exactly as JSP lists them ("Hyrum Smith"), or facet ids. */
  people?: string[];
  /** Place facet names ("Nauvoo, Illinois"), or facet ids. */
  places?: string[];
  /** Subject facet names ("Nauvoo Legion"), or facet ids. */
  subjects?: string[];
  startDate?: string;
  endDate?: string;
  transcriptsOnly?: boolean;
  sort?: "relevance" | "alphabetical" | "date";
  page?: number;
  perPage?: number;
  facets?: boolean;
};

export type SearchHit = {
  title: string;
  url: string;
  date?: string;
  snippet: string;
  matchIn?: string;
  image?: string;
};

export type Facet = { id: string; title: string; count: number };

export type SearchResult = {
  query: string;
  total: number;
  page: number;
  perPage: number;
  hits: SearchHit[];
  facets?: {
    types: Facet[];
    people: Facet[];
    places: Facet[];
    subjects: Facet[];
    dateRange?: { min: string; max: string };
  };
};

type FacetPrefix = "person" | "place" | "topic";

/** Build a facet id from a display name, mirroring JSP's scheme. */
export function facetId(prefix: FacetPrefix, title: string): string {
  return prefix + title.trim().toLowerCase().replace(/\s+/g, "-");
}

/** True if the value looks like a facet id ("personhyrum-smith") rather than a name. */
export function isFacetId(prefix: FacetPrefix, value: string): boolean {
  const v = value.trim();
  return v.startsWith(prefix) && !/\s/.test(v) && v.toLowerCase() === v;
}

/**
 * The API filters people/places/subjects by facet *title* (the id alone is
 * ignored), so we send both.
 */
const facetFilters = (prefix: FacetPrefix, titles: string[] = []) =>
  titles.map((title) => ({ id: facetId(prefix, title), title: title.trim(), selected: true }));

/** Selecting "papers" alone barely filters; the site UI sends every subtype too. */
function typeFilters(types: SearchType[] = []) {
  const ids = new Set<string>();
  for (const t of types) {
    const id = SEARCH_TYPES[t];
    ids.add(id);
    if (id === "documents-papers") {
      for (const sub of Object.values(SEARCH_TYPES)) if (sub.startsWith("documents-papers-")) ids.add(sub);
    }
  }
  return [...ids].map((id) => ({ id, selected: true }));
}

export function buildSearchBody(p: SearchParams) {
  return {
    search: {
      query: p.query,
      perPage: p.perPage ?? 10,
      sort: p.sort ?? "relevance",
      pageNumber: p.page ?? 1,
      getRefinements: p.facets ?? true,
      documentURI: "",
      refinements: {
        dates: { start: p.startDate ?? "", end: p.endDate ?? "" },
        locations: { location: facetFilters("place", p.places) },
        persons: { person: facetFilters("person", p.people) },
        subjects: { subject: facetFilters("topic", p.subjects) },
        types: { type: typeFilters(p.types) },
        isSuggestion: false,
        transcriptsOnly: p.transcriptsOnly ?? false,
      },
    },
  };
}

const MATCH_LABELS: Record<string, string> = {
  documentText: "document text",
  footnote: "footnote",
  personSummaryText: "biography",
  placeSummaryText: "place description",
  topicSummaryText: "glossary entry",
  eventSummaryText: "event description",
};

function facets(list: any[] | undefined): Facet[] {
  return (list ?? []).map((f) => ({ id: f.id, title: f.title, count: Number(f.count) }));
}

function flattenTypes(list: any[] | undefined, depth = 0): Facet[] {
  const out: Facet[] = [];
  for (const t of list ?? []) {
    out.push({ id: t.id, title: (depth ? "  " : "") + t.title, count: Number(t.count) });
    out.push(...flattenTypes(t.types?.type, depth + 1));
  }
  return out;
}

export function parseSearchResponse(json: any, p: SearchParams): SearchResult {
  const s = json?.search ?? {};
  const hits: SearchHit[] = (s.results?.result ?? []).map((r: any) => {
    const link = canonicalPath(r.link ?? "");
    return {
      title: htmlToText(r.title),
      url: absUrl(link),
      date: r.date || undefined,
      snippet: snippet(r.summary),
      matchIn: MATCH_LABELS[r.summaryType] ?? undefined,
      image: r.image ? absUrl(r.image) : undefined,
    };
  });
  const ref = s.refinements;
  return {
    query: s.query ?? p.query,
    total: Number(s.total ?? hits.length),
    page: Number(s.pageNumber ?? p.page ?? 1),
    perPage: Number(s.perPage ?? p.perPage ?? 10),
    hits,
    facets: ref
      ? {
          types: flattenTypes(ref.types?.type),
          people: facets(ref.persons?.person),
          places: facets(ref.locations?.location),
          subjects: facets(ref.subjects?.subject),
          dateRange: ref.dates?.min ? { min: ref.dates.min, max: ref.dates.max } : undefined,
        }
      : undefined,
  };
}

/** Search snippets come as <summary><e>… <mark>hit</mark> …</e></summary>. */
function snippet(html: string | undefined): string {
  if (!html) return "";
  return html
    .replace(/<mark>/g, "**")
    .replace(/<\/mark>/g, "**")
    .replace(/<[^>]+>/g, "")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/\*\*\s*\*\*/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

/**
 * If facet ids were passed instead of names, look the names up from the
 * query's own facets (ids only appear in facets returned for that query).
 */
async function resolveFacetIds(p: SearchParams): Promise<SearchParams> {
  const groups: Array<["people" | "places" | "subjects", FacetPrefix]> = [
    ["people", "person"],
    ["places", "place"],
    ["subjects", "topic"],
  ];
  if (!groups.some(([k, pre]) => p[k]?.some((v) => isFacetId(pre, v)))) return p;
  const base = parseSearchResponse(
    await postJson<any>("/api/v2-search-results", buildSearchBody({ query: p.query, perPage: 10, facets: true })),
    p,
  );
  const out: SearchParams = { ...p };
  for (const [k, pre] of groups) {
    out[k] = p[k]?.map((v) => {
      if (!isFacetId(pre, v)) return v;
      const hit = base.facets?.[k].find((f) => f.id === v.trim());
      // Fall back to a best-effort title reconstructed from the id.
      return hit?.title ?? v.slice(pre.length).replace(/-/g, " ");
    });
  }
  return out;
}

export async function search(p: SearchParams): Promise<SearchResult> {
  const params = await resolveFacetIds(p);
  const json = await postJson<any>("/api/v2-search-results", buildSearchBody(params));
  return parseSearchResponse(json, params);
}

export function formatSearch(r: SearchResult, facetLimit = 8): string {
  const lines: string[] = [];
  const first = (r.page - 1) * r.perPage + 1;
  const last = first + r.hits.length - 1;
  lines.push(
    `# Search: “${r.query}”`,
    r.total
      ? `${r.total.toLocaleString("en-US")} results — showing ${first}–${last} (page ${r.page} of ${Math.max(1, Math.ceil(r.total / r.perPage))})`
      : "No results.",
    "",
  );
  r.hits.forEach((h, i) => {
    const meta = [h.date, h.matchIn ? `match in ${h.matchIn}` : ""].filter(Boolean).join(" · ");
    lines.push(`${first + i}. **${h.title}**${meta ? ` (${meta})` : ""}`);
    lines.push(`   ${h.url}`);
    if (h.snippet) lines.push(`   ${h.snippet}`);
  });
  if (r.facets) {
    const f = r.facets;
    const fmt = (list: Facet[]) =>
      list
        .slice(0, facetLimit)
        .map((x) => `${x.title.trim()} (${x.count.toLocaleString("en-US")})`)
        .join("; ");
    lines.push("", "## Refine (pass these names back to `search` as types / people / places / subjects)");
    const typeCounts = f.types
      .map((t) => {
        const name = Object.entries(SEARCH_TYPES).find(([, id]) => id === t.id)?.[0];
        return name ? `${name} (${t.count.toLocaleString("en-US")})` : null;
      })
      .filter(Boolean)
      .join("; ");
    if (typeCounts) lines.push(`- types: ${typeCounts}`);
    if (f.people.length) lines.push(`- people: ${fmt(f.people)}`);
    if (f.places.length) lines.push(`- places: ${fmt(f.places)}`);
    if (f.subjects.length) lines.push(`- subjects: ${fmt(f.subjects)}`);
    if (f.dateRange) lines.push(`- dates: ${f.dateRange.min} to ${f.dateRange.max}`);
  }
  return lines.join("\n");
}

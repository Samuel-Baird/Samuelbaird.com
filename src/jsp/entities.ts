/**
 * Reference entries: people (/person), places (/place), glossary topics
 * (/topic) and timeline events (/event). All four share one data shape:
 * pageProps[kind].authority.refObject.{documentInfo, [kind]}.
 */
import { JspError, absUrl, canonicalPath, getPageData, toPath } from "./client";
import { htmlToMarkdown, htmlToText, renderFootnotes, type Footnote } from "./html";
import { citation } from "./cite";
import { search, type SearchType } from "./search";

export type EntityKind = "person" | "place" | "topic" | "event";

const SEARCH_TYPE_FOR: Record<EntityKind, SearchType> = {
  person: "people",
  place: "places",
  topic: "glossary",
  event: "events",
};

export const KIND_LABEL: Record<EntityKind, string> = {
  person: "Person",
  place: "Place",
  topic: "Glossary term",
  event: "Event",
};

export type Entity = {
  kind: EntityKind;
  id: string;
  name: string;
  url: string;
  classification?: string;
  abstract?: string;
  altNames: string[];
  date?: string;
  geo?: { lat: number; lon: number };
  description: string;
  footnotes: Footnote[];
  images: Array<{ url: string; title?: string; caption?: string }>;
  references?: number;
  related: Array<{ group: string; total: number; links: Array<{ title: string; url: string; date?: string }> }>;
  citation: string;
  /** Other search matches when the entry was found by name. */
  otherMatches?: Array<{ title: string; url: string }>;
};

/**
 * Resolve a slug, URL or human name to a path like /person/emma-hale-smith.
 * Names are looked up with the site search restricted to the matching type.
 */
export async function resolveEntityPath(kind: EntityKind, input: string): Promise<string> {
  const s = input.trim();
  const looksLikeSlug = /^[a-z0-9][a-z0-9-]*$/.test(s);
  if (/^https?:\/\//i.test(s) || s.startsWith("/") || /josephsmithpapers\.org/i.test(s)) {
    const path = toPath(s).split(/[?#]/)[0];
    if (!path.startsWith(`/${kind}/`)) {
      throw new JspError(`Expected a /${kind}/ URL, got ${path}.`);
    }
    return path;
  }
  if (looksLikeSlug) return `/${kind}/${s}`;
  return (await searchEntityPath(kind, s)).path;
}

async function searchEntityPath(kind: EntityKind, s: string) {
  const r = await search({ query: s, types: [SEARCH_TYPE_FOR[kind]], perPage: 10, facets: false });
  const hits = r.hits.filter((h) => new URL(h.url).pathname.startsWith(`/${kind}/`));
  if (!hits.length) throw new JspError(`No ${KIND_LABEL[kind].toLowerCase()} found matching “${s}”.`);
  return {
    path: new URL(hits[0].url).pathname,
    others: hits.slice(1, 6).map((h) => ({ title: h.title, url: h.url.split("?")[0] })),
  };
}

function list<T>(v: T | T[] | undefined | null): T[] {
  if (v == null) return [];
  return Array.isArray(v) ? v : [v];
}

function altNames(entity: any, kind: EntityKind): string[] {
  const raw = entity?.altNames;
  const vals: unknown[] = Array.isArray(raw)
    ? raw
    : raw && typeof raw === "object"
      ? list((raw as any)[`${kind}Name`])
      : [];
  return vals.map((x) => htmlToText(String(x ?? ""))).filter(Boolean);
}

export function parseEntity(pageProps: Record<string, any>, kind: EntityKind, path: string, relatedLimit = 25): Entity {
  const e = pageProps[kind];
  const ro = e?.authority?.refObject;
  if (!ro) throw new JspError(`No ${kind} data at ${absUrl(path)}`);
  const info = ro.documentInfo ?? {};
  const body = ro[kind] ?? {};
  const desc = htmlToMarkdown(body.description?.summary);
  const url = absUrl(info.defaultUrl || path);
  const name = htmlToText(ro.docDesc || info.title || info.a?.title) || path;
  const geo = body.geo?.lat && body.geo?.long ? { lat: Number(body.geo.lat), lon: Number(body.geo.long) } : undefined;
  const date = body.date?._value || info.date?._value || info.subtitle || undefined;

  return {
    kind,
    id: String(ro.url ?? e.authority.target ?? ""),
    name,
    url,
    classification: info.classification || undefined,
    abstract: htmlToText(info.abstract) || undefined,
    altNames: altNames(body, kind),
    date,
    geo,
    description: desc.markdown,
    footnotes: desc.footnotes,
    images: list(e.images).map((i: any) => ({
      url: absUrl(i.location),
      title: i.title || undefined,
      caption: htmlToText(i.caption) || undefined,
    })),
    references: e.authority.references ? Number(e.authority.references) : undefined,
    related: list(e.relatedlinks).map((g: any) => {
      const links = list(g.links);
      return {
        group: String(g.name),
        total: links.length,
        links: links.slice(0, relatedLimit).map((l: any) => ({
          title: htmlToText(l.value),
          url: absUrl(canonicalPath(l.url)),
          date: l.date || undefined,
        })),
      };
    }),
    citation: citation({ title: name, url }),
  };
}

export async function getEntity(kind: EntityKind, input: string, relatedLimit = 25): Promise<Entity> {
  const s = input.trim();
  const isSlug = /^[a-z0-9][a-z0-9-]*$/.test(s);
  const isUrl = /^https?:\/\//i.test(s) || s.startsWith("/") || /josephsmithpapers\.org/i.test(s);

  if (isUrl || isSlug) {
    const path = await resolveEntityPath(kind, s);
    try {
      const { pageProps } = await getPageData(path);
      return parseEntity(pageProps, kind, path, relatedLimit);
    } catch (err) {
      if (!isSlug) throw err;
      // A guessed slug that doesn't exist: fall through to a name search ("emma-smith" → "emma smith").
    }
  }
  const found = await searchEntityPath(kind, isSlug ? s.replace(/-/g, " ") : s);
  const { pageProps } = await getPageData(found.path);
  const entity = parseEntity(pageProps, kind, found.path, relatedLimit);
  entity.otherMatches = found.others;
  return entity;
}

const GROUP_LABEL: Record<string, string> = {
  papers: "Documents that mention this",
  glossary: "Related glossary entries",
  other: "Other related entries",
};

export function formatEntity(e: Entity, opts: { footnotes?: boolean } = {}): string {
  const out = [`# ${e.name}`];
  const meta: Array<[string, string | undefined]> = [
    ["URL", e.url],
    ["Type", e.classification ?? KIND_LABEL[e.kind]],
    ["Date", e.date],
    ["Also known as", e.altNames.length ? e.altNames.join("; ") : undefined],
    ["Coordinates", e.geo ? `${e.geo.lat}, ${e.geo.lon}` : undefined],
    ["Mentions in the papers", e.references ? e.references.toLocaleString("en-US") : undefined],
    ["Cite as", e.citation],
  ];
  for (const [k, v] of meta) if (v) out.push(`- **${k}:** ${v}`);
  // The abstract is a truncated copy of the description; show it only as a fallback.
  out.push("", e.description || (e.abstract ? `> ${e.abstract}` : "_(No description.)_"));
  if (opts.footnotes !== false && e.footnotes.length) {
    out.push("", "### Notes", "", renderFootnotes(e.footnotes));
  }
  if (e.images.length) {
    out.push("", "## Images");
    for (const i of e.images) out.push(`- ${i.title ?? "Image"}${i.caption ? ` — ${i.caption}` : ""}: ${i.url}`);
  }
  if (e.otherMatches?.length) {
    out.push("", "## Other matches for this name (pass a URL to get_" + (e.kind === "topic" ? "glossary_term" : e.kind) + " to switch)");
    for (const m of e.otherMatches) out.push(`- ${m.title}: ${m.url}`);
  }
  for (const g of e.related) {
    if (!g.total) continue;
    const shown = g.links.length;
    out.push("", `## ${GROUP_LABEL[g.group] ?? g.group} (${g.total}${shown < g.total ? `, first ${shown} shown` : ""})`);
    for (const l of g.links) out.push(`- ${l.title}${l.date ? ` (${l.date})` : ""}: ${l.url}`);
  }
  return out.join("\n");
}

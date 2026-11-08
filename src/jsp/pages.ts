/**
 * Articles, browse panes, the calendar of documents, reference directories,
 * and a generic "any JSP URL" reader that routes to the right parser.
 */
import {
  JspError,
  absUrl,
  canonicalPath,
  getPageData,
  postJson,
  toPath,
} from "./client";
import { citation } from "./cite";
import { formatDocument, getDocument, parseDocumentPage } from "./document";
import { formatEntity, parseEntity, type EntityKind } from "./entities";
import {
  htmlToMarkdown,
  htmlToText,
  pageHtmlToMarkdown,
  renderFootnotes,
} from "./html";

// ---------------------------------------------------------------------------
// Articles: /articles/{slug}, /back/{slug}, /intro/{slug}, /doc/{slug}, /news

export function formatArticle(pageProps: Record<string, any>, path: string): string {
  const a = pageProps.articleData;
  if (!a) throw new JspError(`No article data at ${absUrl(path)}`);
  const info = a.documentInfo ?? {};
  const title = htmlToText(a.title || info.title) || path;
  const url = absUrl(path);
  const body = htmlToMarkdown(a.content);
  const notes = (a.footnotes ?? []).map((n: any) => ({
    marker: String(n.number ?? n.id),
    text: htmlToMarkdown(n.text).markdown,
  }));
  const footnotes = notes.length ? notes : body.footnotes;
  const out = [`# ${title}`, `- **URL:** ${url}`];
  const date = info.date?._value || info.date?.value || info.subtitle;
  if (info.classification && info.classification !== "article") out.push(`- **Type:** ${info.classification}`);
  if (date) out.push(`- **Date:** ${date}`);
  if (info.author && info.author !== "Author Name") out.push(`- **Author:** ${htmlToText(info.author)}`);
  out.push(`- **Cite as:** ${citation({ title, url })}`, "", body.markdown);
  if (footnotes.length) out.push("", "### Notes", "", renderFootnotes(footnotes));
  return out.join("\n");
}

export async function getArticle(input: string): Promise<string> {
  const path = canonicalPath(toPath(input, "/articles"));
  const { pageProps } = await getPageData(path);
  return formatArticle(pageProps, path);
}

// ---------------------------------------------------------------------------
// Browse the papers: /the-papers/{series}/{volume}

type BrowseLink = { title: string; url: string; description?: string; count?: string };

function browseLink(l: any): BrowseLink {
  const t = typeof l.title === "object" && l.title ? l.title : l;
  return {
    title: htmlToText(t.text ?? l.text ?? ""),
    url: absUrl(t.href ?? l.href ?? ""),
    description: l.description ? htmlToText(l.description) : undefined,
    count: l.count ? String(l.count) : undefined,
  };
}

export function formatBrowse(pageProps: Record<string, any>, path: string): string {
  const panes: any[] = (pageProps.docDetails?.panes ?? pageProps.baseInfo?.panes ?? []).filter((p: any) =>
    (p.sections ?? []).some((s: any) => (s.links ?? []).length > 0),
  );
  if (!panes.length) throw new JspError(`No browse data at ${absUrl(path)}`);
  const pane = panes[panes.length - 1];
  const crumbs = panes.slice(0, -1).map((p) => htmlToText(p.title));
  const out = [`# ${htmlToText(pane.title)}`, `- **URL:** ${absUrl(path)}`];
  if (crumbs.length) out.push(`- **Within:** ${crumbs.join(" › ")}`);
  if (pane.message) out.push("", htmlToMarkdown(pane.message).markdown);
  for (const sec of pane.sections ?? []) {
    const links = (sec.links ?? []).map(browseLink).filter((l: BrowseLink) => l.title);
    if (!links.length) continue;
    out.push("", sec.title ? `## ${htmlToText(sec.title)}` : "## Contents");
    for (const l of links) {
      const extra = [l.count ? `${l.count} items` : "", l.description ?? ""].filter(Boolean).join(" — ");
      out.push(`- ${l.title}${extra ? ` (${extra})` : ""}: ${l.url}`);
    }
  }
  out.push(
    "",
    "_Pass a /the-papers/… path back to `browse_papers` to go deeper; open documents (/paper-summary/…) with `get_document`._",
  );
  return out.join("\n");
}

export async function browsePapers(path = ""): Promise<string> {
  const p = path.trim().replace(/^\/+|\/+$/g, "");
  const full = /^https?:|^the-papers/.test(p) ? toPath(p.startsWith("the-papers") ? `/${p}` : p) : `/the-papers${p ? `/${p}` : ""}`;
  if (!full.startsWith("/the-papers")) throw new JspError(`Expected a /the-papers path, got ${full}`);
  const { pageProps } = await getPageData(full);
  return formatBrowse(pageProps, full);
}

// ---------------------------------------------------------------------------
// Calendar of Documents (chronological list of every known JS document).

const CALENDAR_API =
  "https://jsp-api.pvu.cf.churchofjesuschrist.org/jsp-api/v1/reference/calendar/search";

export type CalendarEntry = {
  heading: string;
  date: string;
  sortDate: string;
  versions: string[];
};

export async function getCalendar(p: {
  startDate: string;
  endDate?: string;
  keywords?: string;
}): Promise<CalendarEntry[]> {
  const qs = new URLSearchParams({
    startDate: p.startDate,
    endDate: p.endDate ?? endOfMonth(p.startDate),
    keywords: p.keywords ?? "",
  });
  const json = await postJson<any[]>("/api/proxyToBackend", {
    headers: {},
    method: "GET",
    url: `${CALENDAR_API}?${qs.toString()}`,
  });
  if (!Array.isArray(json)) throw new JspError("Unexpected calendar response from JSP.");
  return json.map(parseCalendarEntry);
}

export function parseCalendarEntry(e: any): CalendarEntry {
  return {
    heading: htmlToText(e.heading),
    date: htmlToText(e.label),
    sortDate: String(e.sortDate ?? "").slice(0, 10),
    versions: (e.content ?? []).map((c: string) => htmlToMarkdown(c).markdown.replace(/\s+/g, " ").trim()),
  };
}

function endOfMonth(iso: string): string {
  const [y, m] = iso.split("-").map(Number);
  if (!y || !m) return iso;
  const d = new Date(Date.UTC(y, m, 0));
  return d.toISOString().slice(0, 10);
}

export function formatCalendar(entries: CalendarEntry[], p: { startDate: string; endDate?: string; keywords?: string }, offset = 0, limit = 50): string {
  const end = p.endDate ?? endOfMonth(p.startDate);
  const slice = entries.slice(offset, offset + limit);
  const out = [
    `# Calendar of Documents: ${p.startDate} to ${end}${p.keywords ? ` (“${p.keywords}”)` : ""}`,
    `${entries.length} documents${entries.length > slice.length ? `, showing ${offset + 1}–${offset + slice.length}` : ""}. Source: ${absUrl("/reference/calendar-of-documents")}`,
  ];
  for (const e of slice) {
    out.push("", `## ${e.date} — ${e.heading}`);
    for (const v of e.versions) out.push(`- ${v}`);
  }
  if (offset + slice.length < entries.length) {
    out.push("", `_More entries: call again with offset=${offset + slice.length}._`);
  }
  return out.join("\n");
}

// ---------------------------------------------------------------------------
// Reference directories: /reference/people?filter=a, /reference/places, …

export function formatEntityList(pageProps: Record<string, any>, path: string): string {
  // The site sends the whole directory and filters by letter in the browser.
  const letter = new URLSearchParams(path.split("?")[1] ?? "").get("filter")?.toLowerCase();
  const all: any[] = pageProps.entityList ?? [];
  const list = letter
    ? all.filter((e) => htmlToText(e.name).toLowerCase().normalize("NFD").startsWith(letter))
    : all;
  const title = htmlToText(pageProps.summary?.title) || path;
  const out = [
    `# ${title}${letter ? ` — ${letter.toUpperCase()}` : ""}`,
    `- **URL:** ${absUrl(path)}`,
    `- **Entries:** ${list.length}${letter ? ` (of ${all.length}; add ?filter=<letter> to pick another letter)` : ""}`,
    "",
  ];
  for (const e of list) out.push(`- ${htmlToText(e.name)}: ${absUrl(e.url)}`);
  return out.join("\n");
}

// ---------------------------------------------------------------------------
// Generic reader for any josephsmithpapers.org URL.

const ENTITY_ROUTES: Record<string, EntityKind> = {
  "/person/[uri]": "person",
  "/place/[uri]": "place",
  "/topic/[uri]": "topic",
  "/event/[uri]": "event",
};

export async function readJspUrl(input: string): Promise<string> {
  const path = canonicalPath(toPath(input));
  const docMatch = path.match(/^\/paper-summary\/([^/?#]+)(?:\/(\d+))?/);
  if (docMatch) {
    const d = await getDocument(path);
    return formatDocument(d, ["transcript", "footnotes"]);
  }

  const { route, pageProps, html } = await getPageData(path, { keepHtml: true });

  const kind = ENTITY_ROUTES[route];
  if (kind && pageProps[kind]) return formatEntity(parseEntity(pageProps, kind, path));
  if (pageProps.summary?.clearText !== undefined) {
    const m = route.match(/paper-summary/) ? path.match(/^\/paper-summary\/([^/]+)\/(\d+)/) : null;
    if (m) return formatDocument(parseDocumentPage(pageProps, { slug: m[1], page: Number(m[2]) }));
  }
  if (pageProps.articleData) return formatArticle(pageProps, path);
  if (pageProps.docDetails?.panes) return formatBrowse(pageProps, path);
  if (Array.isArray(pageProps.entityList)) return formatEntityList(pageProps, path);

  // Fallback: render the page's main content.
  const md = html ? pageHtmlToMarkdown(html) : { markdown: "", footnotes: [] };
  const title = pageProps.pageTitle || pageProps.summary?.title || pageProps.title || path;
  return [`# ${htmlToText(String(title))}`, `- **URL:** ${absUrl(path)}`, "", md.markdown || "_(No readable content.)_"].join("\n");
}

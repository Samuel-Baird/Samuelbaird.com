/** Documents ("papers"): /paper-summary/{slug}/{page}. */
import { IMAGE_BASE, JspError, absUrl, getPageData, toPath } from "./client";
import { htmlToMarkdown, htmlToText, renderFootnotes, type Footnote } from "./html";
import { citation } from "./cite";

export type DocumentSection =
  | "transcript"
  | "footnotes"
  | "sourceNote"
  | "historicalIntro"
  | "versions";

export type DocumentRef = { slug: string; page: number };

/** Accepts "journal-1835-1836", "/paper-summary/journal-1835-1836/11", or a full URL. */
export function parseDocumentRef(input: string, page?: number): DocumentRef {
  const path = toPath(input, "/paper-summary").split(/[?#]/)[0];
  const m = path.match(/^\/paper-summary\/([^/]+)(?:\/(\d+))?/);
  if (!m) {
    throw new JspError(
      `Not a document URL: ${input}. Documents live at /paper-summary/{slug}/{page}; use fetch_jsp_url for other pages.`,
    );
  }
  return { slug: m[1], page: page ?? (m[2] ? Number(m[2]) : 1) };
}

export function documentPath(ref: DocumentRef) {
  return `/paper-summary/${ref.slug}/${ref.page}`;
}

export type DocumentPage = {
  url: string;
  slug: string;
  page: number;
  numberOfPages: number;
  title: string;
  editorialPageNumber?: string;
  date?: string;
  classification?: string;
  series?: string;
  handwriting?: string;
  scribes: string[];
  printVolume?: string;
  images?: { thumbnail?: string; medium?: string; large?: string; download?: string; deepZoom?: string };
  transcript: string;
  footnotes: Footnote[];
  sourceNote?: { text: string; footnotes: Footnote[] };
  historicalIntro?: { text: string; footnotes: Footnote[] };
  versions: Array<{ title: string; url: string; featured: boolean }>;
  previous?: string;
  next?: string;
  citation: string;
};

function img(path: string | undefined) {
  return path ? IMAGE_BASE + (path.startsWith("/") ? "" : "/") + path : undefined;
}

function noteList(list: any[] | undefined): Footnote[] {
  return (list ?? []).map((n) => ({
    marker: String(n.number ?? n.id),
    text: htmlToMarkdown(n.text).markdown,
  }));
}

export function parseDocumentPage(
  pageProps: Record<string, any>,
  ref: DocumentRef,
  opts: { text?: "clear" | "expanded"; lineBreaks?: boolean } = {},
): DocumentPage {
  const s = pageProps.summary;
  if (!s) throw new JspError(`No document data at ${absUrl(documentPath(ref))}`);
  const expanded = opts.text === "expanded";
  const body = htmlToMarkdown(expanded ? s.expandedText : s.clearText, {
    lineBreaks: opts.lineBreaks ?? expanded,
  });
  const numberOfPages = Number(s.numberOfPages ?? pageProps.gallery?.length ?? 1);
  const page = Number(s.requestedPageNumber ?? ref.page);
  const url = absUrl(documentPath({ slug: ref.slug, page }));
  const title = htmlToText(s.documentSeriesTitle || s.cleanEditorialTitle || s.editorialTitle) || ref.slug;
  const editorialPageNumber = s.isPageNumberPresent ? String(s.editorialPageNumber) : undefined;
  const listed = noteList(s.footnotes);
  const intro = s.historicalIntro?.text
    ? (() => {
        const r = htmlToMarkdown(s.historicalIntro.text);
        const fn = noteList(s.historicalIntro.footnotes);
        return { text: r.markdown, footnotes: fn.length ? fn : r.footnotes };
      })()
    : undefined;
  const source = s.sourceNotes?.text
    ? (() => {
        const r = htmlToMarkdown(s.sourceNotes.text);
        const fn = noteList(s.sourceNotes.footnotes);
        return { text: r.markdown, footnotes: fn.length ? fn : r.footnotes };
      })()
    : undefined;

  return {
    url,
    slug: ref.slug,
    page,
    numberOfPages,
    title,
    editorialPageNumber,
    date: s.date || undefined,
    classification: s.classification || undefined,
    series: s.series || undefined,
    handwriting: s.handwriting || undefined,
    scribes: (s.scribes ?? []).map((x: any) => x.name).filter(Boolean),
    printVolume: htmlToText(s.printVolumeLocation) || undefined,
    images: s.images
      ? {
          thumbnail: img(s.images.smallImageUrl),
          medium: img(s.images.mediumImageUrl),
          large: img(s.images.largeImageUrl),
          download: img(s.images.downloadImageUrl),
          deepZoom: img(s.dzUrlXml),
        }
      : undefined,
    transcript: body.markdown,
    // The page's own note list is authoritative; fall back to notes found inline.
    footnotes: listed.length ? listed : body.footnotes,
    sourceNote: source,
    historicalIntro: intro,
    versions: (s.versions ?? []).map((v: any) => ({
      title: htmlToText(v.versionTitle),
      url: absUrl(v.versionLink),
      featured: String(v.versionFeatured) === "true",
    })),
    previous: page > 1 ? absUrl(documentPath({ slug: ref.slug, page: page - 1 })) : undefined,
    next: page < numberOfPages ? absUrl(documentPath({ slug: ref.slug, page: page + 1 })) : undefined,
    citation: citation({
      title,
      page: editorialPageNumber,
      url,
    }),
  };
}

export async function getDocument(
  input: string,
  opts: { page?: number; text?: "clear" | "expanded"; lineBreaks?: boolean } = {},
): Promise<DocumentPage> {
  const ref = parseDocumentRef(input, opts.page);
  const { pageProps } = await getPageData(documentPath(ref));
  return parseDocumentPage(pageProps, ref, opts);
}

export function formatDocument(
  d: DocumentPage,
  sections: DocumentSection[] = ["transcript", "footnotes"],
): string {
  const out: string[] = [];
  const pageLabel = d.editorialPageNumber ? `, Page ${d.editorialPageNumber}` : "";
  out.push(`# ${d.title}${pageLabel}`);
  const meta: Array<[string, string | undefined]> = [
    ["URL", d.url],
    ["Image", `${d.page} of ${d.numberOfPages}`],
    ["Date", d.date],
    ["Type", d.classification],
    ["Handwriting", d.handwriting],
    ["Print edition", d.printVolume],
    ["Page image", d.images?.large],
    ["Previous page", d.previous],
    ["Next page", d.next],
    ["Cite as", d.citation],
  ];
  for (const [k, v] of meta) if (v) out.push(`- **${k}:** ${v}`);

  if (sections.includes("historicalIntro") && d.historicalIntro) {
    out.push("", "## Historical Introduction", "", d.historicalIntro.text);
    if (sections.includes("footnotes") && d.historicalIntro.footnotes.length) {
      out.push("", renderFootnotes(d.historicalIntro.footnotes.map(prefix("intro"))));
    }
  }
  if (sections.includes("sourceNote") && d.sourceNote) {
    out.push("", "## Source Note", "", d.sourceNote.text);
    if (sections.includes("footnotes") && d.sourceNote.footnotes.length) {
      out.push("", renderFootnotes(d.sourceNote.footnotes.map(prefix("source"))));
    }
  }
  if (sections.includes("transcript")) {
    out.push("", "## Transcript", "", d.transcript || "_(No transcript for this page.)_");
    if (sections.includes("footnotes") && d.footnotes.length) {
      out.push("", "### Footnotes", "", renderFootnotes(d.footnotes));
    }
  }
  if (sections.includes("versions") && d.versions.length) {
    out.push("", "## Other versions of this text");
    for (const v of d.versions) out.push(`- ${v.title}${v.featured ? " (featured)" : ""}: ${v.url}`);
  }
  return out.join("\n");
}

const prefix = (p: string) => (n: Footnote): Footnote => ({ ...n, marker: `${p}${n.marker}` });

/** Table of contents + page list for a document. */
export async function getDocumentPages(input: string) {
  const ref = parseDocumentRef(input);
  const { pageProps } = await getPageData(documentPath(ref));
  const s = pageProps.summary ?? {};
  const gallery: any[] = pageProps.gallery ?? [];
  const toc: any[] = pageProps.tableOfContents ?? [];
  return {
    title: htmlToText(s.documentSeriesTitle || s.editorialTitle) || ref.slug,
    url: absUrl(`/paper-summary/${ref.slug}/1`),
    numberOfPages: Number(s.numberOfPages ?? gallery.length),
    pages: gallery.map((g) => ({ page: Number(g.page), label: String(g.label ?? ""), url: absUrl(g.href) })),
    contents: toc.map((t) => ({
      title: htmlToText(t.pageTitle),
      date: t.date || undefined,
      page: Number(t.intPageNumber ?? t.pageNumber),
      editorialPage: t.editorialPageNumber ? String(t.editorialPageNumber) : undefined,
      url: absUrl(`/paper-summary/${ref.slug}/${t.intPageNumber ?? t.pageNumber}`),
    })),
  };
}

export function formatDocumentPages(p: Awaited<ReturnType<typeof getDocumentPages>>): string {
  const out = [`# ${p.title}: pages and contents`, `- **URL:** ${p.url}`, `- **Images/pages:** ${p.numberOfPages}`];
  if (p.contents.length) {
    out.push("", "## Contents (entry → image page)");
    for (const c of p.contents) {
      out.push(`- ${c.title}${c.date && !c.title.includes(c.date) ? ` (${c.date})` : ""} → page ${c.page}${c.editorialPage ? ` [p. ${c.editorialPage}]` : ""}`);
    }
  }
  if (p.pages.length) {
    out.push("", "## Pages (image page number: label)", "");
    out.push(p.pages.map((g) => `${g.page}: ${g.label}`).join(" · "));
    out.push("", `Page URL pattern: ${p.url.replace(/\/1$/, "/{page}")}`);
  }
  return out.join("\n");
}

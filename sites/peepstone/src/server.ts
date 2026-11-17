/** Peepstone tool definitions, shared by the HTTP (Vercel) and stdio entry points. */
import type { McpServer } from "@modelcontextprotocol/server";
import { z } from "zod";
import { run } from "./format";
import { IMAGE_BASE, absUrl, canonicalPath, getPageData, toPath } from "./jsp/client";
import { citation } from "./jsp/cite";
import {
  formatDocument,
  formatDocumentPages,
  getDocument,
  getDocumentPages,
  type DocumentSection,
} from "./jsp/document";
import { formatEntity, getEntity, type EntityKind } from "./jsp/entities";
import { htmlToText } from "./jsp/html";
import { browsePapers, formatCalendar, getArticle, getCalendar, readJspUrl } from "./jsp/pages";
import { SEARCH_TYPE_NAMES, formatSearch, search } from "./jsp/search";

export const SERVER_INFO = { name: "peepstone", version: "0.1.0" };

export const INSTRUCTIONS = `Peepstone searches and reads The Joseph Smith Papers (https://www.josephsmithpapers.org): Joseph Smith's journals, letters, revelations, histories, minutes and legal/financial records, with the project's transcriptions, footnotes, source notes and historical introductions, plus its biographical and geographical directories, glossary, timeline of events and calendar of documents.

How to use it:
- Start with \`search\`. Narrow it with \`types\`, dates, and the people, places and subjects facet names that every search returns.
- Read a document page with \`get_document\`. Page through it with \`get_document_pages\`, or with the previous/next URLs it returns.
- Look up people, places, glossary terms and events with \`get_person\`, \`get_place\`, \`get_glossary_term\` and \`get_event\`. Each accepts a name, slug or URL.
- For chronology, use \`get_calendar\` (every known document by date). For the series and volume structure, use \`browse_papers\`.
- \`fetch_jsp_url\` reads any other josephsmithpapers.org page.

Cite every claim drawn from the papers with the josephsmithpapers.org URL the tool returned (a "Cite as" line is provided). Quote transcriptions exactly as given. JSP keeps original spelling, and its editorial insertions appear in [brackets].`;

const readOnly = { readOnlyHint: true, openWorldHint: true, idempotentHint: true } as const;

const offset = z
  .number()
  .int()
  .min(0)
  .optional()
  .describe("Character offset for reading long results; use the value given in a truncation note.");

const entityInput = (what: string, example: string) =>
  z.object({
    query: z
      .string()
      .min(1)
      .describe(`${what} name, JSP slug or URL, e.g. ${example}. Names are resolved with the site search.`),
    related_limit: z
      .number()
      .int()
      .min(0)
      .max(500)
      .optional()
      .describe("Max related documents/entries to list per group (default 25)."),
    offset,
  });

export function registerTools(server: McpServer) {
  server.registerTool(
    "search",
    {
      title: "Search the Joseph Smith Papers",
      description:
        "Full-text search across the entire Joseph Smith Papers site: document transcriptions and footnotes, people, places, glossary, events and reference material. It returns ranked hits with highlighted snippets and URLs, plus facets (types, people, places and subjects, with counts) whose names can be passed back to refine the search.",
      inputSchema: z.object({
        query: z.string().min(1).describe("Search words or phrase, e.g. \"Kirtland Temple\" or \"gift of tongues\"."),
        types: z
          .array(z.enum(SEARCH_TYPE_NAMES))
          .optional()
          .describe(
            "Restrict to content types. Document subtypes: papers (all), administrative, documents, legal, financial, histories, journals, revelations-and-translations, introductions, other-contemporary-papers. Other types: reference, people, places, glossary, events.",
          ),
        people: z
          .array(z.string())
          .optional()
          .describe("Only results tagged with all of these people, by name exactly as listed in search facets, e.g. \"Hyrum Smith\"."),
        places: z
          .array(z.string())
          .optional()
          .describe("Only results tagged with these places, by facet name, e.g. \"Nauvoo, Illinois\" or \"Kirtland, Ohio\"."),
        subjects: z
          .array(z.string())
          .optional()
          .describe("Only results tagged with these subjects, by facet name, e.g. \"Nauvoo Legion\" or \"Twelve Apostles\"."),
        start_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/).optional().describe("Earliest document date (YYYY-MM-DD)."),
        end_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/).optional().describe("Latest document date (YYYY-MM-DD)."),
        transcripts_only: z.boolean().optional().describe("Match only document transcription text (not notes or reference entries)."),
        sort: z.enum(["relevance", "alphabetical", "date"]).optional().describe("Default: relevance."),
        page: z.number().int().min(1).optional().describe("Results page (default 1)."),
        per_page: z.number().int().min(1).max(50).optional().describe("Results per page, 1–50 (default 10)."),
      }),
      annotations: readOnly,
    },
    async (a) =>
      run(async () =>
        formatSearch(
          await search({
            query: a.query,
            types: a.types,
            people: a.people,
            places: a.places,
            subjects: a.subjects,
            startDate: a.start_date,
            endDate: a.end_date,
            transcriptsOnly: a.transcripts_only,
            sort: a.sort,
            page: a.page,
            perPage: a.per_page,
          }),
        ),
      ),
  );

  server.registerTool(
    "get_document",
    {
      title: "Read a document page",
      description:
        "Read one page of a Joseph Smith Papers document. Returns the transcription as Markdown, with footnotes, metadata, the page image URL, previous/next page URLs and a citation. Optionally includes the document's historical introduction, source note and other versions.",
      inputSchema: z.object({
        document: z
          .string()
          .min(1)
          .describe("Document slug or URL, e.g. \"journal-1835-1836\" or \"https://www.josephsmithpapers.org/paper-summary/journal-1835-1836/11\"."),
        page: z.number().int().min(1).optional().describe("Image page number (as in the URL). Overrides the page in the URL; default 1."),
        include: z
          .array(z.enum(["transcript", "footnotes", "sourceNote", "historicalIntro", "versions"]))
          .optional()
          .describe("Sections to return. Default: [\"transcript\", \"footnotes\"]. The historical intro and source note are the same on every page of a document."),
        text: z
          .enum(["clear", "expanded"])
          .optional()
          .describe("\"clear\" (default) is the reading text; \"expanded\" keeps deletions (~~struck~~), insertions and original line breaks."),
        offset,
      }),
      annotations: readOnly,
    },
    async (a) =>
      run(async () => {
        const d = await getDocument(a.document, { page: a.page, text: a.text });
        return formatDocument(d, (a.include as DocumentSection[] | undefined) ?? ["transcript", "footnotes"]);
      }, a.offset),
  );

  server.registerTool(
    "get_document_pages",
    {
      title: "List a document's pages",
      description:
        "Table of contents (e.g. journal entries by date) and the full page list for a document, mapping each entry to the image page number used by get_document.",
      inputSchema: z.object({
        document: z.string().min(1).describe("Document slug or URL, e.g. \"journal-1835-1836\"."),
        offset,
      }),
      annotations: readOnly,
    },
    async (a) => run(async () => formatDocumentPages(await getDocumentPages(a.document)), a.offset),
  );

  const entityTools: Array<[string, EntityKind, string, string, string]> = [
    ["get_person", "person", "Biographical directory entry", "Person", "\"Emma Hale Smith\", \"emma-hale-smith\""],
    ["get_place", "place", "Geographical directory entry", "Place", "\"Nauvoo, Illinois\", \"nauvoo-illinois\""],
    ["get_glossary_term", "topic", "Glossary entry", "Glossary term", "\"Nauvoo Legion\", \"nauvoo-legion\""],
    ["get_event", "event", "Timeline event", "Event", "\"Reorganization of Nauvoo House Association\""],
  ];
  for (const [name, kind, title, what, example] of entityTools) {
    server.registerTool(
      name,
      {
        title,
        description: `${title} from the Joseph Smith Papers: the full description with notes, alternate names, dates${kind === "place" ? ", coordinates" : ""}, images and the documents that mention it.`,
        inputSchema: entityInput(what, example),
        annotations: readOnly,
      },
      async (a) => run(async () => formatEntity(await getEntity(kind, a.query, a.related_limit ?? 25)), a.offset),
    );
  }

  server.registerTool(
    "get_calendar",
    {
      title: "Calendar of Documents",
      description:
        "The JSP Calendar of Documents: every known Joseph Smith document (1825–1844) for a date range, with its versions and links. Useful for asking what was written or dictated on a given date.",
      inputSchema: z.object({
        start_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/).describe("Start date (YYYY-MM-DD)."),
        end_date: z
          .string()
          .regex(/^\d{4}-\d{2}-\d{2}$/)
          .optional()
          .describe("End date (YYYY-MM-DD). Default: end of the start date's month."),
        keywords: z.string().optional().describe("Optional keyword filter."),
        offset: z.number().int().min(0).optional().describe("Entry offset for paging (default 0)."),
        limit: z.number().int().min(1).max(200).optional().describe("Entries per call (default 50)."),
      }),
      annotations: readOnly,
    },
    async (a) =>
      run(async () => {
        const p = { startDate: a.start_date, endDate: a.end_date, keywords: a.keywords };
        return formatCalendar(await getCalendar(p), p, a.offset ?? 0, a.limit ?? 50);
      }),
  );

  server.registerTool(
    "browse_papers",
    {
      title: "Browse the papers",
      description:
        "Browse the papers by series and volume, as on josephsmithpapers.org/the-papers. Empty path = top-level series (Documents, Journals, Administrative Records, Revelations and Translations, Histories, Legal/Business/Financial, Other Contemporary Papers). Pass a returned path such as \"journals\" or \"journals/jsppj1\" to go deeper.",
      inputSchema: z.object({
        path: z.string().optional().describe("Path under /the-papers, e.g. \"documents/jsppd1\". Empty for the top level."),
        offset,
      }),
      annotations: readOnly,
    },
    async (a) => run(() => browsePapers(a.path ?? ""), a.offset),
  );

  server.registerTool(
    "get_article",
    {
      title: "Read an article or introduction",
      description:
        "Read a JSP editorial article, series or volume introduction, or reference essay: pages under /articles/, /intro/, /doc/ and /back/ (for example organizational charts such as Nauvoo City Officers).",
      inputSchema: z.object({
        article: z.string().min(1).describe("Article URL or path, e.g. \"/articles/introduction-to-calendar-of-documents\" or \"/back/nauvoo-city-officers-1841-1844\". A bare slug is treated as /articles/{slug}."),
        offset,
      }),
      annotations: readOnly,
    },
    async (a) => run(() => getArticle(a.article), a.offset),
  );

  server.registerTool(
    "cite_page",
    {
      title: "Cite a JSP page",
      description: "Build a citation in the Joseph Smith Papers' own format (title, page, “The Joseph Smith Papers”, accessed date, URL) for any josephsmithpapers.org page.",
      inputSchema: z.object({ url: z.string().min(1).describe("josephsmithpapers.org URL or path.") }),
      annotations: readOnly,
    },
    async (a) =>
      run(async () => {
        const path = canonicalPath(toPath(a.url));
        if (path.startsWith("/paper-summary/")) return (await getDocument(path)).citation;
        const { pageProps } = await getPageData(path);
        const kind = (["person", "place", "topic", "event"] as const).find((k) => pageProps[k]);
        const title =
          (kind && htmlToText(pageProps[kind]?.authority?.refObject?.docDesc)) ||
          htmlToText(pageProps.articleData?.title) ||
          htmlToText(pageProps.summary?.title) ||
          htmlToText(pageProps.pageTitle) ||
          path;
        return citation({ title, url: absUrl(path) });
      }),
  );

  server.registerTool(
    "get_page_image",
    {
      title: "Get manuscript image URLs",
      description: "Image URLs for a document page: thumbnail, medium, large and download sizes, plus the Deep Zoom descriptor. The images are not downloaded.",
      inputSchema: z.object({
        document: z.string().min(1).describe("Document slug or URL."),
        page: z.number().int().min(1).optional().describe("Image page number (default 1, or the page in the URL)."),
      }),
      annotations: readOnly,
    },
    async (a) =>
      run(async () => {
        const d = await getDocument(a.document, { page: a.page });
        if (!d.images) return `No image is available for ${d.url}.`;
        const lines = [`# Images: ${d.title}, image ${d.page} of ${d.numberOfPages}`, `- **Page:** ${d.url}`];
        for (const [k, v] of Object.entries(d.images)) if (v) lines.push(`- **${k}:** ${v}`);
        lines.push("", `Image base: ${IMAGE_BASE}`);
        return lines.join("\n");
      }),
  );

  server.registerTool(
    "fetch_jsp_url",
    {
      title: "Read any JSP page",
      description:
        "Read any josephsmithpapers.org page as Markdown: documents, people, places, glossary, events, articles, browse pages, reference directories (e.g. /reference/people?filter=b), media and news. Use it for links returned by other tools, or for pages that no other tool covers.",
      inputSchema: z.object({
        url: z.string().min(1).describe("josephsmithpapers.org URL or path, e.g. \"/topic/nauvoo-legion\"."),
        offset,
      }),
      annotations: readOnly,
    },
    async (a) => run(() => readJspUrl(a.url), a.offset),
  );
}

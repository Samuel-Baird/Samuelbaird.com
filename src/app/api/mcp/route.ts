import { createMcpHandler } from "mcp-handler";
import { z } from "zod";
import {
  getChannelsWithLatest,
  getChannelBySlug,
  getChannelStatsHistory,
  getStudies,
  getStudyBySlug,
  getAllStudyTags,
  getAllClaimTopicTags,
  getClaimBySlug,
  getPublishedClaims,
} from "@/lib/data";
import { TIMELINES } from "@/app/timelines/registry";
import eternalIncreaseSources from "@/app/eternal-increase-timeline/sources.json";

// Loosely typed to the documented shape (docs/timelines/SCHEMA.md) rather
// than inferred from the JSON literal — the per-entry inferred union from
// `typeof sources[number]` doesn't unify cleanly across entries with
// different optional fields.
type Quote = {
  quoteId: string;
  categories: string[];
  excerpt: string;
  referent?: string;
};
type SourceEntry = {
  id: string;
  date: string;
  title: string;
  speaker: string;
  hearsay: string;
  referent: string;
  quotes: Quote[];
};

// Timelines are static content bundled with the site (not database rows).
// Extend this map when a new timeline is added to the registry. A timeline
// still in preparation belongs here with an empty array rather than being left
// out: it is listed by list_timelines either way, and an omission would make
// get_timeline_sources throw "unknown timeline" for a timeline that does exist.
const TIMELINE_SOURCES: Record<string, SourceEntry[]> = {
  "/eternal-increase-timeline": eternalIncreaseSources as SourceEntry[],
  "/family-proclamation-timeline": [],
  "/baptism-timeline": [],
  "/sacrament-timeline": [],
};

function channelTags(c: { channel_types: string[]; channel_type: string | null }) {
  return c.channel_types?.length ? c.channel_types : c.channel_type ? [c.channel_type] : [];
}

function findTimeline(href: string) {
  const meta = TIMELINES.find((t) => t.href === href);
  const sources = TIMELINE_SOURCES[href];
  if (!meta || !sources) {
    const known = TIMELINES.map((t) => t.href).join(", ");
    throw new Error(`Unknown timeline "${href}". Known timelines: ${known}`);
  }
  return { meta, sources };
}

const handler = createMcpHandler(
  (server) => {
    server.registerTool(
      "list_channels",
      {
        title: "List channels",
        description:
          "List LDS-related YouTube channels tracked by Latter-day Stats (faith-affiliated, cultural, news, education, etc). Critical-of-the-Church channels are always excluded.",
        inputSchema: z.object({
          search: z.string().optional().describe("Case-insensitive substring match on channel name."),
          type: z.string().optional().describe('Filter by channel type/tag, e.g. "Church", "BYU", "Music", "Apologetics". See list_channel_types.'),
          country: z.string().optional().describe("Exact match on the channel's country."),
          featuredOnly: z.boolean().optional(),
          minSubscribers: z.number().int().nonnegative().optional(),
          sort: z.enum(["subscribers", "name", "newest"]).optional().describe("Default: subscribers (descending)."),
          limit: z.number().int().positive().max(500).optional().describe("Default 50, max 500."),
        }),
      },
      async (args) => {
        let rows = (await getChannelsWithLatest({ includeCritical: false })).map((c) => ({
          slug: c.slug,
          youtube_channel_id: c.youtube_channel_id,
          name: c.name,
          description: c.description,
          channel_type: c.channel_type,
          channel_types: c.channel_types,
          country: c.country_manual ?? c.country ?? null,
          language: c.language_manual ?? c.language ?? null,
          handle: c.handle,
          featured: c.featured,
          created_at_youtube: c.created_at_youtube,
          subscribers: c.latest?.subscribers ?? null,
          total_views: c.latest?.total_views ?? null,
          video_count: c.latest?.video_count ?? null,
          stats_captured_at: c.latest?.captured_at ?? null,
        }));

        if (args.search) {
          const needle = args.search.toLowerCase();
          rows = rows.filter((r) => r.name.toLowerCase().includes(needle));
        }
        if (args.type) rows = rows.filter((r) => r.channel_types.includes(args.type!));
        if (args.country) {
          const wanted = args.country.toLowerCase();
          rows = rows.filter((r) => (r.country ?? "").toLowerCase() === wanted);
        }
        if (args.featuredOnly) rows = rows.filter((r) => r.featured);
        if (args.minSubscribers != null) {
          rows = rows.filter((r) => (r.subscribers ?? 0) >= args.minSubscribers!);
        }

        const sort = args.sort ?? "subscribers";
        rows.sort((a, b) => {
          if (sort === "name") return a.name.localeCompare(b.name);
          if (sort === "newest") {
            return (
              new Date(b.created_at_youtube ?? 0).getTime() -
              new Date(a.created_at_youtube ?? 0).getTime()
            );
          }
          return (b.subscribers ?? 0) - (a.subscribers ?? 0);
        });

        const limit = Math.min(args.limit ?? 50, 500);
        return {
          content: [
            { type: "text", text: JSON.stringify(rows.slice(0, limit), null, 2) },
          ],
        };
      },
    );

    server.registerTool(
      "get_channel",
      {
        title: "Get channel",
        description:
          "Get one channel's full detail plus its subscriber/view history over time. Provide slug or youtubeChannelId. Returns null if not found or if the channel is Critical-tagged.",
        inputSchema: z.object({
          slug: z.string().optional(),
          youtubeChannelId: z.string().optional(),
        }),
      },
      async ({ slug, youtubeChannelId }) => {
        const key = slug ?? youtubeChannelId;
        if (!key) throw new Error("Provide either slug or youtubeChannelId.");
        const channel = await getChannelBySlug(key);
        if (!channel || channelTags(channel).includes("Critical")) {
          return { content: [{ type: "text", text: "null" }] };
        }
        const history = await getChannelStatsHistory(channel.id);
        return {
          content: [
            { type: "text", text: JSON.stringify({ ...channel, stats_history: history }, null, 2) },
          ],
        };
      },
    );

    server.registerTool(
      "list_channel_types",
      {
        title: "List channel types",
        description: "List the distinct channel type/tag values in use (excluding Critical), for use with list_channels' `type` filter.",
        inputSchema: z.object({}),
      },
      async () => {
        const channels = await getChannelsWithLatest({ includeCritical: false });
        const set = new Set<string>();
        for (const c of channels) for (const t of channelTags(c)) set.add(t);
        return { content: [{ type: "text", text: JSON.stringify([...set].sort(), null, 2) }] };
      },
    );

    server.registerTool(
      "list_studies",
      {
        title: "List studies",
        description:
          "List/search research studies and analyses in the Latter-day Stats library (surveys, academic papers, articles about Latter-day Saint demographics, belief, and culture).",
        inputSchema: z.object({
          search: z.string().optional().describe('Full-text search over title/abstract (websearch syntax, e.g. "faith AND retention").'),
          tags: z.array(z.string()).optional().describe("Studies must contain all of these tags."),
          sort: z.enum(["categories", "year", "upvotes"]).optional().describe("Default: year (descending)."),
          limit: z.number().int().positive().max(500).optional().describe("Default 50, max 500."),
        }),
      },
      async (args) => {
        const studies = await getStudies({ query: args.search, tags: args.tags, sort: args.sort });
        const limit = Math.min(args.limit ?? 50, 500);
        return { content: [{ type: "text", text: JSON.stringify(studies.slice(0, limit), null, 2) }] };
      },
    );

    server.registerTool(
      "get_study",
      {
        title: "Get study",
        description: "Get one study's full detail by slug, including findings, limitations, and source links.",
        inputSchema: z.object({ slug: z.string() }),
      },
      async ({ slug }) => {
        const study = await getStudyBySlug(slug);
        return { content: [{ type: "text", text: JSON.stringify(study, null, 2) }] };
      },
    );

    server.registerTool(
      "list_study_tags",
      {
        title: "List study tags",
        description: "List all study tags in use with their counts, for use with list_studies' `tags` filter.",
        inputSchema: z.object({}),
      },
      async () => {
        const tags = await getAllStudyTags();
        return { content: [{ type: "text", text: JSON.stringify(tags, null, 2) }] };
      },
    );

    // Claim library. Published claims only — drafts and the occurrence
    // mapping (which names the critical videos making each claim) are
    // apologist-only and never reach this surface.
    server.registerTool(
      "list_claims",
      {
        title: "List claims",
        description:
          "List/search the Latter-day Stats claim library: common criticisms of the Church of Jesus Christ of Latter-day Saints, each stated at its strongest and answered from cited primary sources.",
        inputSchema: z.object({
          search: z.string().optional().describe('Full-text search over the claim and response (websearch syntax, e.g. "seer stone").'),
          tags: z.array(z.string()).optional().describe("Claims must carry all of these topic tags. See list_claim_topics."),
          sort: z.enum(["recent", "title"]).optional().describe("Default: recent (most recently published first)."),
          limit: z.number().int().positive().max(200).optional().describe("Default 25, max 200."),
        }),
      },
      async (args) => {
        const claims = await getPublishedClaims({
          query: args.search,
          tags: args.tags,
          sort: args.sort,
        });
        const limit = Math.min(args.limit ?? 25, 200);
        // Trimmed shape: the full response text can be long, and callers
        // fetching a list usually want to pick one and call get_claim.
        const rows = claims.slice(0, limit).map((c) => ({
          slug: c.slug,
          title: c.title,
          claim_text: c.claim_text,
          topic_tags: c.topic_tags,
          source_count: c.sources.length,
          published_at: c.published_at,
        }));
        return { content: [{ type: "text", text: JSON.stringify(rows, null, 2) }] };
      },
    );

    server.registerTool(
      "get_claim",
      {
        title: "Get claim",
        description:
          "Get one claim's full detail by slug: the claim as critics state it, the sourced response, and every citation behind it.",
        inputSchema: z.object({ slug: z.string() }),
      },
      async ({ slug }) => {
        const claim = await getClaimBySlug(slug);
        return { content: [{ type: "text", text: JSON.stringify(claim, null, 2) }] };
      },
    );

    server.registerTool(
      "list_claim_topics",
      {
        title: "List claim topics",
        description: "List the topic tags used in the claim library with their counts, for use with list_claims' `tags` filter.",
        inputSchema: z.object({}),
      },
      async () => {
        const tags = await getAllClaimTopicTags();
        return { content: [{ type: "text", text: JSON.stringify(tags, null, 2) }] };
      },
    );

    server.registerTool(
      "list_timelines",
      {
        title: "List timelines",
        description:
          "List the site's sourced doctrinal/historical timelines (e.g. the eternal-increase timeline), each a graded, cited chronology of primary sources on one question.",
        inputSchema: z.object({}),
      },
      async () => {
        return { content: [{ type: "text", text: JSON.stringify(TIMELINES, null, 2) }] };
      },
    );

    server.registerTool(
      "get_timeline_sources",
      {
        title: "Get timeline sources",
        description:
          "Get the sourced entries in a timeline, with filters. Each entry is a graded primary/citing source (speaker, date, hearsay grade A-E, correlation status, quotes with category tags).",
        inputSchema: z.object({
          href: z.string().describe('Timeline href from list_timelines, e.g. "/eternal-increase-timeline".'),
          referent: z.enum(["father", "son", "ambiguous", "n/a"]).optional().describe("Who the claim is about."),
          category: z.string().optional().describe('A quote category tag, e.g. "FATHER-BECAME-GOD". See list_timeline_categories.'),
          hearsay: z.enum(["A", "B", "C", "D", "E"]).optional().describe("Source-level provenance grade."),
          yearFrom: z.number().int().optional(),
          yearTo: z.number().int().optional(),
          search: z.string().optional().describe("Case-insensitive substring match over title, speaker, and quote text."),
          limit: z.number().int().positive().max(300).optional().describe("Default 50, max 300."),
        }),
      },
      async (args) => {
        const { meta, sources } = findTimeline(args.href);
        let rows: SourceEntry[] = sources;

        if (args.referent) {
          rows = rows.filter(
            (s) => s.referent === args.referent || s.quotes?.some((q: Quote) => q.referent === args.referent),
          );
        }
        if (args.hearsay) rows = rows.filter((s) => s.hearsay === args.hearsay);
        if (args.category) {
          const wanted = args.category.toUpperCase();
          rows = rows.filter((s) => s.quotes?.some((q: Quote) => q.categories?.includes(wanted)));
        }
        if (args.yearFrom != null) rows = rows.filter((s) => Number(s.date.slice(0, 4)) >= args.yearFrom!);
        if (args.yearTo != null) rows = rows.filter((s) => Number(s.date.slice(0, 4)) <= args.yearTo!);
        if (args.search) {
          const needle = args.search.toLowerCase();
          rows = rows.filter(
            (s) =>
              s.title.toLowerCase().includes(needle) ||
              s.speaker.toLowerCase().includes(needle) ||
              s.quotes?.some((q: Quote) => q.excerpt.toLowerCase().includes(needle)),
          );
        }

        rows = [...rows].sort((a, b) => a.date.localeCompare(b.date));
        const limit = Math.min(args.limit ?? 50, 300);
        const result = {
          timeline: { href: meta.href, title: meta.title },
          total: rows.length,
          returned: Math.min(rows.length, limit),
          sources: rows.slice(0, limit),
        };
        return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
      },
    );

    server.registerTool(
      "list_timeline_categories",
      {
        title: "List timeline categories",
        description: "List the quote category tags used within one timeline, for use with get_timeline_sources' `category` filter.",
        inputSchema: z.object({
          href: z.string().describe("Timeline href from list_timelines."),
        }),
      },
      async ({ href }) => {
        const { sources } = findTimeline(href);
        const set = new Set<string>();
        for (const s of sources) {
          for (const q of s.quotes ?? []) for (const c of q.categories ?? []) set.add(c);
        }
        return { content: [{ type: "text", text: JSON.stringify([...set].sort(), null, 2) }] };
      },
    );
  },
  {
    serverInfo: { name: "latter-day-stats", version: "0.1.0" },
  },
);

export { handler as GET, handler as POST };

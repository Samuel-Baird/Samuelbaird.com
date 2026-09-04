import { createMcpHandler } from "mcp-handler";
import { z } from "zod";
import {
  getChannelsWithLatest,
  getChannelBySlug,
  getChannelStatsHistory,
  getStudies,
  getStudyBySlug,
  getAllStudyTags,
} from "@/lib/data";
import { DATASETS, getDataset, categorySlug } from "@/lib/data-explorer";

function channelTags(c: { channel_types: string[]; channel_type: string | null }) {
  return c.channel_types?.length ? c.channel_types : c.channel_type ? [c.channel_type] : [];
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

    // Data Explorer: survey/compiled datasets (Pew, Ryan Burge, membership
    // history, etc), each with its own set of rendered chart graphics.
    server.registerTool(
      "list_datasets",
      {
        title: "List Data Explorer datasets",
        description:
          "List/search the Data Explorer's datasets: surveys and compiled data series on Latter-day Saint demographics, belief, and culture, each with rendered chart graphics.",
        inputSchema: z.object({
          search: z.string().optional().describe("Case-insensitive substring match on dataset name/description."),
          category: z.string().optional().describe('Filter by category slug, e.g. "mixed-datasets". See list_dataset_categories.'),
          limit: z.number().int().positive().max(200).optional().describe("Default 50, max 200."),
        }),
      },
      async (args) => {
        let rows = DATASETS.map((d) => ({
          slug: d.slug,
          name: d.name,
          shortDescription: d.shortDescription,
          sponsor: d.sponsor,
          fielder: d.fielder,
          fieldedPeriod: d.fieldedPeriod,
          category: d.category ?? null,
          graphic_count: d.graphics.length,
        }));

        if (args.search) {
          const needle = args.search.toLowerCase();
          rows = rows.filter(
            (r) =>
              r.name.toLowerCase().includes(needle) ||
              r.shortDescription.toLowerCase().includes(needle),
          );
        }
        if (args.category) {
          rows = rows.filter((r) => r.category && categorySlug(r.category) === args.category);
        }

        const limit = Math.min(args.limit ?? 50, 200);
        return { content: [{ type: "text", text: JSON.stringify(rows.slice(0, limit), null, 2) }] };
      },
    );

    server.registerTool(
      "get_dataset",
      {
        title: "Get Data Explorer dataset",
        description:
          "Get one Data Explorer dataset's full detail by slug: description, methodology, citation, and its list of chart graphics (title/description/alt text per graphic).",
        inputSchema: z.object({ slug: z.string() }),
      },
      async ({ slug }) => {
        const dataset = getDataset(slug);
        if (!dataset) return { content: [{ type: "text", text: "null" }] };
        const result = {
          slug: dataset.slug,
          name: dataset.name,
          shortDescription: dataset.shortDescription,
          sponsor: dataset.sponsor,
          fielder: dataset.fielder,
          fieldedPeriod: dataset.fieldedPeriod,
          description: dataset.description,
          methodology: dataset.methodology ?? null,
          citation: dataset.citation ?? null,
          doi: dataset.doi ?? null,
          sourceUrl: dataset.sourceUrl ?? null,
          category: dataset.category ?? null,
          graphics: dataset.graphics.map((g) => ({
            title: g.title,
            description: g.description,
            alt: g.alt,
          })),
        };
        return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
      },
    );

    server.registerTool(
      "list_dataset_categories",
      {
        title: "List Data Explorer dataset categories",
        description: "List the Data Explorer's dataset category labels and slugs, for use with list_datasets' `category` filter.",
        inputSchema: z.object({}),
      },
      async () => {
        const seen = new Map<string, string>();
        for (const d of DATASETS) {
          if (d.category) seen.set(categorySlug(d.category), d.category);
        }
        const rows = [...seen.entries()].map(([slug, label]) => ({ slug, label }));
        return { content: [{ type: "text", text: JSON.stringify(rows, null, 2) }] };
      },
    );
  },
  {
    serverInfo: { name: "latter-day-stats", version: "0.1.0" },
  },
);

export { handler as GET, handler as POST };

#!/usr/bin/env node
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { listChannels, getChannel, listChannelTypes } from "./channels.js";
import { listStudies, getStudy, listStudyTags } from "./studies.js";
import {
  listTimelines,
  getTimelineSources,
  listTimelineCategories,
} from "./timelines.js";

const server = new McpServer({
  name: "latter-day-stats",
  version: "0.1.0",
});

function json(data: unknown) {
  return { content: [{ type: "text" as const, text: JSON.stringify(data, null, 2) }] };
}

// ---------------------------------------------------------------------------
// Channels — always excludes channels tagged "Critical" (critical-of-the-
// Church commentary channels), matching the site's faithful-view filter.
// ---------------------------------------------------------------------------

server.registerTool(
  "list_channels",
  {
    title: "List channels",
    description:
      "List LDS-related YouTube channels tracked by Latter-day Stats (faith-affiliated, cultural, news, education, etc). Critical-of-the-Church channels are always excluded.",
    inputSchema: {
      search: z.string().optional().describe("Case-insensitive substring match on channel name."),
      type: z.string().optional().describe("Filter by channel type/tag, e.g. \"Church\", \"BYU\", \"Music\", \"Apologetics\". See list_channel_types."),
      country: z.string().optional().describe("Exact match on the channel's country."),
      featuredOnly: z.boolean().optional(),
      minSubscribers: z.number().int().nonnegative().optional(),
      sort: z.enum(["subscribers", "name", "newest"]).optional().describe("Default: subscribers (descending)."),
      limit: z.number().int().positive().max(500).optional().describe("Default 50, max 500."),
    },
  },
  async (args) => json(await listChannels(args)),
);

server.registerTool(
  "get_channel",
  {
    title: "Get channel",
    description:
      "Get one channel's full detail plus its subscriber/view history over time. Provide slug or youtubeChannelId. Returns null if not found or if the channel is Critical-tagged.",
    inputSchema: {
      slug: z.string().optional(),
      youtubeChannelId: z.string().optional(),
    },
  },
  async (args) => json(await getChannel(args)),
);

server.registerTool(
  "list_channel_types",
  {
    title: "List channel types",
    description: "List the distinct channel type/tag values in use (excluding Critical), for use with list_channels' `type` filter.",
    inputSchema: {},
  },
  async () => json(await listChannelTypes()),
);

// ---------------------------------------------------------------------------
// Studies
// ---------------------------------------------------------------------------

server.registerTool(
  "list_studies",
  {
    title: "List studies",
    description:
      "List/search research studies and analyses in the Latter-day Stats library (surveys, academic papers, articles about Latter-day Saint demographics, belief, and culture).",
    inputSchema: {
      search: z.string().optional().describe("Full-text search over title/abstract (websearch syntax, e.g. \"faith AND retention\")."),
      tags: z.array(z.string()).optional().describe("Studies must contain all of these tags."),
      year: z.number().int().optional(),
      category: z.string().optional(),
      sourceType: z.string().optional(),
      sort: z.enum(["year", "title"]).optional().describe("Default: year (descending)."),
      limit: z.number().int().positive().max(500).optional().describe("Default 50, max 500."),
    },
  },
  async (args) => json(await listStudies(args)),
);

server.registerTool(
  "get_study",
  {
    title: "Get study",
    description: "Get one study's full detail by slug, including findings, limitations, and source links.",
    inputSchema: {
      slug: z.string(),
    },
  },
  async ({ slug }) => json(await getStudy(slug)),
);

server.registerTool(
  "list_study_tags",
  {
    title: "List study tags",
    description: "List all study tags in use with their counts, for use with list_studies' `tags` filter.",
    inputSchema: {},
  },
  async () => json(await listStudyTags()),
);

// ---------------------------------------------------------------------------
// Timelines
// ---------------------------------------------------------------------------

server.registerTool(
  "list_timelines",
  {
    title: "List timelines",
    description:
      "List the site's sourced doctrinal/historical timelines (e.g. the eternal-increase timeline), each a graded, cited chronology of primary sources on one question.",
    inputSchema: {},
  },
  async () => json(await listTimelines()),
);

server.registerTool(
  "get_timeline_sources",
  {
    title: "Get timeline sources",
    description:
      "Get the sourced entries in a timeline, with filters. Each entry is a graded primary/citing source (speaker, date, hearsay grade A-E, correlation status, quotes with category tags).",
    inputSchema: {
      href: z.string().describe("Timeline href from list_timelines, e.g. \"/eternal-increase-timeline\"."),
      referent: z.enum(["father", "son", "ambiguous", "n/a"]).optional().describe("Who the claim is about."),
      category: z.string().optional().describe("A quote category tag, e.g. \"FATHER-BECAME-GOD\". See list_timeline_categories."),
      hearsay: z.enum(["A", "B", "C", "D", "E"]).optional().describe("Source-level provenance grade."),
      yearFrom: z.number().int().optional(),
      yearTo: z.number().int().optional(),
      search: z.string().optional().describe("Case-insensitive substring match over title, speaker, and quote text."),
      limit: z.number().int().positive().max(300).optional().describe("Default 50, max 300."),
    },
  },
  async (args) => json(await getTimelineSources(args)),
);

server.registerTool(
  "list_timeline_categories",
  {
    title: "List timeline categories",
    description: "List the quote category tags used within one timeline, for use with get_timeline_sources' `category` filter.",
    inputSchema: {
      href: z.string().describe("Timeline href from list_timelines."),
    },
  },
  async ({ href }) => json(await listTimelineCategories(href)),
);

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((err) => {
  console.error("Fatal error starting latter-day-stats MCP server:", err);
  process.exit(1);
});

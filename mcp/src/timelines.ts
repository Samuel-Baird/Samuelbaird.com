import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

// mcp/src (dev, via tsx) or mcp/dist (built) -> repo root is two levels up.
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, "..", "..");

// Mirrors src/app/timelines/registry.ts. Timelines are static content
// bundled with the site, not database rows, so this server reads the same
// sources.json files straight from the repo checkout. Keep this list in
// sync with the registry when a new timeline is added there.
const TIMELINE_REGISTRY = [
  {
    href: "/eternal-increase-timeline",
    title: "Eternal regress & eternal increase",
    question:
      "Whether God the Father had a Father, whether exalted humans become parents of spirits, how spirit birth was described, and how those teachings were reframed in correlated materials.",
    jsonPath: "src/app/eternal-increase-timeline/sources.json",
    status: "Working draft",
  },
] as const;

type SourceEntry = {
  id: string;
  date: string;
  dateDisplay: string;
  title: string;
  speaker: string;
  office: string;
  venue: string;
  url: string;
  hearsay: string;
  correlationStatus: string;
  referent: string;
  sourceType: string;
  quotes: { quoteId: string; categories: string[]; excerpt: string }[];
  [key: string]: unknown;
};

const cache = new Map<string, SourceEntry[]>();

async function loadSources(jsonPath: string): Promise<SourceEntry[]> {
  const cached = cache.get(jsonPath);
  if (cached) return cached;
  const raw = await readFile(path.join(REPO_ROOT, jsonPath), "utf8");
  const parsed = JSON.parse(raw) as SourceEntry[];
  cache.set(jsonPath, parsed);
  return parsed;
}

function findTimeline(href: string) {
  const entry = TIMELINE_REGISTRY.find((t) => t.href === href);
  if (!entry) {
    const known = TIMELINE_REGISTRY.map((t) => t.href).join(", ");
    throw new Error(`Unknown timeline "${href}". Known timelines: ${known}`);
  }
  return entry;
}

export async function listTimelines() {
  return Promise.all(
    TIMELINE_REGISTRY.map(async (t) => {
      const sources = await loadSources(t.jsonPath);
      const years = sources.map((s) => Number(s.date.slice(0, 4)));
      return {
        href: t.href,
        title: t.title,
        question: t.question,
        status: t.status,
        span: `${Math.min(...years)}–${Math.max(...years)}`,
        sourceCount: sources.length,
      };
    }),
  );
}

export async function getTimelineSources(opts: {
  href: string;
  referent?: string;
  category?: string;
  hearsay?: string;
  yearFrom?: number;
  yearTo?: number;
  search?: string;
  limit?: number;
}) {
  const timeline = findTimeline(opts.href);
  const sources = await loadSources(timeline.jsonPath);

  let rows = sources;

  if (opts.referent) {
    rows = rows.filter(
      (s) =>
        s.referent === opts.referent ||
        s.quotes?.some((q: any) => q.referent === opts.referent),
    );
  }
  if (opts.hearsay) {
    rows = rows.filter((s) => s.hearsay === opts.hearsay);
  }
  if (opts.category) {
    const wanted = opts.category.toUpperCase();
    rows = rows.filter((s) =>
      s.quotes?.some((q) => q.categories?.includes(wanted)),
    );
  }
  if (opts.yearFrom != null) {
    rows = rows.filter((s) => Number(s.date.slice(0, 4)) >= opts.yearFrom!);
  }
  if (opts.yearTo != null) {
    rows = rows.filter((s) => Number(s.date.slice(0, 4)) <= opts.yearTo!);
  }
  if (opts.search) {
    const needle = opts.search.toLowerCase();
    rows = rows.filter(
      (s) =>
        s.title.toLowerCase().includes(needle) ||
        s.speaker.toLowerCase().includes(needle) ||
        s.quotes?.some((q) => q.excerpt.toLowerCase().includes(needle)),
    );
  }

  rows = [...rows].sort((a, b) => a.date.localeCompare(b.date));

  const limit = Math.min(opts.limit ?? 50, 300);
  return {
    timeline: { href: timeline.href, title: timeline.title },
    total: rows.length,
    returned: Math.min(rows.length, limit),
    sources: rows.slice(0, limit),
  };
}

export async function listTimelineCategories(href: string): Promise<string[]> {
  const timeline = findTimeline(href);
  const sources = await loadSources(timeline.jsonPath);
  const set = new Set<string>();
  for (const s of sources) {
    for (const q of s.quotes ?? []) {
      for (const c of q.categories ?? []) set.add(c);
    }
  }
  return [...set].sort();
}

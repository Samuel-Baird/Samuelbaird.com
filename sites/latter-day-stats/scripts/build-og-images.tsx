// Renders the Open Graph / social card images and the favicon to static PNGs
// before `next build` (package.json "build", which `opennextjs-cloudflare
// build` runs). Run by hand with `npx tsx scripts/build-og-images.tsx`.
//
// The site used to render these per request with next/og's ImageResponse;
// its satori + resvg wasm was ~0.7 MiB of the gzipped Worker, which has to
// fit the Workers free plan's 3 MiB. This script uses the same renderer
// (next/og under Node) and the same designs (src/lib/og.tsx), so the images
// look as before. Output (gitignored, rebuilt on every build/deploy):
//
//   public/og/{home,about,channels,contact,donate,methodology,studies}.png
//   public/og/channels/<slug>.png   one per channel (Supabase channel_full)
//   public/og/studies/<slug>.png    one per study   (Supabase studies)
//   public/icon.png                 32x32 favicon (committed; deterministic)
//
// Data is read with the public anon key (NEXT_PUBLIC_SUPABASE_URL /
// NEXT_PUBLIC_SUPABASE_ANON_KEY, from the environment or .env.local). Without
// them, or if Supabase fails, it still writes the fixed pages (without the
// live totals) and skips the per-channel/per-study cards: the metadata then
// points at missing files, and worker.ts serves the section image instead.
// So a build never fails because of this script; it warns loudly.
//
// Metadata URLs: src/lib/og-images.ts.

import { mkdir, rm, writeFile } from "node:fs/promises";
import path from "node:path";
import { ImageResponse } from "next/og";
import type { ReactElement } from "react";
import { createClient, type SupabaseClient } from "@supabase/supabase-js";
import { config as loadEnv } from "dotenv";
import { OgFrame, OG_ACCENT, OG_INK, OG_MUTED, OG_SIZE } from "../src/lib/og";
import { fmtCompact, fmtNumber } from "../src/lib/format";
import {
  BEEHIVE_BANDS,
  BEEHIVE_BARS,
  BEEHIVE_BAR_BASELINE,
  BEEHIVE_BAR_WIDTH,
} from "../src/lib/beehive-stats-mark";

const ROOT = path.resolve(__dirname, "..");
const PUBLIC = path.join(ROOT, "public");
const OUT = path.join(PUBLIC, "og");
const CONCURRENCY = 8;
const SAFE_SLUG = /^[A-Za-z0-9_-]+$/;

loadEnv({ path: path.join(ROOT, ".env.local"), quiet: true });

// ---------------------------------------------------------------- designs

const TITLE = {
  fontWeight: 700,
  color: OG_INK,
  lineHeight: 1.05,
  letterSpacing: "-0.02em",
} as const;
const SUBTITLE = {
  fontSize: 28,
  color: OG_MUTED,
  fontFamily: "system-ui, sans-serif",
  maxWidth: 900,
} as const;
const STATS = {
  display: "flex",
  gap: 32,
  fontSize: 26,
  color: OG_ACCENT,
  fontFamily: "system-ui, sans-serif",
  fontWeight: 600,
} as const;

type SiteStats = { total_channels: number; total_subscribers: number; total_views: number };

function sectionCard(
  eyebrow: string,
  title: string,
  subtitle: string,
  opts: { titleSize?: number; titleMaxWidth?: number; extra?: ReactElement } = {},
) {
  const { titleSize = 88, titleMaxWidth, extra } = opts;
  return (
    <OgFrame eyebrow={`Latter-day Stats · ${eyebrow}`}>
      <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
        <div style={{ ...TITLE, fontSize: titleSize, ...(titleMaxWidth ? { maxWidth: titleMaxWidth } : {}) }}>{title}</div>
        <div style={SUBTITLE}>{subtitle}</div>
        {extra}
      </div>
    </OgFrame>
  );
}

function homeCard(stats: SiteStats | null) {
  return (
    <OgFrame eyebrow="Latter-day Stats">
      <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
        <div style={{ ...TITLE, fontSize: 64, lineHeight: 1.1, maxWidth: 1000 }}>
          Statistics, research, and creator data on the Latter-day Saint community.
        </div>
        {stats && (
          <div style={STATS}>
            <span>{fmtNumber(stats.total_channels)} channels</span>
            <span>·</span>
            <span>{fmtCompact(stats.total_subscribers)} subscribers</span>
            <span>·</span>
            <span>{fmtCompact(stats.total_views)} views</span>
          </div>
        )}
      </div>
    </OgFrame>
  );
}

function sectionCards(stats: SiteStats | null): Record<string, ReactElement> {
  return {
    home: homeCard(stats),
    about: sectionCard(
      "About",
      "A public hub for Latter-day Saint statistics & research",
      "Who runs the site, how it's funded, and what it's built to do.",
      { titleSize: 72, titleMaxWidth: 1000 },
    ),
    channels: sectionCard(
      "Channels",
      "Channel directory",
      "Latter-day Saint YouTube creators, tracked and refreshed regularly.",
      {
        extra: stats ? (
        <div style={STATS}>
          <span>{fmtNumber(stats.total_channels)} channels</span>
          <span>·</span>
          <span>{fmtCompact(stats.total_subscribers)} subscribers</span>
        </div>
        ) : undefined,
      },
    ),
    contact: sectionCard(
      "Contact",
      "Get in touch",
      "Report an error, suggest a channel or study, or send a note.",
    ),
    donate: sectionCard(
      "Donate",
      "Help keep the site running",
      "Free, independent, and ad-free — donations go toward hosting.",
    ),
    methodology: sectionCard(
      "Methodology",
      "Methodology",
      "How channels are selected, statistics collected, and academic studies curated.",
    ),
    studies: sectionCard(
      "Research",
      "Research library",
      "Curated academic studies relating to the Latter-day Saint community.",
    ),
  };
}

type ChannelRow = {
  slug: string;
  name: string | null;
  thumbnail_url: string | null;
  subscribers: number | null;
  total_views: number | null;
  stats_captured_at: string | null;
};

function channelCard(c: ChannelRow, thumbnail: string | null) {
  // Same rule as rowToChannelWithStats in src/lib/data.ts: no stats until the
  // first capture.
  const hasStats = c.stats_captured_at !== null && c.subscribers !== null;
  const subs = hasStats && c.subscribers ? `${fmtCompact(c.subscribers)} subscribers` : null;
  const views = hasStats && c.total_views ? `${fmtCompact(c.total_views)} total views` : null;
  const stat = [subs, views].filter(Boolean).join("  ·  ");
  return (
    <OgFrame eyebrow="Latter-day Stats · Channel">
      <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
          {thumbnail && (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={thumbnail} width={80} height={80} style={{ borderRadius: 4, objectFit: "cover" }} alt="" />
          )}
          <div style={{ ...TITLE, fontSize: 72 }}>{c.name ?? "Channel"}</div>
        </div>
        {stat && <div style={{ fontSize: 28, color: OG_MUTED, fontFamily: "system-ui, sans-serif" }}>{stat}</div>}
      </div>
    </OgFrame>
  );
}

type StudyRow = { slug: string; title: string | null; authors: string[] | null; year: number | null };

function studyCard(s: StudyRow) {
  const title = s.title ?? "Research Study";
  const authorList = s.authors ?? [];
  const authors =
    authorList.length > 0 ? authorList.slice(0, 2).join(", ") + (authorList.length > 2 ? " et al." : "") : null;
  const meta = [authors, s.year ? String(s.year) : null].filter(Boolean).join("  ·  ");
  return (
    <OgFrame eyebrow="Latter-day Stats · Academic Study">
      <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
        <div style={{ ...TITLE, fontSize: title.length > 60 ? 52 : 64, lineHeight: 1.1 }}>
          {title.length > 110 ? title.slice(0, 108) + "…" : title}
        </div>
        {meta && <div style={{ fontSize: 26, color: OG_MUTED, fontFamily: "system-ui, sans-serif" }}>{meta}</div>}
      </div>
    </OgFrame>
  );
}

// Favicon: the filled beehive-and-bar-chart mark, transparent background.
// Geometry shared with src/components/beehive-stats-mark.tsx (the nav logo).
function iconMark() {
  const HONEY = "#d9a441"; // brand honey (dark-mode value — reads on any tab background)
  const INK = "#1a1a1a";
  return (
    <div style={{ width: "100%", height: "100%", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <svg width="30" height="30" viewBox="0 0 24 24">
        {BEEHIVE_BANDS.map((b, i) => (
          <rect key={i} x={b.x} y={b.y} width={b.w} height={b.h} rx={b.rx} fill={HONEY} />
        ))}
        {BEEHIVE_BARS.map((b, i) => (
          <rect key={i} x={b.x} y={BEEHIVE_BAR_BASELINE - b.h} width={BEEHIVE_BAR_WIDTH} height={b.h} rx={0.6} fill={INK} />
        ))}
      </svg>
    </div>
  );
}

// ---------------------------------------------------------------- helpers

async function render(element: ReactElement, file: string, size = OG_SIZE) {
  const res = new ImageResponse(element, size);
  const png = Buffer.from(await res.arrayBuffer());
  await mkdir(path.dirname(file), { recursive: true });
  await writeFile(file, png);
}

async function pool<T>(items: T[], fn: (item: T) => Promise<void>) {
  let next = 0;
  const workers = Array.from({ length: Math.min(CONCURRENCY, items.length) }, async () => {
    while (next < items.length) await fn(items[next++]);
  });
  await Promise.all(workers);
}

// Fetch the avatar ourselves (with a timeout) so a dead YouTube URL drops the
// avatar instead of failing the card.
async function thumbnailDataUrl(url: string | null): Promise<string | null> {
  if (!url) return null;
  try {
    const res = await fetch(url, { signal: AbortSignal.timeout(10_000) });
    if (!res.ok) return null;
    const type = res.headers.get("content-type") ?? "image/jpeg";
    if (!type.startsWith("image/")) return null;
    return `data:${type};base64,${Buffer.from(await res.arrayBuffer()).toString("base64")}`;
  } catch {
    return null;
  }
}

async function selectAll<T>(sb: SupabaseClient, table: string, columns: string): Promise<T[]> {
  const rows: T[] = [];
  const PAGE = 1000;
  for (let from = 0; ; from += PAGE) {
    const { data, error } = await sb.from(table).select(columns).order("slug").range(from, from + PAGE - 1);
    if (error) throw error;
    rows.push(...((data ?? []) as T[]));
    if (!data || data.length < PAGE) return rows;
  }
}

// ---------------------------------------------------------------- main

async function main() {
  const started = Date.now();
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
  const sb = url && key ? createClient(url, key, { auth: { persistSession: false, autoRefreshToken: false } }) : null;
  if (!sb) console.warn("[og] WARNING: no Supabase env; writing section images only (no totals, no per-slug cards).");

  let stats: SiteStats | null = null;
  let channels: ChannelRow[] = [];
  let studies: StudyRow[] = [];
  if (sb) {
    try {
      const statsRes = await sb.from("site_stats").select("*").maybeSingle();
      if (statsRes.error) throw statsRes.error;
      stats = (statsRes.data as SiteStats) ?? null;
      channels = await selectAll<ChannelRow>(
        sb,
        "channel_full",
        "slug, name, thumbnail_url, subscribers, total_views, stats_captured_at",
      );
      studies = await selectAll<StudyRow>(sb, "studies", "slug, title, authors, year");
    } catch (err) {
      console.warn(`[og] WARNING: Supabase read failed (${err instanceof Error ? err.message : String(err)}); per-slug cards skipped.`);
    }
  }

  // Start clean so a deleted channel/study doesn't keep a stale card.
  await rm(OUT, { recursive: true, force: true });

  const sections = sectionCards(stats);
  for (const [name, element] of Object.entries(sections)) {
    await render(element, path.join(OUT, `${name}.png`));
  }
  await render(iconMark(), path.join(PUBLIC, "icon.png"), { width: 32, height: 32 });

  let failed = 0;
  const safeChannels = channels.filter((c) => c.slug && SAFE_SLUG.test(c.slug));
  await pool(safeChannels, async (c) => {
    try {
      await render(channelCard(c, await thumbnailDataUrl(c.thumbnail_url)), path.join(OUT, "channels", `${c.slug}.png`));
    } catch (err) {
      failed++;
      console.warn(`[og] channel ${c.slug}: ${err instanceof Error ? err.message : String(err)}`);
    }
  });
  const safeStudies = studies.filter((s) => s.slug && SAFE_SLUG.test(s.slug));
  await pool(safeStudies, async (s) => {
    try {
      await render(studyCard(s), path.join(OUT, "studies", `${s.slug}.png`));
    } catch (err) {
      failed++;
      console.warn(`[og] study ${s.slug}: ${err instanceof Error ? err.message : String(err)}`);
    }
  });

  const skipped = channels.length - safeChannels.length + studies.length - safeStudies.length;
  console.log(
    `[og] ${Object.keys(sections).length} section images, ${safeChannels.length} channel and ${safeStudies.length} study cards` +
      ` (${failed} failed, ${skipped} unsafe slugs skipped) in ${((Date.now() - started) / 1000).toFixed(1)}s`,
  );
}

main().catch((err) => {
  // Never fail the build over social images; the section fallbacks cover it.
  console.warn("[og] WARNING: image build failed:", err);
});

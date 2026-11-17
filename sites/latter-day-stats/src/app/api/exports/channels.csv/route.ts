import { NextRequest, NextResponse } from "next/server";
import { getChannelsWithLatest } from "@/lib/data";
import { toCsv } from "@/lib/csv";
import { fmtAvgViews } from "@/lib/format";
import type { ChannelWithStats } from "@/lib/types";

const UNKNOWN = "Unknown";

function normalizeFilterValue(value: string | null | undefined) {
  const normalized = value?.trim();
  return normalized ? normalized : UNKNOWN;
}

function channelTagsOf(channel: ChannelWithStats): string[] {
  return channel.channel_types?.length
    ? channel.channel_types
    : channel.channel_type
      ? [channel.channel_type]
      : [];
}

function getChannelFilterValue(
  channel: ChannelWithStats,
  key: "country" | "language",
) {
  if (key === "country")
    return normalizeFilterValue(channel.country_manual ?? channel.country);
  return normalizeFilterValue(channel.language_manual ?? channel.language);
}

function matchesType(channel: ChannelWithStats, selected: Set<string>): boolean {
  if (selected.size === 0) return true;
  const tags = channelTagsOf(channel);
  if (tags.length === 0) return selected.has(UNKNOWN);
  return tags.some((tag) => selected.has(tag));
}

function selectedValues(req: NextRequest, key: "type" | "country" | "language") {
  return new Set(
    req.nextUrl.searchParams
      .getAll(key)
      .map((value) => value.trim())
      .filter(Boolean),
  );
}

function youtubeUrl(channel: ChannelWithStats) {
  if (channel.handle) {
    return `https://www.youtube.com/${
      channel.handle.startsWith("@") ? channel.handle : `@${channel.handle}`
    }`;
  }
  return `https://www.youtube.com/channel/${channel.youtube_channel_id}`;
}

export async function GET(req: NextRequest) {
  const selections = {
    type: selectedValues(req, "type"),
    country: selectedValues(req, "country"),
    language: selectedValues(req, "language"),
  };

  const channels = (await getChannelsWithLatest({ includeInactive: true })).filter(
    (channel) =>
      matchesType(channel, selections.type) &&
      (selections.country.size === 0 ||
        selections.country.has(getChannelFilterValue(channel, "country"))) &&
      (selections.language.size === 0 ||
        selections.language.has(getChannelFilterValue(channel, "language"))),
  );

  const csv = toCsv(channels, [
    { header: "Name", value: (c) => c.name },
    { header: "Tags", value: (c) => channelTagsOf(c).join("|") },
    { header: "Country", value: (c) => c.country_manual ?? c.country ?? "" },
    { header: "Language", value: (c) => c.language_manual ?? c.language ?? "" },
    { header: "Subscribers", value: (c) => c.latest?.subscribers ?? "" },
    { header: "Total views", value: (c) => c.latest?.total_views ?? "" },
    { header: "Videos", value: (c) => c.latest?.video_count ?? "" },
    {
      header: "Avg views/video",
      value: (c) => fmtAvgViews(c.latest?.total_views, c.latest?.video_count),
    },
    { header: "Channel created", value: (c) => c.created_at_youtube ?? "" },
    { header: "YouTube URL", value: youtubeUrl },
  ]);

  return new NextResponse(`\uFEFF${csv}`, {
    headers: {
      "Content-Type": "text/csv; charset=utf-8",
      "Content-Disposition": 'attachment; filename="latter-day-stats-channels.csv"',
      "Cache-Control": "private, no-store",
    },
  });
}

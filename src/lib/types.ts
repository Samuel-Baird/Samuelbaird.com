// Display shape is the joined `channel_full` view: user-curated metadata from
// `channels` + YouTube-derived fields from `channel_youtube`. The split is by
// table, but consumers see one merged row.
export type Channel = {
  id: string;
  youtube_channel_id: string;
  slug: string;
  // YouTube-derived (from channel_youtube). `name` falls back to the channel
  // ID in the channel_full view when a refresh has not yet populated it.
  name: string;
  description: string | null;
  country: string | null;
  language: string | null;
  thumbnail_url: string | null;
  created_at_youtube: string | null;
  last_synced_at: string | null;
  last_sync_status: string | null;
  last_sync_error: string | null;
  // User-curated metadata.
  country_manual: string | null;
  language_manual: string | null;
  channel_type: string | null;
  state: string | null;
  city: string | null;
  owned_by: string | null;
  handle: string | null;
  lds_affiliation_source: string | null;
  facebook_url: string | null;
  instagram_url: string | null;
  tiktok_url: string | null;
  x_url: string | null;
  notes: string | null;
  featured: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type ChannelStats = {
  channel_id: string;
  captured_at: string;
  subscribers: number;
  total_views: number;
  video_count: number;
};

export type ChannelWithStats = Channel & {
  latest: ChannelStats | null;
};

export function effectiveCountry(channel: Pick<Channel, "country" | "country_manual">): string | null {
  return channel.country_manual ?? channel.country ?? null;
}

export function effectiveLanguage(channel: Pick<Channel, "language" | "language_manual">): string | null {
  return channel.language_manual ?? channel.language ?? null;
}

export type Study = {
  id: string;
  slug: string;
  title: string;
  authors: string[];
  year: number | null;
  source: string | null;
  abstract: string | null;
  tags: string[];
  pdf_path: string | null;
  external_url: string | null;
  featured: boolean;
  published_at: string | null;
  findings: string[];
  limitations: string | null;
  flagged_problematic: boolean;
  flag_reason: string | null;
  context_note: string | null;
  source_type: string | null;
  category: string | null;
  secondary_url: string | null;
  preview_image_path: string | null;
  preview_image_source: string | null;
  preview_image_caption: string | null;
  preview_image_is_ai: boolean;
  created_at: string;
  updated_at: string;
};

export type SiteStats = {
  total_channels: number;
  total_subscribers: number;
  total_views: number;
  total_videos: number;
  last_refresh: string | null;
};

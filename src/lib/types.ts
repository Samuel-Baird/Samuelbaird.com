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
  channel_types: string[];
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

// ============================================================================
// Apologetics Hub — private, apologist-gated. All reads/writes go through
// createSupabaseServiceClient() behind requireApologist(); RLS on these
// tables is deny-all (see supabase/migrations/0039_apologetics_hub.sql).
// ============================================================================

export type HubVideoStatusValue = "working_on_it" | "responded";

export type HubVideoState = "active" | "removed" | "private";

export type HubVideo = {
  id: string;
  channel_id: string;
  youtube_video_id: string;
  title: string;
  published_at: string;
  duration_seconds: number | null;
  thumbnail_url: string | null;
  summary: string;
  view_count: number;
  view_count_updated_at: string | null;
  expected_views: number | null;
  debunkability: number | null;
  priority_score: number | null;
  video_status: HubVideoState;
  analyzed_at: string | null;
  created_at: string;
  updated_at: string;
};

// Joined display shape used by the feed and detail pages.
export type HubVideoWithChannel = HubVideo & {
  channel_name: string;
  channel_slug: string;
};

export type HubClaimSource = {
  title: string;
  url: string;
  note: string;
};

export type HubClaim = {
  id: string;
  video_id: string;
  position: number;
  timestamp_seconds: number;
  excerpt: string;
  claim_summary: string;
  response: string;
  sources: HubClaimSource[];
  created_at: string;
  updated_at: string;
};

export type HubVideoStatus = {
  user_id: string;
  video_id: string;
  status: HubVideoStatusValue;
  response_url: string | null;
  created_at: string;
  updated_at: string;
};

// Joined display shape: a status row plus the creator's display name.
export type HubVideoStatusWithUser = HubVideoStatus & {
  full_name: string | null;
  email: string | null;
};

// Transcript is stored for (re)analysis only — never selected for rendering
// in the UI. Typed here for the ingest scripts, not for page components.
export type HubTranscript = {
  video_id: string;
  transcript: string;
  segments: { start: number; text: string }[] | null;
  source: "timedtext" | "yt-dlp" | "manual";
  fetched_at: string;
};
